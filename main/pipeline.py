from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect

from django.utils.translation import ugettext_lazy as _

from social_core.exceptions import AuthException


def check_email_exists(backend, user, response, *args, **kwargs):
    # TODO twitter, google, facebook, github
    email = response.get('email')
    print(email)
    if not email:
        return
    # check if given email is in use
    count = User.objects.filter(username=email).count()

    # user is not logged in, social profile with given uid doesn't exist
    # and email is in use
    if not user and count:
        # TODO messages
        raise AuthException(backend, 'This email is already in use.')
