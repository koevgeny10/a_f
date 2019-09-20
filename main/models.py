from io import BytesIO

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from eventlog.models import log

from PIL import Image

from multiselectfield import MultiSelectField


# global settings
class Settings(models.Model):
    setting_name = models.CharField(max_length=50, null=False, blank=False, default=None)

    additional_settings_available = models.BooleanField(default=True, verbose_name=_('Additional settings available'))
    alternative_email_edit_available = models.BooleanField(default=True, verbose_name=_('Alt email edit available'))
    font_size_edit_available = models.BooleanField(default=True, verbose_name=_('Font size edit available'))
    password_edit_available = models.BooleanField(default=True, verbose_name=_('Password edit available'))
    social_links_edit_available = models.BooleanField(default=True, verbose_name=_('Social links edit available'))
    table_buttons_text = models.BooleanField(default=True, verbose_name=_('Table buttons text available'))

    is_the_chosen_one = models.BooleanField(default=False, verbose_name=_('Active setting'))  # this model is 'unique'

    def save(self, *args, **kwargs):
        if self.is_the_chosen_one:
            try:
                temp = Settings.objects.get(is_the_chosen_one=True)
                if self != temp:
                    temp.is_the_chosen_one = False
                    temp.save()
            except Settings.DoesNotExist:
                pass
        super(Settings, self).save(*args, **kwargs)

    def __str__(self):
        return self.setting_name
# end global settings


# Roles
class Role(models.Model):
    name = models.CharField(max_length=50, null=True, unique=True, verbose_name=_('Role'))

    # 1 Врачь
    # 2 Асистент врача
    # 3 Пациент
    def isDoctor(self):
        return self.pk == 1 # Врачь

    #def has_permission(self, permission):
     #   return str(self.name) == str(permission)

    def __str__(self):
        return self.name
# end Roles


# Club
class Club(models.Model):
    name = models.CharField(max_length=200, null=True, unique=True, verbose_name=_('Club name'))

    def __str__(self):
        return self.name


class ClubUserLink(models.Model):
    club = models.ForeignKey('Club', null=True, blank=True)
    user = models.ForeignKey('UserProfile', null=True, blank=True)

    def __str__(self):
        return str(self.pk)
# end Club


class UserLog(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    user_ip = models.CharField(max_length=200)
    user_browser = models.CharField(max_length=100)
    user_browser_version = models.CharField(max_length=100)
    user_os = models.CharField(max_length=100)
    user_os_version = models.CharField(max_length=100)
    user_device = models.CharField(max_length=100)
    user_logged_via = models.CharField(max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.username + ' ' + self.user_ip


class LogHistoryType(models.Model):
    type_name = models.CharField(max_length=200)

    def __str__(self):
        return '{0} {1}'.format(str(self.pk),
                                self.type_name)


class LogHistory(UserLog):
    loghistory_type_idmoment = models.ForeignKey('LogHistoryType', on_delete=models.CASCADE)
    user_remember_me = models.BooleanField(default=True)
    user_login_date = models.DateTimeField(default=timezone.now, null=True)
    user_logout_date_time = models.DateTimeField(null=True)

    def __str__(self):
        return '{0} {1} {2}'.format(self.user.username,
                                    self.user_ip,
                                    self.loghistory_type_idmoment.type_name)

    class Meta:
        verbose_name_plural = "Log histories"


class Invitation(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    to_user_email = models.EmailField(null=True, blank=False, unique=True, verbose_name=_('E-mail of the invited user'))
    success = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {}'.format(self.from_user.email, self.to_user_email)


class UserLogFail(models.Model):
    user_ip = models.CharField(max_length=200)
    username_attempt = models.CharField(max_length=200, null=True)
    user_failed_password = models.CharField(max_length=200)

    def __str__(self):
        return '{0} {1}'.format(self.user_ip,
                                self.username_attempt)


def upload_user_photo_location(instance, filename):
    return '{0}-{1}/user/{2}'.format(instance.user.username, instance.user.pk, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey('Role', null=True, blank=True)
    about_user = models.TextField(null=True, blank=True, verbose_name=_('About user'))
    user_alternative_email = models.EmailField(null=True, blank=True, unique=True,
                                               verbose_name=_('Alt email'))

    # patronymic (по батькові)
    user_full_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_('Patronymic'))

    user_contact_email = models.EmailField(null=True, blank=False, unique=True, verbose_name=_('Contact email'))
    user_main_email_confirmed = models.BooleanField(default=False, verbose_name=_('Main email confirmed'))
    user_alt_email_confirmed = models.BooleanField(default=False, verbose_name=_('Alt email confirmed'))
    user_photo = models.ImageField(
        default='None/No_image.png',
        upload_to=upload_user_photo_location,
        null=True,
        blank=True,
        height_field='photo_height_field',
        width_field='photo_width_field',
        verbose_name=_('Photo')
    )

    # user_photo size
    photo_height_field = models.IntegerField(default=0)
    photo_width_field = models.IntegerField(default=0)

    finish_test = models.BooleanField(default=False, verbose_name=_('Test is finished'))
    # doctor = models.BooleanField(default=False, verbose_name=_('Doctor'))  # TODO remove this

    sexes = (
        ('Male', _('Male')),
        ('Female', _('Female'))
    )
    dispatches = (
        ('Email', _('Email')),
        ('SMS', _('SMS'))
    )
    sex = models.CharField(max_length=20, choices=sexes, null=True, blank=True, verbose_name=_('Sex'))
    birthday = models.DateField(null=True, blank=True, verbose_name=_('Birthday'))
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Address'))
    phone = models.CharField(max_length=20, null=True, blank=False, unique=True, verbose_name=_('Phone'))

    dispatch = MultiSelectField(max_length=50, choices=dispatches,
                                null=True, blank=True,
                                default=('Email', 'SMS'), verbose_name=_('Dispatch'))

    offer = models.BooleanField(default=False)
    user_personal_info = models.BooleanField(default=False,
                                             verbose_name=_('The user agrees to provide access to personal info'))

    # user can change this settings
    user_settings_text_with_icons = models.BooleanField(default=True, verbose_name=_('Text with icons'))
    user_settings_show_prompts = models.BooleanField(default=True, verbose_name=_('Show prompts'))
    # end here

    def save(self, *args, **kwargs):
        if not self.id:
            log(user=self.user, action='CREATE_PROFILE',
                extra={
                    'user_name': self.user.username
                })
        else:
            log(user=self.user, action='UPDATE_PROFILE',
                extra={
                    'user_name': self.user.username
                })
        self.photo_height_field = 400
        self.photo_width_field = 400

        # image compression and conversion to JPG
        if not self.user_photo == 'None/No_image.png':
            try:
                img = Image.open(BytesIO(self.user_photo.read()))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.thumbnail((self.user_photo.width / 1.5, self.user_photo.height / 1.5), Image.ANTIALIAS)
                output = BytesIO()
                img.save(output, format='JPEG', quality=70)
                output.seek(0)
                self.user_photo = InMemoryUploadedFile(output, 'ImageField',
                                                       "%s.jpg" % self.user_photo.name.split('.')[0],
                                                       'image/jpeg', None, None)
                log(user=self.user, action='PHOTO_UPDATE',
                    extra={
                        'user_name': self.user.username,
                        'user_photo': self.user_photo.url,
                    })
            except ValueError:
                log(user=self.user, action='IMAGE_VALUE_ERROR',
                    extra={
                        'user_name': self.user.username,
                        'user_photo': self.user_photo.url,
                    })

        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username + ' ' + str(self.phone)


class UserSocialNetworks(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_facebook = models.URLField(max_length=200, null=True, blank=True)
    user_twitter = models.URLField(max_length=200, null=True, blank=True)
    user_google_plus = models.URLField(max_length=200, null=True, blank=True)
    user_github = models.URLField(max_length=200, null=True, blank=True)
    user_linkedin = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return '{0} {1}'.format(self.user.username, self.user.pk)


class UserFriend(models.Model):
    users = models.ManyToManyField(User, related_name='friend_set')
    current_user = models.ForeignKey(User, related_name='owner', null=True, on_delete=models.CASCADE)

    @classmethod
    def make_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.add(new_friend)

    @classmethod
    def lose_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.remove(new_friend)


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])
        user_social_networks = UserSocialNetworks.objects.create(user=kwargs['instance'])


post_save.connect(create_profile, sender=User)
