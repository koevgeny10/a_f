from django.conf.urls import url
from django.contrib.auth.views import (
    password_reset, password_reset_done, password_reset_confirm, password_reset_complete,
)

from . import views

urlpatterns = [
    url(r'^$', views.LoginView.as_view(), name='login'),

    url(r'^about/', views.about, name='about'),
    url(r'^home/', views.home, name='home'),
    url(r'^logout/', views.logout_view, name='logout'),
    url(r'^sign_up/', views.RegisterView.as_view(), name='sign_up'),

    url(r'^aboutuser/(?P<pk>\d+)/', views.about_user, name='about_user'),
    url(r'^connect/(?P<operation>.+)/(?P<pk>\d+)/$', views.change_friends, name='change_friends'),
    url(r'^profile/', views.profile, name='profile'),

    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^activate_alt_email/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<email>\w+|[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        views.activate_alt_email, name='activate_alt_email'),

    # password reset
    url(r'^reset-password/$', password_reset,
        {
            'template_name': 'password_reset/password_reset_form.html',
            'email_template_name': 'password_reset/password_reset_email.html',
        },
        name='reset_password'
        ),
    url(r'^reset-password/done/$', password_reset_done,
        {'template_name': 'password_reset/password_reset_done.html'}, name='password_reset_done'
        ),
    url(r'^reset-password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', password_reset_confirm,
        {'template_name': 'password_reset/password_reset_confirm.html'}, name='password_reset_confirm'
        ),
    url(r'^reset-password/complete/$', password_reset_complete,
        {'template_name': 'password_reset/password_reset_complete.html'}, name='password_reset_complete'
        ),

    url(r'^oferta/$', views.oferta, name='oferta'),

    url(r'graph/$', views.diagnostic_pdf_view, name='user_graph'),
]
