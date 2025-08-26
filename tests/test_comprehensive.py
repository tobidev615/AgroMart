import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from userprofiles.models import UserProfile, UserType
from farmers.models import FarmerProfile, Produce
from orders.models import Order, OrderStatus
from subscriptions.models import SubscriptionPlan, BillingPeriod


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )


@pytest.fixture
def farmer_user():
    user = User.objects.create_user(
        username="farmer",
        email="farmer@example.com",
        password="testpass123"
    )
    profile = UserProfile.objects.get(user=user)
    profile.role = UserType.FARMER
    profile.save()
    return user


@pytest.fixture
def consumer_user():
    user = User.objects.create_user(
        username="consumer",
        email="consumer@example.com",
        password="testpass123"
    )
    profile = UserProfile.objects.get(user=user)
    profile.role = UserType.CONSUMER
    profile.save()
    return user


@pytest.fixture
def farmer_profile(farmer_user):
    return FarmerProfile.objects.create(
        user=farmer_user,
        name="Test Farmer",
        location="Test Location"
    )


@pytest.fixture
def produce(farmer_profile):
    return Produce.objects.create(
        farmer=farmer_profile,
        name="Tomatoes",
        variety="Cherry",
        quantity_available=100,
        unit="kg",
        price_per_unit=5.00
    )


@pytest.fixture
def subscription_plan():
    return SubscriptionPlan.objects.create(
        name="Weekly Box",
        description="Fresh produce weekly",
        price=25.00,
        period=BillingPeriod.WEEKLY,
        is_active=True
    )


@pytest.mark.django_db
class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user(self, api_client):
        """Test user registration."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "role": "CONSUMER"
        }
        response = api_client.post("/api/v1/accounts/register/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert response.data["user"]["username"] == "newuser"
    
    def test_jwt_login(self, api_client, user):
        """Test JWT login."""
        data = {"username": "testuser", "password": "testpass123"}
        response = api_client.post("/api/v1/accounts/jwt/login/", data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
    
    def test_me_endpoint(self, api_client, user):
        """Test user profile endpoint."""
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/accounts/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["username"] == "testuser"


@pytest.mark.django_db
class TestFarmers:
    """Test farmer-related endpoints."""
    
    def test_farmer_profile_me(self, api_client, farmer_user, farmer_profile):
        """Test farmer profile endpoint."""
        farmer_user.refresh_from_db()
        api_client.force_authenticate(user=farmer_user)
        response = api_client.get("/api/v1/farmers/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Test Farmer"
    
    def test_create_produce(self, api_client, farmer_user, farmer_profile):
        """Test creating produce."""
        farmer_user.refresh_from_db()
        api_client.force_authenticate(user=farmer_user)
        data = {
            "name": "Carrots",
            "variety": "Orange",
            "quantity_available": 50,
            "unit": "kg",
            "price_per_unit": 3.00
        }
        response = api_client.post("/api/v1/farmers/produce/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Carrots"
    
    def test_public_produce_list(self, api_client, produce):
        """Test public produce listing."""
        response = api_client.get("/api/v1/farmers/public/produce/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Tomatoes"


@pytest.mark.django_db
class TestOrders:
    """Test order-related endpoints."""
    
    def test_add_to_cart(self, api_client, consumer_user, produce):
        """Test adding item to cart."""
        api_client.force_authenticate(user=consumer_user)
        data = {"produce_id": produce.id, "quantity": 2}
        response = api_client.post("/api/v1/cart/items/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantity"] == 2
    
    def test_checkout(self, api_client, consumer_user, produce):
        """Test checkout process."""
        api_client.force_authenticate(user=consumer_user)
        
        # Add to cart first
        cart_data = {"produce_id": produce.id, "quantity": 2}
        api_client.post("/api/v1/cart/items/", cart_data)
        
        # Checkout
        response = api_client.post("/api/v1/checkout/")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == OrderStatus.PENDING
        assert response.data["total_amount"] == "10.00"
    
    def test_order_list(self, api_client, consumer_user):
        """Test order listing."""
        api_client.force_authenticate(user=consumer_user)
        response = api_client.get("/api/v1/orders/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSubscriptions:
    """Test subscription endpoints."""
    
    def test_subscription_plans_list(self, api_client):
        """Test subscription plans listing."""
        response = api_client.get("/api/v1/plans/")
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_subscription(self, api_client, consumer_user, subscription_plan):
        """Test creating subscription."""
        api_client.force_authenticate(user=consumer_user)
        today = date.today()
        next_week = today + timedelta(days=7)
        data = {
            "plan": subscription_plan.id,
            "items": [],
            "start_date": today.isoformat(),
            "next_delivery_date": next_week.isoformat()
        }
        response = api_client.post("/api/v1/subscriptions/", data)
        assert response.status_code == status.HTTP_201_CREATED


class TestNotifications:
    """Test notification endpoints."""
    
    def test_notifications_list(self, api_client, consumer_user):
        """Test notifications listing."""
        api_client.force_authenticate(user=consumer_user)
        response = api_client.get("/api/v1/notifications/")
        assert response.status_code == status.HTTP_200_OK


class TestDeliveries:
    """Test delivery endpoints."""
    
    def test_deliveries_list(self, api_client, consumer_user):
        """Test deliveries listing."""
        api_client.force_authenticate(user=consumer_user)
        response = api_client.get("/api/v1/deliveries/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSecurity:
    """Test security features."""
    
    def test_rate_limiting(self, api_client):
        """Test rate limiting on sensitive endpoints."""
        # Try to register multiple times quickly
        data = {
            "username": "rateuser",
            "email": "rate@example.com",
            "password": "testpass123",
            "role": "CONSUMER"
        }
        
        # First request should succeed
        response = api_client.post("/api/v1/accounts/register/", data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Multiple rapid requests should be rate limited
        for _ in range(5):
            response = api_client.post("/api/v1/accounts/register/", data)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        else:
            pytest.fail("Rate limiting not working")
    
    def test_input_sanitization(self, api_client):
        """Test input sanitization."""
        malicious_data = {
            "username": "test<script>alert('xss')</script>",
            "email": "test@example.com",
            "password": "testpass123",
            "role": "CONSUMER"
        }
        response = api_client.post("/api/v1/accounts/register/", malicious_data)
        # Should either reject or sanitize the input
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED]


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_response(self, api_client):
        """Test 404 error response."""
        response = api_client.get("/api/v1/nonexistent/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "code" in response.data
    
    def test_403_response(self, api_client, consumer_user):
        """Test 403 error response."""
        api_client.force_authenticate(user=consumer_user)
        # Try to access farmer-only endpoint
        response = api_client.get("/api/v1/farmers/me/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "code" in response.data


@pytest.mark.django_db
class TestCaching:
    """Test caching functionality."""
    
    def test_public_produce_caching(self, api_client, produce):
        """Test that public produce list is cached."""
        # First request
        response1 = api_client.get("/api/v1/farmers/public/produce/")
        assert response1.status_code == status.HTTP_200_OK
        
        # Second request should be cached
        response2 = api_client.get("/api/v1/farmers/public/produce/")
        assert response2.status_code == status.HTTP_200_OK
        assert response1.data == response2.data


class TestAPIVersioning:
    """Test API versioning."""
    
    def test_v1_endpoints(self, api_client):
        """Test that v1 endpoints work."""
        response = api_client.get("/api/v1/health/")
        assert response.status_code == status.HTTP_200_OK
    
    def test_legacy_endpoints(self, api_client):
        """Test that legacy endpoints still work."""
        response = api_client.get("/api/health/")
        assert response.status_code == status.HTTP_200_OK


