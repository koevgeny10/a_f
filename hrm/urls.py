from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^oauth/', include('social_django.urls', namespace='social')),
    url(r'^i18n/', include('django.conf.urls.i18n')),  # languages
    url(r'^jsi18n/', JavaScriptCatalog.as_view(), name='js-catalog'),

    url(r'^', include('main.urls')),

    url(r'^diagnostic/', include('diagnostics.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
