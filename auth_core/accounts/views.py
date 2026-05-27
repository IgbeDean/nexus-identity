# ------------- Building the Registration View -------------#
from django.urls import reverse_lazy
# to create a view
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import CustomUserCreationForm

import uuid
from .utils import send_verification_email


# ----------------Building the Registration View -------------#
class UserRegisterView(SuccessMessageMixin, CreateView):
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    success_message = "Account created! Please check your email to verify your identity."

    def form_valid(self, form):
        # 1. Save the user to the database
        response = super().form_valid(form)
        
        # 2. 'self.object' is the user that was just created
        user = self.object
        
        # 3. Fire off the verification email
        try:
            send_verification_email(self.request, user)
        except Exception as e:
            # If the email fails, we still want the user created, 
            # but we should log the error or notify the user.
            print(f"Email failed to send: {e}")
            
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Registration failed. Please correct the errors below.")
        return super().form_invalid(form)



# ----------------Building the Login & Logout Views -------------#
# built-in login and logout views
from django.contrib.auth.views import LoginView, LogoutView

# built-in django flash messages
from django.contrib import messages

from django.conf import settings

# Import Axes structural tools to inspect live database attempts
from axes.models import AccessAttempt

class UserLoginView(SuccessMessageMixin, LoginView):
    template_name = 'accounts/login.html'
    success_message = 'Welcome back!'

    def form_invalid(self, form):
        # 1. Let Django and Axes process the failure internally first
        response = super().form_invalid(form)
        
        # 2. Grab the email/username string entered into the form
        username = form.cleaned_data.get('username') or form.data.get('username')
        
        if username:
            # Look up the tracking row for this specific IP + target credential combination
            ip_address = self.request.META.get('REMOTE_ADDR')
            attempt = AccessAttempt.objects.filter(username=username, ip_address=ip_address).first()
            
            # 4. Check if the database record actually exists and has the attribute
            if attempt and hasattr(attempt, 'failures_since_start'):
                max_attempts = getattr(settings, 'AXES_FAILURE_LIMIT', 5)
                failures_recorded = attempt.failures_since_start
                attempts_left = max_attempts - failures_recorded
                
                if attempts_left > 0:
                    messages.warning(
                        self.request, 
                        f"Invalid credentials. Warning: You have {attempts_left} attempt(s) remaining before security lockout."
                    )
                    return response
                
        # Fallback if no database row has generated yet for this user session
        messages.error(self.request, "Invalid username or password. Please try again.")
        return response

    def get_success_url(self):
        # look for the 'next' parameter
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        
        # Fallback to home if 'next' doesn't exist
        return reverse_lazy('home')


class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        # We check if the user is authenticated so we don't spam 
        # messages if they just refresh the logout URL
        if request.user.is_authenticated:
            messages.info(request, "You have been logged out!")
        return super().dispatch(request, *args, **kwargs)


# building a logout sequence
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
def logout_sequence_view(request):
    # This view will now accept both GET and POST
    return render(request, 'accounts/logout_sequence.html')



# ----------------- Building the Home View-------------#
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'accounts/home.html'


# ----------------- Building all Profile Related View Logic-------------#
from django.contrib.auth.mixins import LoginRequiredMixin

class NexusLoginRequiredMixin(LoginRequiredMixin):
    """Custom Mixin to add a warning message when a guest tries to access protected pages."""
    
    def handle_no_permission(self):
        # Add the warning message
        if not self.request.user.is_authenticated:
            messages.warning(self.request, "Page cannot be accessed without authentication.")
        # Redirect to login page (Django handles the 'next' parameter automatically)
        return super().handle_no_permission()

# ----------------- Building the Profile View-------------#
class ProfileView(NexusLoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'


# ----------------- Building the Edit Profile View-------------#
from django.views.generic import UpdateView
from .models import Profile
from .forms import ProfileUpdateForm

class ProfileUpdateView(NexusLoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/edit_profile.html'

    # This tells Django to only edit the profile of the logged-in user
    def get_object(self):
        return self.request.user.profile
    
    def get_success_url(self):
        messages.success(self.request, "Your profile has been updated!")
        return reverse_lazy('profile') # Redirect back to the "About You" page



# ----------------- Building the User Password Change View-------------#
from django.contrib.auth.views import PasswordChangeView

class UserPasswordChangeView(NexusLoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        messages.success(self.request, "Your password was successfully updated!")
        return super().form_valid(form)
    


# ----------------Building the Account Status View -------------#
class AccountStatusView(NexusLoginRequiredMixin, TemplateView):
    template_name = 'accounts/account_status.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # You can add logic here later, like:
        # context['is_verified'] = self.request.user.is_verified
        return context



# ----------------Building the Email Request Verification Link -------------#
from django.contrib.auth.decorators import login_required

@login_required
def request_verification_link(request):
    # only send if they are not verified
    if not request.user.profile.email_verified:
        try:
            send_verification_email(request, request.user)
            messages.success(request, "A verification link has been sent to your inbox!")
        except Exception as e:
            messages.error(request, "We couldn't send the email right now. Please try again later.")
            print(f"Manual email trigger failed: {e}")
    else:
        messages.info(request, "Your account is already verified.")
    
    return redirect('profile')



# ----------------Building the Email Verification View -------------#
import uuid
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

def verify_email(request, token):
    # Try to find a profile with this exact token
    profile = get_object_or_404(Profile, verification_token=token)

    # check if link is older than 24 hours
    expiry_time = profile.token_created_at + timedelta(hours=24)

    if timezone.now() > expiry_time:
        # 1. Regenerate credentials safely
        profile.verification_token = uuid.uuid4()
        profile.token_created_at = timezone.now()
        profile.save()
        
        # 2. Automatically fire off the fresh email right here so they don't have to be logged in!
        try:
            # Passing profile.user ensures the backend utility knows who to send it to
            send_verification_email(request, profile.user)
            messages.error(request, "Your verification link had expired. We have automatically sent a fresh link to your inbox.")
        except Exception as e:
            messages.error(request, "Your link expired, and we couldn't send a new one automatically. Please login and request a new link.")
            print(f"Auto-recovery email failed: {e}")
            
        return redirect('login')  # Safely send them to login, completely bypassing the @login_required trap

    # If it's within 24 hours, proceed with verification
    if not profile.email_verified:
        profile.email_verified = True
        profile.verification_token = None  # Burn the token so it can't be reused
        profile.save()
        messages.success(request, "Your email has been verified! Please login.")
    else:
        messages.info(request, "This account is already verified.")
        
    return redirect('login')



# ----------------- Building the Error (404, 500 etc..) Pages view Views-------------#
def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)






# ----------------- Building the Axes lockout view-------------#
# accounts/views.py
from django.shortcuts import render
from django.conf import settings

def axes_lockout_view(request, credentials=None, *args, **kwargs):
    # Pass the cool-off time (in seconds) to the template for JavaScript to use
    # 30 minutes = 1800 seconds
    cooloff_seconds = 1800 
    
    context = {
        'cooloff_seconds': cooloff_seconds,
        'email_attempted': credentials.get('username') if credentials else "Your account"
    }
    # Render a custom beautiful template with a 403 status code
    return render(request, 'accounts/lockout.html', context, status=403)






# ------------- Building the google auth message -------------
# accounts/views.py (or at the bottom of the file)
from django.dispatch import receiver
from django.contrib import messages
from allauth.account.signals import user_logged_in

@receiver(user_logged_in)
def customize_social_login_message(request, user, **kwargs):
    """
    Catches both standard and social logins handled by allauth.
    Ensures a uniform, branded 'Welcome back!' flash message appears.
    """
    # 1. Clear out any generic allauth messages so they don't double up
    storage = messages.get_messages(request)
    for message in storage:
        pass # This flushes the existing system message queue cleanly
        
    # 2. Inject your signature branded flash message
    messages.success(request, "Welcome back!")