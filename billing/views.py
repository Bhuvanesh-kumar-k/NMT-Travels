from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from .models import Bill
from .serializers import BillSerializer
from trips.models import Trip

class BillListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BillSerializer
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Bill.objects.all()
        return Bill.objects.filter(trip__driver__user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save()

class BillDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BillSerializer
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Bill.objects.all()
        return Bill.objects.filter(trip__driver__user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_bill_pdf(request, trip_id):
    """Generate PDF bill for a trip"""
    try:
        trip = Trip.objects.get(id=trip_id)
        
        # Check permissions
        if request.user.role != 'admin' and trip.driver.user != request.user:
            return Response({'error': 'Permission denied'}, status=403)
        
        # Create or get bill
        bill, created = Bill.objects.get_or_create(trip=trip)
        
        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f"bill_{trip.trip_code}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        doc = SimpleDocTemplate(response, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e3a8a'),
            spaceAfter=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6
        )
        
        # Company Header
        elements.append(Paragraph("NMT TRAVELS", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Company Details
        company_details = """
        <para alignment=center>
        <b>Call Taxi Management System</b><br/>
        123 Main Street, City<br/>
        Phone: +91 98765 43210<br/>
        Email: info@nmttravels.com
        </para>
        """
        elements.append(Paragraph(company_details, normal_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Bill Title
        elements.append(Paragraph("TAXI BILL / INVOICE", header_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Bill Info
        bill_info = [
            ['Bill Code:', bill.bill_code],
            ['Trip Code:', trip.trip_code],
            ['Date:', str(trip.date)],
            ['Day:', trip.day],
            ['Generated:', str(bill.generated_at.strftime('%Y-%m-%d %H:%M'))],
        ]
        
        bill_table = Table(bill_info, colWidths=[2*inch, 3*inch])
        bill_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(bill_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Driver Info
        elements.append(Paragraph("DRIVER INFORMATION", header_style))
        driver_info = [
            ['Driver Name:', trip.driver.user.get_full_name()],
            ['License No:', trip.driver.licence_no],
            ['Phone:', trip.driver.phone],
        ]
        
        driver_table = Table(driver_info, colWidths=[2*inch, 3*inch])
        driver_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(driver_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Trip Details
        elements.append(Paragraph("TRIP DETAILS", header_style))
        trip_details = [
            ['Starting Place:', trip.start_place],
            ['Pickup Place:', trip.pickup_place],
            ['Dropping Place:', trip.drop_place],
            ['Ending Place:', trip.end_place or '-'],
            ['Starting KM:', str(trip.start_km)],
            ['Ending KM:', str(trip.end_km) if trip.end_km else '-'],
            ['Total KM:', str(trip.total_km) if trip.total_km else '-'],
            ['Time In:', str(trip.time_in)],
            ['Time Out:', str(trip.time_out) if trip.time_out else '-'],
            ['Total Time:', f"{trip.total_time} hrs" if trip.total_time else '-'],
        ]
        
        trip_table = Table(trip_details, colWidths=[2*inch, 3*inch])
        trip_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(trip_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Fare Breakdown
        elements.append(Paragraph("FARE BREAKDOWN", header_style))
        
        if trip.trip_type == 'local':
            fare_data = [
                ['Description', 'Amount'],
                ['Waiting Charge', f"₹{trip.waiting_charge or 0}"],
                ['Inter State Permit', f"₹{trip.inter_state_permit or 0}"],
                ['Luggage Charges', f"₹{trip.luggage_charges or 0}"],
                ['Pet Charges', f"₹{trip.pet_charges or 0}"],
                ['Hill Charges', f"₹{trip.hill_charges or 0}"],
                ['Toll Charges', f"₹{trip.toll_charges or 0}"],
                ['Base Fare', f"₹{trip.base_fare or 0}"],
                ['Driver Allowance', f"₹{trip.driver_allowance or 0}"],
                ['', ''],
                ['TOTAL', f"₹{bill.total_amount}"],
            ]
        else:
            fare_data = [
                ['Description', 'Amount'],
                ['CNG', f"₹{trip.cng}"],
                ['Petrol', f"₹{trip.petrol}"],
                ['Red Taxi Income', f"₹{trip.red_taxi_income}"],
                ['Commission', f"₹{trip.commission}"],
                ['', ''],
                ['NET INCOME', f"₹{trip.net_red_income}"],
            ]
        
        fare_table = Table(fare_data, colWidths=[3*inch, 2*inch])
        fare_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(fare_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Signature Section
        signature_data = [
            ['', '', ''],
            ['__________________', '', '__________________'],
            ['Driver Signature', '', 'Admin Signature'],
        ]
        
        signature_table = Table(signature_data, colWidths=[2*inch, 2*inch, 2*inch])
        signature_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elements.append(signature_table)
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer = """
        <para alignment=center>
        <font size=8 color=gray>
        Thank you for choosing NMT Travels!<br/>
        This is a computer-generated bill. No signature required.
        </font>
        </para>
        """
        elements.append(Paragraph(footer, normal_style))
        
        # Build PDF
        doc.build(elements)
        
        return response
        
    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
