from django.shortcuts import render_to_response,redirect,HttpResponse
from django.contrib.auth import *
from django.template import RequestContext
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.conf import settings
from collections import defaultdict
from forms import *
from models import *

import string,random
chars = string.ascii_lowercase

import requests,simplejson,urllib2

def sumdict(list):
	ret = defaultdict(int)
	for i in xrange(len(list)):
		for k,v in list[i].items():
			ret[k] += v
	return dict(ret)

def home(request):
	if request.user.is_authenticated():
		return redirect('/profile/')
	else:
		return render_to_response('home.html',context_instance=RequestContext(request))

def usrlogout(request):
	logout(request)
	User.objects.filter(id=request.user.id).delete()
	return redirect('/')

def linkedin(request):
	LINKEDIN_CONSUMER_KEY = settings.LINKEDIN_CONSUMER_KEY
	LINKEDIN_CONSUMER_SECRET = settings.LINKEDIN_CONSUMER_SECRET
	REDIRECT_URI = 'http://localhost:8000/oauth2/access/'
	ACCESS_URL = 'https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id=' + LINKEDIN_CONSUMER_KEY + '&state=DAINAK23121234&redirect_uri=' + REDIRECT_URI
	return redirect(ACCESS_URL)

def access(request):
	AUTHORIZATION_CODE = request.GET['code']
	REDIRECT_URI = 'http://localhost:8000/oauth2/access/'
	STATE = request.GET['state']
	LINKEDIN_CONSUMER_KEY = settings.LINKEDIN_CONSUMER_KEY
	LINKEDIN_CONSUMER_SECRET = settings.LINKEDIN_CONSUMER_SECRET
	TOKEN_URL = 'https://www.linkedin.com/uas/oauth2/accessToken?grant_type=authorization_code&code=' + AUTHORIZATION_CODE + '&redirect_uri=' + REDIRECT_URI + '&client_id=' + LINKEDIN_CONSUMER_KEY + '&client_secret=' + LINKEDIN_CONSUMER_SECRET

	resp = requests.get(TOKEN_URL).text
	access_token = simplejson.loads(resp)['access_token']

	data_url = 'https://api.linkedin.com/v1/people/~:(first-name,email-address,last-name)?format=json&oauth2_access_token=' + access_token

	f =requests.get(data_url)
	profile_data = simplejson.loads(f.text)

	email= profile_data['emailAddress']

	try:
		get_email = UserProfile.objects.get(email=email)
	except UserProfile.DoesNotExist:
		try:
			UserProfile(email=email).save()
		except UserProfile.IntegrityError:
			pass

	random_username = ''.join(random.choice('abcdefghijklmn12345678') for x in range(9))
	request.session['password'] = User.objects.make_random_password()		
	User.objects.create_user(username=random_username,password=request.session['password'],email=profile_data['emailAddress']).save()		
	user = authenticate(username=random_username,password=request.session['password'])		
		
	login(request,user)
	request.session['linkedin_access_token'] = access_token
	return redirect('/profile/')

def profile(request):
	linkedin_access_token = request.session['linkedin_access_token']

	linkedin_data_url = 'https://api.linkedin.com/v1/people/~:(first-name,email-address,last-name,headline,picture-urls::(original),skills,educations)?format=json&oauth2_access_token=' + linkedin_access_token
	f = requests.get(linkedin_data_url)
	linkedin_profile_data = simplejson.loads(f.text)
	request.session['email'] = linkedin_profile_data['emailAddress']
	profile = UserProfile.objects.get(email=linkedin_profile_data['emailAddress'])

	if profile.is_github_connected:
		github_access_token = UserProfile.objects.get(email=request.session['email']).github_access_token
		get_githubuser_url = 'https://api.github.com/user?access_token=' + github_access_token
		userjson = requests.get(get_githubuser_url).text
		username = simplejson.loads(userjson)['login']

		list_languages_dict = []

		get_repos_url = 'https://api.github.com/users/' + username + '/repos?access_token=' + github_access_token
		repos = simplejson.loads(requests.get(get_repos_url).text)
		for i in xrange(len(repos)):
			if not repos[i]['fork']:
				get_repo_languages = 'https://api.github.com/repos/'+ username + '/' + repos[i]['name'] + '/languages?access_token=' + github_access_token
				languages = simplejson.loads(requests.get(get_repo_languages).text)
				list_languages_dict.append(languages)

		final_dict = sumdict(list_languages_dict)
		fval = ''
		val = ''
		for k,v in final_dict.items():
			val = '{language:"' + k + '",val:' + format(v) + '},'
			fval += val

		fval = [x for x in fval]
		fval.pop()
		fval = ''.join(fval)

		return render_to_response('profile.html',{'linkedin_profile_data':linkedin_profile_data,
												  'profile':profile,
												  'github_access_token':github_access_token,
												  'github_user':username,
												  'dnut_values':fval,
												  'repos':repos},context_instance=RequestContext(request))
	else:
		return render_to_response('profile.html',{'linkedin_profile_data':linkedin_profile_data,'profile':profile},context_instance=RequestContext(request))

def github(request):
	GITHUB_KEY = settings.GITHUB_KEY
	GITHUB_SECRET = settings.GITHUB_SECRET
	authorize_base_url = 'https://github.com/login/oauth/authorize'
	access_base_url = 'https://github.com/login/oauth/access_token'
	redirect_uri = 'http://localhost:8000/github/access/'

	get_auth_code_url = authorize_base_url + '?client_id=' + GITHUB_KEY + '&scope=user,repo&state=dasd89as67dasjkd&?redirect_uri=' + redirect_uri
	return redirect(get_auth_code_url)

def github_access(request):
	GITHUB_KEY = settings.GITHUB_KEY
	GITHUB_SECRET = settings.GITHUB_SECRET
	access_base_url = 'https://github.com/login/oauth/access_token'

	authorization_code = request.GET['code']
	get_access_token_url = access_base_url + '?client_id=' + GITHUB_KEY + '&client_secret=' + GITHUB_SECRET +'&scope=user,repo&state=dasd89as67dasjkd&code=' + authorization_code
	resp = requests.get(get_access_token_url).text
	github_access_token = resp.split('&')[0].split('=')[1]	

	email = request.session['email']

	# github_access_token = userprofile.github_access_token
	github_data_url = 'https://api.github.com/users?access_token=' + github_access_token
	f = requests.get(github_data_url)
	user = simplejson.loads(f.text)
	
	UserProfile.objects.filter(email=email).update(is_github_connected=True,github_access_token=github_access_token)
	request.session['github_access_token'] = github_access_token
	
	return redirect('/profile/')