from django.test import TestCase
from django.utils import timezone
from datetime import time, date, timedelta
from decimal import Decimal
from trips.models import Trip, SalaryRecord, AuditLog
from accounts.models import User, Driver

class TripCalculationTests(TestCase):
    """Test trip calculation formulas"""
    
    def setUp(self):
        # Create test user and driver
        self.user = User.objects.create_user(
            username='testdriver',
            password='testpass123',
            role='driver',
            first_name='Test',
            last_name='Driver'
        )
        self.driver = Driver.objects.create(
            user=self.user,
            licence_no='TEST123',
            phone='9876543210',
            address='Test Address',
            bank_account='1234567890',
            ifsc='ABCD0123456'
        )
    
    def test_total_km_calculation(self):
        """Test TOTAL KM = ENDING KM - STARTING KM"""
        trip = Trip.objects.create(
            trip_code='202610000001',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000.50'),
            end_km=Decimal('1500.75'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            salary_per_hour=Decimal('10')
        )
        
        self.assertEqual(trip.total_km, Decimal('500.25'))
    
    def test_total_time_calculation(self):
        """Test TOTAL TIME = MOD(TIME OUT - TIME IN, 1)"""
        trip = Trip.objects.create(
            trip_code='202610000002',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            salary_per_hour=Decimal('10')
        )
        
        # 8 hours = 8.00
        self.assertEqual(trip.total_time, Decimal('8.00'))
    
    def test_net_red_income_calculation(self):
        """Test NET RED INCOME = RED TAXI INCOME - COMMISSION"""
        trip = Trip.objects.create(
            trip_code='202610000003',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            salary_per_hour=Decimal('10')
        )
        
        self.assertEqual(trip.net_red_income, Decimal('4500'))
    
    def test_salary_calculation(self):
        """Test SALARY = TOTAL TIME * SALARY_PER_HOUR * 24"""
        trip = Trip.objects.create(
            trip_code='202610000004',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            salary_per_hour=Decimal('10')
        )
        
        # 8 * 10 * 24 = 1920
        self.assertEqual(trip.salary, Decimal('1920.00'))
    
    def test_main_salary_calculation(self):
        """Test MAIN SALARY = SALARY + PREVIOUS SALARY - DR_ADV"""
        trip = Trip.objects.create(
            trip_code='202610000005',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            previous_salary=Decimal('500'),
            dr_adv=Decimal('200'),
            salary_per_hour=Decimal('10')
        )
        
        # 1920 + 500 - 200 = 2220
        self.assertEqual(trip.main_salary, Decimal('2220.00'))
    
    def test_total_expense_calculation(self):
        """Test TOTAL EXPENSE = CNG + PETROL + SALARY"""
        trip = Trip.objects.create(
            trip_code='202610000006',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            salary_per_hour=Decimal('10')
        )
        
        # 500 + 1000 + 1920 = 3420
        self.assertEqual(trip.total_expense, Decimal('3420.00'))
    
    def test_balance_amount_calculation(self):
        """Test BALANCE AMOUNT = RED TAXI INCOME - TOTAL EXPENSE"""
        trip = Trip.objects.create(
            trip_code='202610000007',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            salary_per_hour=Decimal('10')
        )
        
        # 5000 - 3420 = 1580
        self.assertEqual(trip.balance_amount, Decimal('1580.00'))
    
    def test_bonus_calculation(self):
        """Test BONUS = TOTAL TIME * 24 * 3"""
        trip = Trip.objects.create(
            trip_code='202610000008',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            salary_per_hour=Decimal('10')
        )
        
        # 8 * 24 * 3 = 576
        self.assertEqual(trip.bonus, Decimal('576.00'))
    
    def test_total_advance_calculation(self):
        """Test TOTAL ADVANCE = ADVANCE - ADVANCE_RECEIVED_TODAY"""
        trip = Trip.objects.create(
            trip_code='202610000009',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            cng=Decimal('500'),
            petrol=Decimal('1000'),
            red_taxi_income=Decimal('5000'),
            commission=Decimal('500'),
            advance=Decimal('1000'),
            advance_received_today=Decimal('300'),
            salary_per_hour=Decimal('10')
        )
        
        # 1000 - 300 = 700
        self.assertEqual(trip.total_advance, Decimal('700'))

class LocalTripCalculationTests(TestCase):
    """Test local trip specific calculations"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testdriver',
            password='testpass123',
            role='driver',
            first_name='Test',
            last_name='Driver'
        )
        self.driver = Driver.objects.create(
            user=self.user,
            licence_no='TEST123',
            phone='9876543210',
            address='Test Address',
            bank_account='1234567890',
            ifsc='ABCD0123456'
        )
    
    def test_local_trip_fields(self):
        """Test local trip specific fields are saved correctly"""
        trip = Trip.objects.create(
            trip_code='202610000010',
            trip_type='local',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='T Nagar',
            start_km=Decimal('1000'),
            end_km=Decimal('1050'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            waiting_charge=Decimal('100'),
            inter_state_permit=Decimal('50'),
            luggage_charges=Decimal('30'),
            pet_charges=Decimal('20'),
            hill_charges=Decimal('40'),
            toll_charges=Decimal('60'),
            base_fare=Decimal('200'),
            driver_allowance=Decimal('150'),
            salary_per_hour=Decimal('10')
        )
        
        self.assertEqual(trip.waiting_charge, Decimal('100'))
        self.assertEqual(trip.inter_state_permit, Decimal('50'))
        self.assertEqual(trip.luggage_charges, Decimal('30'))
        self.assertEqual(trip.pet_charges, Decimal('20'))
        self.assertEqual(trip.hill_charges, Decimal('40'))
        self.assertEqual(trip.toll_charges, Decimal('60'))
        self.assertEqual(trip.base_fare, Decimal('200'))
        self.assertEqual(trip.driver_allowance, Decimal('150'))

class TripStatusTests(TestCase):
    """Test trip status transitions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testdriver',
            password='testpass123',
            role='driver',
            first_name='Test',
            last_name='Driver'
        )
        self.driver = Driver.objects.create(
            user=self.user,
            licence_no='TEST123',
            phone='9876543210',
            address='Test Address',
            bank_account='1234567890',
            ifsc='ABCD0123456'
        )
    
    def test_trip_draft_status(self):
        """Test trip can be created with draft status"""
        trip = Trip.objects.create(
            trip_code='202610000011',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            time_in=time(8, 0),
            status='draft',
            salary_per_hour=Decimal('10')
        )
        
        self.assertEqual(trip.status, 'draft')
    
    def test_trip_completed_status(self):
        """Test trip can be completed"""
        trip = Trip.objects.create(
            trip_code='202610000012',
            trip_type='taxi',
            date=date.today(),
            day='Monday',
            driver=self.driver,
            start_place='Chennai',
            pickup_place='Chennai Central',
            drop_place='Bangalore',
            start_km=Decimal('1000'),
            end_km=Decimal('1500'),
            time_in=time(8, 0),
            time_out=time(16, 0),
            status='completed',
            salary_per_hour=Decimal('10')
        )
        
        self.assertEqual(trip.status, 'completed')
        self.assertIsNotNone(trip.total_km)
        self.assertIsNotNone(trip.total_time)
