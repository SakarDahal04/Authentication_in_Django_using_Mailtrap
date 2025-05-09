from django import forms
from account.models import User


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ["email", "name", "password", "confirm_password"]

    # Check if the passwords match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            # For add_error we need to mention which field the error should pop up in
            # This will be added to forms.error which we will send back to the frontend
            self.add_error(
                "confirm_password", "Password and Confirm Password does not match"
            )

        return cleaned_data

    # Check if the user is trying to regiter from the email which is already used for registration
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")

        return email


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(("No account is associated with this email"))

        return email
