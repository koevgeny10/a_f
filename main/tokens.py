from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.userprofile.user_main_email_confirmed)
        )


class TokenGeneratorForAltEmail(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.userprofile.user_alt_email_confirmed) +
            six.text_type(user.userprofile.user_alternative_email)
        )


account_activation_token = TokenGenerator()
alt_email_confirmation = TokenGeneratorForAltEmail()
