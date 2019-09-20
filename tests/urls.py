from django.conf.urls import url
from . import views

app_name = 'tests'

urlpatterns = [
    url(r'^$', views.TestView.as_view(), name='tests')
]