from datetime import datetime

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import extras
from django.utils.translation import ugettext_lazy as _

from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

from .models import UserProfile, UserSocialNetworks, Invitation

from . import custom_widgets


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(
        attrs={
            'class': 'form-control input-sm chat-input',
            'placeholder': _('Email'),
        }
    ))

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control input-sm chat-input',
            'placeholder': _('Password'),
        }
    ))

    captcha = ReCaptchaField(widget=ReCaptchaWidget(attrs={'class': 'g-recaptcha'}), label='')

    class Meta:
        model = User
        fields = ('email', 'password', 'captcha',)


class InvitationForm(forms.ModelForm):

    class Meta:
        model = Invitation
        fields = ('to_user_email', )


# custom registration form
class RegistrationForm(UserCreationForm):
    username = forms.EmailField(widget=forms.TextInput(
        attrs={
            'class': 'form-control input-sm chat-input',
            'placeholder': _('Email'),
        }
    ))

    first_name = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control input-sm chat-input',
            'placeholder': _('First name'),
        }
    ))

    last_name = forms.CharField(widget=forms.TextInput(
        attrs={
            'class': 'form-control input-sm chat-input',
            'placeholder': _('Last name'),
        }
    ))

    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control input-sm chat-input',
            'placeholder': _('Password'),
        }
    ))

    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control input-sm chat-input',
            'placeholder': _('Password confirmation'),
        }
    ))

    #offer = forms.BooleanField(label=_('I agree with the contract of public offer'))

    captcha = ReCaptchaField(widget=ReCaptchaWidget(attrs={'class': 'g-recaptcha'}), label='')

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'password1',
            'password2',
            #'offer',
            'captcha',
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['username']  # email = username

        if commit:
            user.save()

        return user

    def clean(self):
        username = self.cleaned_data['username']
        if username and \
                (User.objects.filter(email=username).exists() or User.objects.filter(username=username).exists()):
            raise forms.ValidationError(_('This email is already in use.'))

        username = self.cleaned_data.get('email')
        return username
# end here


# custom user edit form
class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'password',
        )


# end here


# custom profile edit forms
class UserEditSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'user_settings_text_with_icons',
            'user_settings_show_prompts',
        )


class UserEditProfilePhotoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'user_photo',
        )


class UserEditAltEmail(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            'user_alternative_email',
        )


class UserEditSocialNetworksForm(forms.ModelForm):

    class Meta:
        model = UserSocialNetworks
        fields = (
            'user_facebook',
            'user_twitter',
            'user_google_plus',
            'user_github',
            'user_linkedin',
        )

    def clean(self):
        user_facebook = self.cleaned_data['user_facebook']
        user_twitter = self.cleaned_data['user_twitter']
        user_google_plus = self.cleaned_data['user_google_plus']
        user_github = self.cleaned_data['user_github']
        user_linkedin = self.cleaned_data['user_linkedin']

        # if links are wrong and not empty then raise validation error
        if not user_facebook.startswith('https://www.facebook.com/') and user_facebook:
            raise forms.ValidationError(_('Facebook link is not correct.'))
        if not user_twitter.startswith('https://twitter.com/') and user_twitter:
            raise forms.ValidationError(_('Twitter link is not correct.'))
        if not user_google_plus.startswith('https://plus.google.com/') and user_google_plus:
            raise forms.ValidationError(_('Google+ link is not correct.'))
        if not user_github.startswith('https://github.com/') and user_github:
            raise forms.ValidationError(_('Github link is not correct.'))
        if not user_linkedin.startswith('https://www.linkedin.com/') and user_linkedin:
            raise forms.ValidationError(_('Linkedin link is not correct.'))


class UserEditCustomerProfileForm(forms.ModelForm):
    # years settings
    date_range = 100
    this_year = datetime.now().year
    years_list = range(this_year - date_range, this_year + 1)
    birthday = forms.DateField(widget=extras.SelectDateWidget(years=years_list))
    # end here

    address = forms.CharField(label=_('Address'),
                              required=False,
                              error_messages={'invalid_choice': _('Wrong address')},
                              widget=custom_widgets.AddressWidget)

    phone = forms.CharField(label=_('Phone'),
                            min_length=19)

    user_photo = forms.ImageField(label=_('User photo'),
                                  required=False,
                                  error_messages={'invalid': _("Image files only")},
                                  widget=forms.FileInput)

    class Meta:
        model = UserProfile

        fields = (
            'about_user',
            'address',
            'birthday',
            'dispatch',
            'phone',
            'sex',
            'user_contact_email',
            'user_full_name',
            'user_photo',
            'user_personal_info',
        )

# end here
