from django import forms
from .models import Employee

class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = [
            'emp_id',
            'phone',
            'join_date',
            'attendance_percentage'
        ]
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'})
        }
