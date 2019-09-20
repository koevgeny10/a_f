from django.conf.urls import url
from . import views


app_name = 'diagnostic'
urlpatterns = [
    url(r'^(?P<user>[0-9]+)/(?P<diag>[0-9]+|new)/$', views.diagnostic, name='diagnostic'),
    url(r'^results/$', views.DiagnosticResults.as_view(), name='results'),
    url(r'^generate/$', views.generate_report, name='generate'),
    url(r'reportview/([0-9]+)/([0-9]+)/$', views.diagnostic_report_view, name='reportview')
]