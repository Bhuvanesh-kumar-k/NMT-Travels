from django.db import models
from trips.models import Trip

class Bill(models.Model):
    trip = models.OneToOneField(Trip, on_delete=models.CASCADE, related_name='bill')
    bill_code = models.CharField(max_length=20, unique=True, editable=False)
    generated_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='bills/', blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_emailed = models.BooleanField(default=False)
    emailed_to = models.EmailField(blank=True, null=True)
    emailed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'bills'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.bill_code} - {self.trip.trip_code}"
    
    def save(self, *args, **kwargs):
        if not self.bill_code:
            self.bill_code = self.generate_bill_code()
        self.calculate_total()
        super().save(*args, **kwargs)
    
    def generate_bill_code(self):
        """Generate unique bill code"""
        from datetime import datetime
        year = datetime.now().year
        last_bill = Bill.objects.filter(bill_code__startswith=f'BILL{year}').order_by('-bill_code').first()
        if last_bill:
            last_seq = int(last_bill.bill_code[-8:])
            new_seq = last_seq + 1
        else:
            new_seq = 1
        return f'BILL{year}{new_seq:08d}'
    
    def calculate_total(self):
        """Calculate total amount for the bill"""
        if self.trip.trip_type == 'local':
            # TOTAL = WAITING CHARGE + INTER STATE PERMIT + LUGGAGE CHARGES + PET CHARGES + HILL CHARGES + TOLL CHARGES + DRIVER ALLOWANCE
            total = (
                (self.trip.waiting_charge or 0) +
                (self.trip.inter_state_permit or 0) +
                (self.trip.luggage_charges or 0) +
                (self.trip.pet_charges or 0) +
                (self.trip.hill_charges or 0) +
                (self.trip.toll_charges or 0) +
                (self.trip.driver_allowance or 0)
            )
            self.total_amount = total
        else:
            # For taxi trips, total is based on red taxi income
            self.total_amount = self.trip.red_taxi_income
