from django import forms
from .models import Vendor, PurchaseOrder, PurchaseOrderItem

class VendorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Vendor
        fields = ['name', 'email', 'phone', 'address', 'is_active']
        
    def save(self, commit=True):
        vendor = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            from django.contrib.auth.hashers import make_password
            vendor.password_hash = make_password(password)
        if commit:
            vendor.save()
        return vendor

class PortalLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
