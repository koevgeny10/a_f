from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from eventlog.models import log  # function


class EmailBackend(ModelBackend):

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=username)
        except User.MultipleObjectsReturned:
            log(user=User.objects.filter(email=username).order_by('id').first(),
                action='USER_MULTIPLE_OBJECTS_ERROR')
            return User.objects.filter(email=username).order_by('id').first()
        except User.DoesNotExist:
            return None

        if getattr(user, 'is_active') and user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.UserDoesNotExist:
            return None
