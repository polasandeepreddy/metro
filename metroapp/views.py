from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from .forms import UserRegisterForm
from .models import Ticket
from django.db.models import Q
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()

def register(request):
    """Handles user registration."""
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Metro Ticket Booking.")
            return redirect('home')
        else:
            messages.error(request, "Error in registration. Please check your details.")
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    """Handles user login requiring both email and phone."""
    if request.method == "POST":
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(request, email=email, phone=phone, password=password)

        if user:
            login(request, user)
            messages.success(request, "Login successful! Welcome back.")
            return redirect('home')
        else:
            messages.error(request, "Invalid email, phone, or password.")

    return render(request, 'login.html')

def user_logout(request):
    """Logs out the user."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def home(request):
    """Renders the home page."""
    return render(request, 'home.html')

@login_required
def book_ticket(request):
    """Handles ticket booking and generates a QR code."""
    if request.method == "POST":
        start_station = request.POST['start']
        end_station = request.POST['end']
        price = 50.00  # Example price calculation
        ticket = Ticket.objects.create(user=request.user, start_station=start_station, end_station=end_station, price=price)

        # Generate QR Code
        qr_data = f'Ticket for {request.user.email}: {start_station} to {end_station}'
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        ticket.qr_code.save(f'qr_{ticket.id}.png', ContentFile(buffer.getvalue()))
        ticket.save()

        messages.success(request, "Ticket booked successfully!")
        return render(request, 'ticket.html', {'ticket': ticket})

    return render(request, 'book_ticket.html')

@login_required
def profile(request):
    """Displays user profile with booked tickets."""
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'profile.html', {'tickets': tickets})

def custom_password_reset(request):
    """Handles password reset by email or phone number."""
    if request.method == "POST":
        identifier = request.POST.get("identifier")  # Could be email or phone
        try:
            user = User.objects.get(Q(email=identifier) | Q(phone=identifier))  # Lookup by email or phone

            # Generate password reset token
            token = default_token_generator.make_token(user)

            # Send email with password reset link
            reset_link = f"{settings.SITE_URL}/reset-password/{user.pk}/{token}/"
            send_mail(
                "Password Reset Request",
                f"Click the link to reset your password: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            messages.success(request, "A password reset link has been sent to your email.")
            return redirect("login")

        except User.DoesNotExist:
            messages.error(request, "No user found with this email or phone number.")

    return render(request, "password_reset.html")
