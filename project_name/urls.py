from django.conf.urls import include, url
#from django.conf.urls.static import static
from django.contrib import admin
#from django.conf import settings

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # url(r'^api/v1.0/', include('', namespace='api')),
]

#if settings.ENV == 'local':
#    # static files (images, css, javascript, etc.)
#    urlpatterns += static(r'^media/(?P<path>.*)$', document_root=settings.MEDIA_ROOT)

