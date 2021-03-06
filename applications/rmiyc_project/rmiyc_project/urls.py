from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
#from rmiyc.views import MyRegistrationView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rmiyc_project.views.home', name='home'),
    # url(r'^rmiyc_project/', include('rmiyc_project.foo.urls')),
    url(r'^users/', include('profiles.urls')),
    url(r'^rmiyc/', include('rmiyc.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^data/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': False}),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^accounts/register/$', MyRegistrationView.as_view(),name='registration_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^leaderboard/', include('leaderboard.urls')),
    url(r'^profile/', include('profiles.urls')),
    url(r'', include('rmiyc.urls')),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()