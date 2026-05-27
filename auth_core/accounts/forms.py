from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUserModel, Profile

# The User Form
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUserModel
        fields = ('email',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Remove the "Your password can't be..." messages
        self.fields['password1'].help_text = ""
        self.fields['password2'].help_text = ""
    


# The Profile Form
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        # We list the fields the user is allowed to change
        fields = ['first_name', 'last_name', 'bio', 'phone_number', 
                  'address', 'city', 'state', 'country', 'image']
        
        # Adding some CSS classes so we can style the inputs in the next step
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'address': forms.TextInput(attrs={'placeholder': '123 Nexus Street'}),
        }