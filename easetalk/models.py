from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, role="anonymousUser", **extra_fields):
        """Creates and saves a user with the given email, random username (if anonymous), and password."""
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", role)

        # If user is anonymous, generate a random username 
        if role == "anonymousUser":
            extra_fields["username"] = f"anon_{uuid.uuid4().hex[:8]}"  # Generates random ID

        user = self.model(email=email, **extra_fields)  
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Creates a superuser with an 'admin' role and access to Django admin panel."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(email, password, **extra_fields) # Ensure superuser is not anonymous or therapist
    

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    objects = CustomUserManager()    
    class UserRole(models.TextChoices):
        ANONYMOUS_USER = "anonymousUser", "Anonymous"
        THERAPIST = "therapist", "Therapist"
        ADMIN = "admin", "Admin"  # New role for superusers

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.ANONYMOUS_USER
    )

    USERNAME_FIELD = "email"  # Use email instead of username for authentication
    REQUIRED_FIELDS = []  # No additional fields required

    # Generate a random username for Anonymous users
    def save(self, *args, **kwargs):
        if self.role == self.UserRole.ANONYMOUS_USER and not self.username:
            self.username = f"anon_{uuid.uuid4().hex[:8]}"  # Generates unique 8-character username
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username or self.email} ({self.role})"


# store chat messages between users
class Message(models.Model):
    sender = models.ForeignKey("easetalk.CustomUser", related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey("easetalk.CustomUser", related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"