from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm
from .models import User, Address, Review, UserPreference, Complaint, Product, Category, Brand, Order, Payment


class SignupForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            try:
                u = User.objects.get(email=email)
                if not u.is_active and not u.is_email_verified:
                    raise forms.ValidationError("Your email is not verified. Please verify your email first.")
            except User.DoesNotExist:
                pass
                
            user = authenticate(username=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password.")
            if not user.is_active:
                raise forms.ValidationError("Your account is disabled.")
            cleaned['user'] = user
        return cleaned


class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={'placeholder': '6-digit OTP', 'class': 'otp-input'}))


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Registered Email'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("No account found with this email.")
        return email


class ResetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
        label='Confirm New Password'
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'date_of_birth', 'profile_photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['user', 'created_at']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'body']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'title': forms.TextInput(attrs={'placeholder': 'Review title'}),
            'body': forms.Textarea(attrs={'placeholder': 'Share your experience...', 'rows': 4}),
        }


class UserPreferenceForm(forms.ModelForm):
    class Meta:
        model = UserPreference
        fields = ['email_order_updates', 'email_promotions', 'sms_order_updates', 'sms_promotions']


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['complaint_type', 'subject', 'description', 'order']
        widgets = {
            'complaint_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Subject of complaint', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your issue...', 'rows': 5, 'class': 'form-control'}),
            'order': forms.Select(attrs={'class': 'form-select'}),
        }


class AdminComplaintForm(forms.ModelForm):
    """Form for admins to respond to complaints"""
    class Meta:
        model = Complaint
        fields = ['status', 'admin_response', 'priority', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'admin_response': forms.Textarea(attrs={'placeholder': 'Admin response...', 'rows': 4, 'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }


class AdminOrderUpdateForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=Payment.METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_status = forms.ChoiceField(
        choices=Payment.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tracking_note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Optional note shown in tracking history...',
            'rows': 3,
            'class': 'form-control'
        })
    )

    class Meta:
        model = Order
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Internal admin note...',
                'rows': 3,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, payment=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_method'].initial = payment.method if payment else 'cod'
        self.fields['payment_status'].initial = payment.status if payment else 'pending'


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return files.get(name)

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True, 'class': 'form-control', 'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductForm(forms.ModelForm):
    video_upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
        required=False,
        help_text="Upload product video"
    )

    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand',
            'description', 'short_description', 'ingredients', 'how_to_use',
            'weight', 'material', 'metal_purity', 'warranty', 'artisan_story',
            'base_price', 'discount_percent', 'is_flash_sale', 'finish',
            'is_active', 'is_featured', 'is_new_arrival', 'is_bestseller'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'ingredients': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'how_to_use': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'weight': forms.TextInput(attrs={'placeholder': 'e.g., 5g, 10ml', 'class': 'form-control'}),
            'material': forms.TextInput(attrs={'placeholder': 'e.g., 18K Gold', 'class': 'form-control'}),
            'warranty': forms.TextInput(attrs={'placeholder': 'e.g., 1 Year', 'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'discount_percent': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'finish': forms.Select(attrs={'class': 'form-select'}),
        }

