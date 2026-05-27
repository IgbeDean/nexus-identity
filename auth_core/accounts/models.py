from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

# Create your models here.

#----------- Here we create a custom manager on how users can be saved to database ----------#
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
    
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)




# ---------------- Here we create The Custom User Model -----------
class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Set the email as the unique identifier
    USERNAME_FIELD = 'email'
    
    # REQUIRED_FIELDS are fields prompted for when creating a user via createsuperuser
    # Note: email and password are required by default.
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email



# ---------------- Here we create The User Profle Model -----------
from django.conf import settings
from PIL import Image
import uuid

class Profile(models.Model):
    # This links the Profile to the Custom User we built in Phase 1 & 2
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    # We'll handle the actual image files later, but we need the field now
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    # email verification
    email_verified = models.BooleanField(default=False)

    # We'll use this to generate the unique link
    verification_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True, editable=False)
    
    # keep track of the token
    token_created_at = models.DateTimeField(auto_now_add=True)

    def full_name(self):
        return f'{self.last_name} {self.first_name}'

    def __str__(self):
        return f'{self.user.email} Profile'
    
    # The Override
    def save(self, *args, **kwargs):
        # First, run the normal save logic
        super().save(*args, **kwargs)

        # Now, open the image we just saved
        img = Image.open(self.image.path)

        # Check if it's larger than 300x300
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size) # Resizes while maintaining aspect ratio
            img.save(self.image.path)  # Overwrite the large image with the small one