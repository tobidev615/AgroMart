from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management import BaseCommand, call_command
from django.db import transaction
from django.utils import timezone

from userprofiles.models import UserProfile, UserType
from farmers.models import FarmerProfile, Produce, FarmerEarnings
from distributors.models import DistributorProfile
from deliveries.models import Delivery, DeliveryStatus
from subscriptions.models import SubscriptionPlan, Subscription, SubscriptionItem, BillingPeriod
from orders.models import Order, OrderItem, OrderStatus
from notifications.models import Notification
from business.models import (
    BusinessProfile,
    BusinessPricingTier,
    ContractOrder,
    ContractOrderItem,
    BusinessInvoice,
    ContractFrequency,
    InvoiceStatus,
)
from payments.models import Payment, PaymentStatus


FARMER_NAMES = [
    ("farmer_ada", "Ada Farms"),
    ("farmer_kofi", "Kofi Greens"),
]

CONSUMERS = [
    ("alice", "Alice"),
    ("bob", "Bob"),
]

BUSINESSES = [
    ("resto_one", "Farm To Table Ltd."),
]

DISTRIBUTORS = [
    ("distro_max", "Max Logistics"),
]

PRODUCE_CATALOG = [
    ("Tomatoes", "kg", Decimal("2.50")),
    ("Potatoes", "kg", Decimal("1.80")),
    ("Carrots", "kg", Decimal("2.20")),
    ("Spinach", "bunch", Decimal("1.20")),
]


class Command(BaseCommand):
    help = "Seed realistic demo data across the entire system (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="NOT IMPLEMENTED. Placeholder for future full reset.")

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding data..."))

        # Ensure subscription plans exist
        try:
            call_command("seed_plans")
        except Exception as exc:  # pragma: no cover - optional
            self.stdout.write(self.style.WARNING(f"seed_plans failed or missing: {exc}"))

        # Create core users and profiles
        staff_user = self._ensure_user("staff", "staff@example.com", is_staff=True)

        farmer_users = [self._ensure_user(username, f"{username}@example.com") for username, _ in FARMER_NAMES]
        consumer_users = [self._ensure_user(username, f"{username}@example.com") for username, _ in CONSUMERS]
        business_users = [self._ensure_user(username, f"{username}@example.com") for username, _ in BUSINESSES]
        distributor_users = [self._ensure_user(username, f"{username}@example.com") for username, _ in DISTRIBUTORS]

        # Assign roles and create related profiles
        for user, (_, display_name) in zip(farmer_users, FARMER_NAMES):
            self._ensure_role(user, UserType.FARMER)
            FarmerProfile.objects.get_or_create(
                user=user,
                defaults={
                    "name": display_name,
                    "location": random.choice(["North Valley", "East Ridge", "Green Plains"]),
                    "crops": "tomatoes,potatoes,carrots,spinach",
                    "estimated_harvest": random.choice(["2 weeks", "1 month", "this weekend"]),
                },
            )

        for user, (_, display_name) in zip(business_users, BUSINESSES):
            self._ensure_role(user, UserType.BUSINESS)
            BusinessProfile.objects.get_or_create(
                user=user,
                defaults={
                    "name": display_name,
                    "company": display_name,
                    "business_type": "RESTAURANT",
                    "city": "Lagos",
                    "country": "NG",
                    "credit_terms_days": 30,
                    "credit_limit": Decimal("5000.00"),
                },
            )

        for user, (_, display_name) in zip(distributor_users, DISTRIBUTORS):
            self._ensure_role(user, UserType.DISTRIBUTOR)
            DistributorProfile.objects.get_or_create(
                user=user,
                defaults={
                    "name": display_name,
                    "hub_location": random.choice(["Main Hub", "West Hub"]),
                    "vehicle_info": random.choice(["Van", "Bike", "Truck"]),
                },
            )

        for user, _ in zip(consumer_users, CONSUMERS):
            self._ensure_role(user, UserType.CONSUMER)
            # ConsumerProfile, Analytics, Preference are created by signals; ensure profile row exists
            # by touching the related name if present; otherwise the signal handles post user save.
            getattr(user, "profile", None)

        # Create produce for each farmer
        for farmer_user, (username, _) in zip(farmer_users, FARMER_NAMES):
            farmer_profile = FarmerProfile.objects.get(user=farmer_user)
            for name, unit, price in PRODUCE_CATALOG:
                Produce.objects.get_or_create(
                    farmer=farmer_profile,
                    name=name,
                    defaults={
                        "variety": random.choice(["Heirloom", "Organic", "Standard"]),
                        "description": f"Fresh {name.lower()} from {farmer_profile.name}",
                        "quantity_available": random.randint(50, 200),
                        "unit": unit,
                        "price_per_unit": price,
                        "available": True,
                    },
                )

        # Business pricing tiers (global tiers)
        for produce in Produce.objects.all()[:3]:
            for min_qty, unit_multiplier in [(10, 1), (50, 1)]:
                BusinessPricingTier.objects.get_or_create(
                    business=None,
                    produce=produce,
                    min_quantity=min_qty,
                    unit=produce.unit,
                    defaults={"unit_price": (produce.price_per_unit * Decimal("0.9"))},
                )

        # Create sample orders for consumers and business
        all_buyers: list[User] = consumer_users + business_users
        distributor_profile = None
        if distributor_users:
            distributor_profile = DistributorProfile.objects.filter(user=distributor_users[0]).first()

        produce_list = list(Produce.objects.all())
        random.shuffle(produce_list)
        now = timezone.now()

        created_orders: list[Order] = []
        for buyer in all_buyers:
            for i in range(2):
                order, _ = Order.objects.get_or_create(
                    user=buyer,
                    created_at__date=date.today(),
                    defaults={"status": OrderStatus.PENDING, "total_amount": Decimal("0.00")},
                )
                # If order already existed due to idempotency filter being too loose, skip adding items twice
                if order.items.exists():
                    created_orders.append(order)
                    continue

                # Add 2-3 items
                items = random.sample(produce_list, k=min(3, len(produce_list)))
                total = Decimal("0.00")
                for prod in items:
                    quantity = random.randint(2, 7)
                    subtotal = prod.price_per_unit * quantity
                    OrderItem.objects.create(
                        order=order,
                        produce=prod,
                        product_name=prod.name,
                        unit=prod.unit,
                        price_per_unit=prod.price_per_unit,
                        quantity=quantity,
                        subtotal=subtotal,
                    )
                    total += subtotal
                    # decrement stock, ensure non-negative
                    if prod.quantity_available >= quantity:
                        prod.quantity_available -= quantity
                    prod.total_sold += quantity
                    prod.total_revenue += subtotal
                    prod.save(update_fields=["quantity_available", "total_sold", "total_revenue"]) 

                    # create farmer earnings (PENDING initially)
                    FarmerEarnings.objects.get_or_create(
                        farmer=prod.farmer,
                        order=order,
                        produce=prod,
                        quantity=quantity,
                        unit_price=prod.price_per_unit,
                        total_amount=subtotal,
                        defaults={"status": "CONFIRMED"},
                    )

                order.total_amount = total
                # Randomize order status
                order.status = random.choice(
                    [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.DELIVERED]
                )
                order.save(update_fields=["total_amount", "status"]) 
                created_orders.append(order)

                # Update farmer profile aggregates when confirmed/delivered
                if order.status in (OrderStatus.CONFIRMED, OrderStatus.DELIVERED):
                    for item in order.items.all().select_related("produce__farmer"):
                        farmer_profile = item.produce.farmer
                        farmer_profile.total_earnings += item.subtotal
                        farmer_profile.total_orders += 1
                        farmer_profile.save(update_fields=["total_earnings", "total_orders"]) 

                # Create delivery
                delivery, _ = Delivery.objects.get_or_create(
                    order=order,
                    defaults={
                        "status": DeliveryStatus.SCHEDULED,
                        "scheduled_date": now + timedelta(days=random.randint(0, 5)),
                        "notes": "Auto-seeded delivery",
                    },
                )
                # Assign distributor and optionally mark delivered
                if distributor_profile and not delivery.distributor:
                    delivery.distributor = distributor_profile
                if order.status == OrderStatus.DELIVERED:
                    delivery.status = DeliveryStatus.DELIVERED
                    delivery.delivered_at = now
                delivery.save()

                # Payment record
                Payment.objects.get_or_create(
                    user=buyer,
                    order=order,
                    defaults={
                        "amount": order.total_amount,
                        "status": PaymentStatus.SUCCEEDED if order.status != OrderStatus.PENDING else PaymentStatus.PENDING,
                    },
                )

                # Notifications
                Notification.objects.get_or_create(
                    user=buyer,
                    title="Order Created",
                    message=f"Your order #{order.id} has been created with {order.items.count()} items.",
                )

        # Subscriptions for consumers
        weekly_plan = SubscriptionPlan.objects.filter(period=BillingPeriod.WEEKLY).first()
        if weekly_plan:
            for user in consumer_users:
                Subscription.objects.get_or_create(
                    user=user,
                    plan=weekly_plan,
                    defaults={
                        "start_date": date.today() - timedelta(days=7),
                        "next_delivery_date": date.today() + timedelta(days=7),
                        "is_active": True,
                    },
                )
                sub = Subscription.objects.get(user=user, plan=weekly_plan)
                # Ensure some items exist
                for prod in Produce.objects.all()[:2]:
                    SubscriptionItem.objects.get_or_create(
                        subscription=sub,
                        produce=prod,
                        defaults={"quantity": random.randint(1, 3)},
                    )

        # Business contracts and invoices
        if business_users:
            biz_user = business_users[0]
            business_profile = BusinessProfile.objects.filter(user=biz_user).first()
            if business_profile:
                contract, _ = ContractOrder.objects.get_or_create(
                    business=business_profile,
                    name="Weekly Veg Box",
                    defaults={
                        "frequency": ContractFrequency.WEEKLY,
                        "next_delivery_date": date.today() + timedelta(days=7),
                        "priority": True,
                        "notes": "Auto-seeded contract",
                    },
                )
                for prod in Produce.objects.all()[:2]:
                    ContractOrderItem.objects.get_or_create(
                        contract=contract,
                        produce=prod,
                        defaults={
                            "quantity": 20,
                            "unit": prod.unit,
                            "agreed_unit_price": prod.price_per_unit * Decimal("0.92"),
                        },
                    )

                # Issue invoices for delivered business orders
                for order in Order.objects.filter(user=biz_user):
                    due_date = date.today() + timedelta(days=business_profile.credit_terms_days or 0)
                    BusinessInvoice.objects.get_or_create(
                        business=business_profile,
                        order=order,
                        defaults={
                            "payment_terms_days": business_profile.credit_terms_days or 0,
                            "due_date": due_date,
                            "status": InvoiceStatus.ISSUED,
                            "total_amount": order.total_amount,
                        },
                    )

        self.stdout.write(self.style.SUCCESS("Seeding complete."))

    def _ensure_user(self, username: str, email: str, is_staff: bool = False) -> User:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "is_staff": is_staff},
        )
        if created:
            user.set_password("password123")
            user.save()
        # Ensure UserProfile exists
        UserProfile.objects.get_or_create(user=user)
        return user

    def _ensure_role(self, user: User, role: str) -> None:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if profile.role != role:
            profile.role = role
            profile.save(update_fields=["role"]) 



