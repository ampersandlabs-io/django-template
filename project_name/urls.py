from django.conf.urls import include, url
#from django.conf.urls.static import static
from django.contrib import admin
#from django.conf import settings

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # url(r'^api/v1.0/docs/', include('rest_framework_swagger.urls')),
    # url(r'^api/v1.0/', include('', namespace='api')),
]

#if settings.ENV == 'local':
#    # static files (images, css, javascript, etc.)
#    urlpatterns += static(r'^media/(?P<path>.*)$', document_root=settings.MEDIA_ROOT)

#################################
## DJANGO 1.8 and lower

#from django.conf.urls import patterns, include, url
#from django.contrib import admin

#admin.autodiscover()

#urlpatterns = (
#    '',
#    url(r'^admin/', include(admin.site.urls)),
#    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
#    # url(r'^api/v1.0/docs/', include('rest_framework_swagger.urls')),
#    # url(r'^api/v1.0/', include('', namespace='api')),
#)
