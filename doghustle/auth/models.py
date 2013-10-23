from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
	user = models.CharField(max_length=20,blank=True)
	email = models.EmailField(max_length=254,primary_key=True)
	is_github_connected = models.BooleanField(blank=True)
	is_bitbucket_connected = models.BooleanField(blank=True)
	github_access_token = models.CharField(max_length=300,blank=True)
	bitbucket_access_token = models.CharField(max_length=300,blank=True)


