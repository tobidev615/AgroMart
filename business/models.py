from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class BusinessType(models.TextChoices):
    RESTAURANT = "RESTAURANT", "Restaurant"
    CATERER = "CATERER", "Caterer"
    HOTEL = "HOTEL", "Hotel"
    SUPERMARKET = "SUPERMARKET", "Supermarket"
    LARGE_BUYER = "LARGE_BUYER", "Large Buyer"


class BusinessProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="business_profile")
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=30, choices=BusinessType.choices, default=BusinessType.LARGE_BUYER)
    tax_id = models.CharField(max_length=100, blank=True)

    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # Support and account manager
    account_manager_name = models.CharField(max_length=120, blank=True)
    account_manager_email = models.EmailField(blank=True)
    account_manager_phone = models.CharField(max_length=40, blank=True)
    support_whatsapp = models.CharField(max_length=40, blank=True)
    support_phone = models.CharField(max_length=40, blank=True)

    # Credit terms
    credit_terms_days = models.PositiveIntegerField(default=0, help_text="0 = prepaid, 7/30 = net terms")
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    # Packaging/branding
    branding_enabled = models.BooleanField(default=False)
    brand_name = models.CharField(max_length=255, blank=True)
    packaging_preferences = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["company"]),
            models.Index(fields=["business_type"]),
        ]

    def __str__(self) -> str:
        return self.company or self.name or self.user.username


class BusinessPricingTier(models.Model):
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="pricing_tiers", null=True, blank=True, help_text="Null = global tier")
    produce = models.ForeignKey('farmers.Produce', on_delete=models.CASCADE, related_name="business_pricing")
    min_quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50, help_text="e.g., kg, crate, sack")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("business", "produce", "min_quantity", "unit")
        indexes = [
            models.Index(fields=["produce", "min_quantity"]),
            models.Index(fields=["business"]),
        ]

    def __str__(self) -> str:
        return f"Tier: {self.produce} ≥{self.min_quantity}{self.unit} @ {self.unit_price}"


class ContractFrequency(models.TextChoices):
    WEEKLY = "WEEKLY", "Weekly"
    BIWEEKLY = "BIWEEKLY", "Bi-weekly"
    MONTHLY = "MONTHLY", "Monthly"


class ContractOrder(models.Model):
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="contract_orders")
    name = models.CharField(max_length=200, help_text="Internal name, e.g. 'Weekly tomatoes'")
    frequency = models.CharField(max_length=20, choices=ContractFrequency.choices)
    next_delivery_date = models.DateField()
    priority = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.business.company or self.business.name} - {self.name}"


class ContractOrderItem(models.Model):
    contract = models.ForeignKey(ContractOrder, on_delete=models.CASCADE, related_name="items")
    produce = models.ForeignKey('farmers.Produce', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)
    agreed_unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.quantity}{self.unit} {self.produce}"


class InvoiceStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    ISSUED = "ISSUED", "Issued"
    PAID = "PAID", "Paid"
    OVERDUE = "OVERDUE", "Overdue"


class BusinessInvoice(models.Model):
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="invoices")
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name="business_invoice")
    payment_terms_days = models.PositiveIntegerField(default=0)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=InvoiceStatus.choices, default=InvoiceStatus.DRAFT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    pdf_path = models.CharField(max_length=512, blank=True, help_text="Path to generated PDF invoice")

    class Meta:
        indexes = [
            models.Index(fields=["business"]),
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        return f"Invoice #{self.id} for Order #{self.order_id}"
