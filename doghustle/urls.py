from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from doghustle.auth.views import *

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    # Auth URL's and VIEWS - Disable them if not necessary
    url(r'^$',home),
    url(r'^profile/$', profile),
    # url(r'^profile/complete/$', profile_complete),
    url(r'^logout/$', usrlogout),
    url(r'^login/linkedin/$',linkedin),
    url(r'^addgithub/$',github),
    url(r'^github/access/$',github_access),
    url(r'^oauth2/access/$',access),

    # Basic Static Pages Rendering - Add more pages like blog,news,landing page etc, as per requirement. 
    # url(r'^about/$', TemplateView.as_view(template_name='about.html')),
    # url(r'^faq/$', TemplateView.as_view(template_name='faq.html')),
    # url(r'^tac/$', TemplateView.as_view(template_name='tac.html')),
)
