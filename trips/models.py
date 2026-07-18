from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import Driver

class Trip(models.Model):
    TRIP_TYPE_CHOICES = [
        ('taxi', 'Taxi'),
        ('local', 'Local'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    # Basic fields
    trip_code = models.CharField(max_length=12, unique=True, editable=False)
    trip_type = models.CharField(max_length=10, choices=TRIP_TYPE_CHOICES, default='taxi')
    date = models.DateField()
    day = models.CharField(max_length=20)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    
    # Location fields
    start_place = models.CharField(max_length=200)
    pickup_place = models.CharField(max_length=200)
    drop_place = models.CharField(max_length=200)
    end_place = models.CharField(max_length=200, blank=True, null=True)
    
    # KM fields
    start_km = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    end_km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])
    total_km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Time fields
    time_in = models.TimeField()
    time_out = models.TimeField(blank=True, null=True)
    total_time = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Duration in hours")
    
    # Common financial fields
    cng = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    petrol = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    red_taxi_income = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    advance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    advance_received_today = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Local trip specific fields
    waiting_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    inter_state_permit = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    luggage_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    pet_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    hill_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    toll_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    driver_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    
    # Calculated fields
    net_red_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    previous_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    main_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_expense = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_advance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    dr_adv = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    salary_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'trips'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['trip_code']),
            models.Index(fields=['driver']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.trip_code} - {self.driver.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        self.calculate_fields()
        super().save(*args, **kwargs)
    
    def calculate_fields(self):
        """Calculate all derived fields based on Excel formulas"""
        # TOTAL KM = ENDING KM - STARTING KM
        if self.end_km is not None and self.start_km is not None:
            self.total_km = self.end_km - self.start_km
        
        # TOTAL TIME = MOD(TIME OUT - TIME IN, 1)
        if self.time_out and self.time_in:
            from datetime import datetime, timedelta
            time_in_seconds = self.time_in.hour * 3600 + self.time_in.minute * 60 + self.time_in.second
            time_out_seconds = self.time_out.hour * 3600 + self.time_out.minute * 60 + self.time_out.second
            diff_seconds = (time_out_seconds - time_in_seconds) % 86400  # 24 hours in seconds
            self.total_time = round(diff_seconds / 3600, 2)  # Convert to hours
        
        # NET RED INCOME = RED TAXI INCOME - COMMISSION
        self.net_red_income = self.red_taxi_income - self.commission
        
        # SALARY = TOTAL TIME * SALARY_PER_HOUR * 24
        if self.total_time is not None:
            self.salary = round(self.total_time * self.salary_per_hour * 24, 2)
        
        # MAIN SALARY = SALARY + PREVIOUS SALARY - DR_ADV
        if self.salary is not None:
            self.main_salary = self.salary + self.previous_salary - self.dr_adv
        
        # TOTAL EXPENSE = CNG + PETROL + SALARY
        if self.salary is not None:
            self.total_expense = self.cng + self.petrol + self.salary
        
        # BALANCE AMOUNT = RED TAXI INCOME - TOTAL EXPENSE
        if self.total_expense is not None:
            self.balance_amount = self.red_taxi_income - self.total_expense
        
        # BONUS = TOTAL TIME * 24 * 3
        if self.total_time is not None:
            self.bonus = round(self.total_time * 24 * 3, 2)
        
        # TOTAL ADVANCE = ADVANCE - ADVANCE_RECEIVED_TODAY
        self.total_advance = self.advance - self.advance_received_today

class SalaryRecord(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='salary_records')
    period_start = models.DateField()
    period_end = models.DateField()
    salary_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    advances = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    paid_on = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'salary_records'
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.driver.user.get_full_name()} - {self.period_start} to {self.period_end}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    table_name = models.CharField(max_length=50)
    record_id = models.PositiveIntegerField()
    changes = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} on {self.table_name}:{self.record_id}"
