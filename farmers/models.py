from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from decimal import Decimal


class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="farmer_profile")
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=255, blank=True)
    crops = models.TextField(blank=True, help_text="Comma-separated list of crops")
    estimated_harvest = models.CharField(max_length=200, blank=True)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_orders = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name or self.user.username
    
    def update_earnings(self, amount: Decimal) -> None:
        """Update total earnings when order is confirmed."""
        self.total_earnings += amount
        self.total_orders += 1
        self.save(update_fields=['total_earnings', 'total_orders'])


class FarmCluster(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    members = models.ManyToManyField(User, related_name="farm_clusters", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Produce(models.Model):
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name="produce")
    
    class ProduceName(models.TextChoices):
        TOMATOES = "TOMATOES", "Tomatoes"
        YAM = "YAM", "Yam"
        TATASHE = "TATASHE", "Tatashe"
        BELL_PEPPER = "BELL_PEPPER", "Bell pepper"
        CAYENNE_PEPPER = "CAYENNE_PEPPER", "Cayenne pepper (Sombo & Bawa)"
        SCOTCH_BONNET = "SCOTCH_BONNET", "Scotch bonnet pepper (Ata rodo)"
        MAIZE = "MAIZE", "Maize (Corn)"
    
    class Unit(models.TextChoices):
        KG = "KG", "KG"
        CRATES = "CRATES", "Crates"
        BUNCHES = "BUNCHES", "Bunches"
        TUBERS = "TUBERS", "Tubers"
        SACS = "SACS", "Sacs"
    
    name = models.CharField(max_length=255, choices=ProduceName.choices)
    variety = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='produce/', blank=True, null=True)
    quantity_available = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=50, choices=Unit.choices)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    available = models.BooleanField(default=True)
    total_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['available']),
            models.Index(fields=['created_at']),
            models.Index(fields=['farmer', 'available']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['farmer', 'name', 'variety', 'unit'],
                name='uniq_farmer_produce_variant_unit',
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.variety}) by {self.farmer.name}"
    
    def update_sales_stats(self, quantity: int, revenue: Decimal) -> None:
        """Update sales statistics when order is confirmed."""
        self.total_sold += quantity
        self.total_revenue += revenue
        self.save(update_fields=['total_sold', 'total_revenue'])


class FarmerEarnings(models.Model):
    """Track individual earnings transactions."""
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name="earnings")
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name="farmer_earnings")
    produce = models.ForeignKey(Produce, on_delete=models.CASCADE, related_name="earnings")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PAID', 'Paid'),
    ], default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['farmer', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.farmer.name} - {self.produce.name} - ${self.total_amount}"

# Create your models here.
