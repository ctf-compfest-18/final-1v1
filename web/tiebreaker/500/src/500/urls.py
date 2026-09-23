from django.conf.urls.defaults import patterns, url
urlpatterns = patterns('500.views',
    url(r'^$', 'home'), url(r'^login/$', 'login'), url(r'^dashboard/$', 'dashboard'),
    url(r'^course/(?P<course_id>[A-Za-z0-9_-]+)/?$', 'course'),
    url(r'^logout/$', 'logout'),
    url(r'^flag/?$', 'flag'),
    url(r'^.*$', 'not_found'))
