from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUserModel, Profile

# 1. Custom Form - Essential to handle the missing 'username'
class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUserModel
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Force remove username if UserCreationForm tries to inject it
        if 'username' in self.fields:
            del self.fields['username']

# 2. Profile Inline
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    extra = 0
    max_num = 1

# 3. Custom User Admin
class CustomUserAdmin(UserAdmin):
    add_form = AdminUserCreationForm
    model = CustomUserModel
    inlines = (ProfileInline,)

    list_display = ('email', 'is_staff', 'is_superuser', 'is_active')
    ordering = ('email',)
    readonly_fields = ('date_joined', 'last_login')

    # The Edit Page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # The Add Page - EXTREMELY SPECIFIC
    # If 'password' causes an error, Django 5.0+ usually expects 'password1' and 'password2'
    # because that is what the UserCreationForm actually produces.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'), 
        }),
    )

    filter_horizontal = ('groups', 'user_permissions')
    search_fields = ('email',)

    # CRITICAL OVERRIDE: 
    # This prevents the "Unknown field" error by telling the Admin 
    # not to validate the 'add_fieldsets' against the model directly.
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

admin.site.register(CustomUserModel, CustomUserAdmin)