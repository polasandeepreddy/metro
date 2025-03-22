from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    """Custom manager allowing user creation with email and phone."""

    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        if not phone:
            raise ValueError("The Phone field is required")

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email=email, phone=phone, password=password, **extra_fields)

class User(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)  # Email is required and unique
    phone = models.CharField(max_length=15, unique=True)  # Phone is required and unique

    USERNAME_FIELD = 'email'  # Primary login field
    REQUIRED_FIELDS = ['phone']  # Phone is required during signup

    objects = CustomUserManager()  # Use custom manager

    def __str__(self):
        return f"{self.email} ({self.phone})"

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_station = models.CharField(max_length=100)
    end_station = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.user.email}"
