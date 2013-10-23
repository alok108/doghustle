from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django import forms
from django.contrib.auth.models import User

class SimpleUserCreation(UserCreationForm):
	email = forms.EmailField(required=True, widget=forms.widgets.TextInput(attrs={'class':'form-control','placeholder': 'Email Address'}))
	full_name = forms.CharField(required=True, widget=forms.widgets.TextInput(attrs={'class':'form-control','placeholder': 'Full Name'}))
	username = forms.CharField(required=False, widget=forms.widgets.HiddenInput())
	first_name = forms.CharField(required=False, widget=forms.widgets.HiddenInput())
	last_name = forms.CharField(required=False, widget=forms.widgets.HiddenInput())
	password1 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class':'form-control','placeholder': 'Password'}))
	password2 = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class':'form-control','placeholder': 'Password Confirmation'}))
	
	class Meta:
		model = User
		fields = ["full_name","email","password1","password2"]

class SimpleAuthForm(AuthenticationForm):
	email = forms.EmailField(widget=forms.widgets.TextInput(attrs={'class':'form-control','placeholder': 'Email Address'}))
	username = forms.CharField(required=False, widget=forms.widgets.HiddenInput())	
	password = forms.CharField(widget=forms.widgets.PasswordInput(attrs={'class':'form-control','placeholder': 'Password'}))
	
	class Meta:
		model = User
		fields = ["email","username","password"]

	def __init__(self, *args, **kwargs):
	    super(SimpleAuthForm, self).__init__(*args, **kwargs)
	    self.fields.keyOrder = [
	        'email',
	        'username',
	        'password']
