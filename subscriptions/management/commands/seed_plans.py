from django.core.management.base import BaseCommand
from subscriptions.models import SubscriptionPlan, BillingPeriod


class Command(BaseCommand):
    help = 'Seed default subscription plans'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Weekly Fresh Box',
                'description': 'Get fresh produce delivered weekly',
                'price': 25.00,
                'period': BillingPeriod.WEEKLY,
                'is_active': True,
            },
            {
                'name': 'Monthly Fresh Box',
                'description': 'Get fresh produce delivered monthly',
                'price': 90.00,
                'period': BillingPeriod.MONTHLY,
                'is_active': True,
            },
            {
                'name': 'Premium Weekly',
                'description': 'Premium selection with organic options',
                'price': 40.00,
                'period': BillingPeriod.WEEKLY,
                'is_active': True,
            },
            {
                'name': 'Premium Monthly',
                'description': 'Premium selection with organic options',
                'price': 150.00,
                'period': BillingPeriod.MONTHLY,
                'is_active': True,
            },
        ]

        created_count = 0
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} subscription plans')
        )
