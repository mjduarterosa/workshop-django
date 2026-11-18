from django import forms
from .models import Member

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["firstname", "lastname", "email", "phone", "joined_date"]
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not email.endswith("@example.com"):
            raise forms.ValidationError("Use your @example.com address.")
        return email
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone is None:
            return phone  # field left empty
        digits = str(phone)
        if len(digits) != 9 or digits[0] != "9":
            raise forms.ValidationError(
                "Enter a valid 9-digit phone number starting with 9."
            )
        return phone
