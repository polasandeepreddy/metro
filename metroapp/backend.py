from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailPhoneAuthBackend(ModelBackend):
    """Custom authentication backend allowing email & phone verification"""

    def authenticate(self, request, email=None, phone=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email, phone=phone)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
