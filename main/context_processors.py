from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

# translation
from django.utils.translation import ugettext_lazy as _

# forms here
from django.contrib.auth.forms import PasswordChangeForm

from eventlog.models import log  # function
from social_django.models import UserSocialAuth

# forms here
from .forms import UserEditAltEmail, UserEditSocialNetworksForm, UserEditSettingsForm, InvitationForm

# models here
from .models import UserProfile, UserSocialNetworks, Settings

from .tokens import alt_email_confirmation, account_activation_token


def settings_form(request):
    if not request.user.is_anonymous:
        info = get_object_or_404(UserProfile, pk=request.user.userprofile.pk)  # user's custom profile
        try:
            custom_settings = Settings.objects.get(is_the_chosen_one=True)  # custom global settings
        except Settings.DoesNotExist:
            custom_settings = True
        social_networks = get_object_or_404(UserSocialNetworks, pk=request.user.usersocialnetworks.pk)

        try:
            user_permission = request.user.userprofile.role.name
        except AttributeError:
            user_permission = None

        form_password = PasswordChangeForm(user=request.user)
        form_alt_email = UserEditAltEmail(instance=info)
        form_user_settings = UserEditSettingsForm(instance=info)
        form_social_networks = UserEditSocialNetworksForm(instance=social_networks)

        form_invitation = InvitationForm()

        try:
            UserSocialAuth.objects.get(user_id=request.user.id)
        except UserSocialAuth.DoesNotExist:
            is_signin_social_network = False
        else:
            is_signin_social_network = True

        if request.method == 'POST' and 'passwordedit' in request.POST and not is_signin_social_network:
            form_password = PasswordChangeForm(data=request.POST, user=request.user)
            if form_password.is_valid():
                form_password.save()
                update_session_auth_hash(request, form_password.user)

                log(user=request.user, action='CHANGE_PASSWORD',
                    extra={
                        'user_name': request.user.username
                    })

                messages.success(request, _('Your password has been successfully changed.'))
            else:
                messages.error(request, _('Sorry, try again.'))

        elif request.method == 'POST' and 'settingsedit' in request.POST:
            form_user_settings = UserEditSettingsForm(request.POST, instance=info)

            if form_user_settings.is_valid():
                form_user_settings.save()

                log(user=request.user, action='CHANGE_SETTINGS',
                    extra={
                        'user_name': request.user.username
                    })
                messages.success(request, _('Your settings have been successfully changed.'))
            else:
                messages.error(request, _('Sorry, try again.'))

        elif request.method == 'POST' and 'altemailedit' in request.POST:
            form_alt_email = UserEditAltEmail(request.POST, instance=info)

            if form_alt_email.is_valid():
                info = form_alt_email.save(commit=False)
                if info.user_alternative_email != request.user.userprofile.user_alternative_email:
                    current_site = get_current_site(request)
                    subject = _('Alternative email')
                    message = render_to_string('activations/acc_active_alt_email.html', {
                        'user': request.user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
                        'token': alt_email_confirmation.make_token(request.user),
                        'email': info.user_alternative_email,
                    })
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [info.user_alternative_email]

                    send_mail(subject, message, from_email, to_list, fail_silently=True)

                    messages.success(request,
                                     _('Check your verification code ') + '"{}"!'.format(info.user_alternative_email))
                else:
                    messages.warning(request, _('Enter another email.'))
            else:
                messages.error(request, _('You cannot enter this email.'))

        elif request.method == 'POST' and 'socialnetworksedit' in request.POST:
            form_social_networks = UserEditSocialNetworksForm(request.POST, instance=social_networks)
            if form_social_networks.is_valid():
                form_social_networks.save()
                messages.success(request, _('Done!'))

                log(user=request.user, action='CHANGE_SOCIAL',
                    extra={
                        'user_name': request.user.username
                    })
            else:
                messages.error(request, _('Wrong links.'))

        elif request.method == 'POST' and 'verifymainemail' in request.POST:
            current_site = get_current_site(request)
            subject = _('Confirmation email')
            message = render_to_string('activations/acc_active_email.html', {
                'user': request.user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(request.user.pk)),
                'token': account_activation_token.make_token(request.user),
            })
            from_email = settings.EMAIL_HOST_USER
            to_list = [request.user.email]

            send_mail(subject, message, from_email, to_list, fail_silently=True)

            messages.success(request, _('Check your verification code ') + '"{}"!'.format(request.user.email))

        elif request.method == 'POST' and 'invitation' in request.POST:
            form_invitation = InvitationForm(request.POST)
            if form_invitation.is_valid():
                invitation = form_invitation.save(commit=False)
                if User.objects.filter(username=invitation.to_user_email).first():
                    messages.error(request, _('This user already exists.'))
                else:
                    invitation.from_user = request.user
                    invitation.save()

                    current_site = get_current_site(request)
                    subject = _('Invitation')

                    message = render_to_string('invitation/invitation_template_0.html', {
                        'from_user': request.user,
                        'to_email': invitation.to_user_email,
                        'domain': current_site.domain,
                    })

                    from_email = settings.EMAIL_HOST_USER
                    to_list = [invitation.to_user_email]

                    send_mail(subject, message, from_email, to_list, fail_silently=True)

                    messages.info(request, _('Thank you for help!'))
            else:
                messages.error(request, _('Fail.'))

        return {
            'custom_settings': custom_settings,
            'user_permission': user_permission,

            'form_invitation': form_invitation,

            'form_password': form_password,
            'form_alt_email': form_alt_email,
            'form_user_settings': form_user_settings,
            'form_social_networks': form_social_networks,
            'is_signin_social_network': is_signin_social_network,
        }
    return {

    }
