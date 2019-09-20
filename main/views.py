import random

from django.contrib import messages

# email conformation
from django.core.mail import send_mail
from django.conf import settings

from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

# authentication, login, views, render, ect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.static import serve
from django.views.generic import View
from django.utils import timezone

# signals
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from eventlog.models import Log  # objects class
from eventlog.models import log  # function

# translation
from django.utils.translation import ugettext_lazy as _

# parse HTTP_USER_AGENT
from user_agents import parse

# charts
from . import mycharts

# forms here
from .forms import (UserLoginForm, RegistrationForm,
                    UserEditForm, UserEditCustomerProfileForm)

# models here
from django.contrib.auth.models import User
from django.db.models import Q

from social_django.models import UserSocialAuth

from .models import (UserLogFail, UserProfile,
                     UserFriend, LogHistory,
                     LogHistoryType, Invitation)

from .tokens import account_activation_token, alt_email_confirmation

from tests import forms as testForms
from tests import models as testModels

from diagnostics import models as diagModels


def get_data(section):
    # I take querysets
    # answers = testModels.Answer.objects.filter(profile__exact=request.user.userprofile)
    questions = testModels.Test.objects.all()
    questions = [i for i in questions if i.section == section]
    variants = [j.variants.all() for j in questions]
    return variants, questions


def for_valid_form(user, form):
    for question, variants in form.cleaned_data.items():
        try:
            variants = eval(variants)
        except SyntaxError:
            pass
        question = testModels.Test.objects.get(id=int(question))
        if type(variants) is list:
            testModels.Answer.objects.filter(profile__exact=user.userprofile,
                                             question__exact=question).delete()
            for i in variants:
                variant = question.variants.all()[int(i)]
                testModels.Answer(profile=user.userprofile,
                                  question=question,
                                  variant=variant).save()
        if type(variants) is int:
            variant = question.variants.all()[variants]
            testModels.Answer.objects.update_or_create(profile=user.userprofile,
                                                       question=question,
                                                       defaults={'variant': variant})


def check_finish_test(user):
    answers = testModels.Answer.objects.filter(profile__exact=user.userprofile)
    questions = testModels.Test.objects.all()
    for i in questions:
        if len(answers.filter(question__exact=i)):
            pass
        else:
            break
    else:
        user.userprofile.finish_test = True
        # Send email
        send_mail(
            _('Passing test at agefree'),
            _('Congratulation, you have successfuly pass the test'),
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )


def about(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/home')
    return render(request, 'index/page.html', {})


@login_required
def home(request):
    # only doctors has the permission
    try:
        if not request.user.userprofile.role.isDoctor():
            return redirect('/profile')
    except AttributeError:
        return redirect('/profile')

    query = request.GET.get('q')
    if query:
        try:
            user = User.objects.get(userprofile__phone=query)
        except ObjectDoesNotExist:
            user = None
    else:
        user = None
    return render(request, 'index/home.html', {
        'user': user,
    })


# user's information page
@login_required
def profile(request):
    info = get_object_or_404(UserProfile, pk=request.user.userprofile.pk)  # user's custom profile (image, about, ect)

    form = UserEditForm(instance=request.user)

    # agefree
    form_customer = UserEditCustomerProfileForm(instance=info, auto_id='customer_%s')

    # by default user's contact email is the same as user's login email
    if not info.user_contact_email:
        form_customer = UserEditCustomerProfileForm(instance=info,
                                                    initial={'user_contact_email': request.user.email},
                                                    auto_id='customer_%s')

    form_username = UserEditForm(instance=request.user, auto_id='user_%s')

    try:
        friend = UserFriend.objects.get(current_user=request.user)
        friends = friend.users.all()
    except UserFriend.DoesNotExist:
        friends = None

    activity_logs = Log.objects.filter(user=request.user.id)
    login_logs = LogHistory.objects.filter(Q(user=request.user.id) &
                                           Q(loghistory_type_idmoment__type_name='success')
                                           ).order_by('-user_login_date')

    TestFormClass = testForms.TestForm
    cur_user = request.user

    variants1, questions = get_data('life style')
    questions1 = [i.question for i in questions]
    lifeStyleTest = TestFormClass(cur_user, variants1)
    variants2, questions = get_data('diseases')
    questions2 = [i.question for i in questions]
    diseasesTest = TestFormClass(cur_user, variants2)
    variants3, questions = get_data('motivation')
    questions3 = [i.question for i in questions]
    motivationTest = TestFormClass(cur_user, variants3)

    if request.method == 'POST' and 'customform' in request.POST:
        form_customer = UserEditCustomerProfileForm(request.POST, request.FILES or None, instance=info)
        form_username = UserEditForm(request.POST, instance=request.user)

        if form_customer.is_valid() and form_username.is_valid():
            info = form_customer.save(commit=False)
            info.user = request.user
            try:
                info.user_photo = request.FILES['file']
            except:
                print('No file')
            info.save()
            form_username.save()
            messages.success(request, _('Success!'))
        else:
            messages.error(request, _('Sorry, try again.'))
        return redirect('/profile')

    elif request.method == 'POST' and 'test' in request.POST:

        form = TestFormClass(cur_user, variants1, data=request.POST)
        if form.is_valid():
            for_valid_form(cur_user, form)

        form = TestFormClass(cur_user, variants2, data=request.POST)
        if form.is_valid():
            for_valid_form(cur_user, form)

        form = TestFormClass(cur_user, variants3, data=request.POST)
        if form.is_valid():
            for_valid_form(cur_user, form)

        if not request.user.userprofile.finish_test:
            check_finish_test(cur_user)

        return redirect('/profile')

    return render(request, 'index/profile.html', {
        'user': request.user,
        'form': form,
        'friends': friends,
        'activities': activity_logs,
        'login_logs': login_logs,

        # agefree
        'form_customer': form_customer,
        'form_username': form_username,

        'questions1': questions1,
        'questions2': questions2,
        'questions3': questions3,
        'lifeStyleTest': lifeStyleTest,
        'diseasesTest': diseasesTest,
        'motivationTest': motivationTest,

        # 'diagnosticFormObjects': diagnosticFormObjects
    })


# end here


# info about another user
@login_required
def about_user(request, pk):
    # only doctors has the permission
    try:
        if not request.user.userprofile.role.isDoctor():
            return redirect('/profile')
    except AttributeError:
        return redirect('/profile')

    try:
        friend = UserFriend.objects.get(current_user=request.user)
        friends = friend.users.all()
    except UserFriend.DoesNotExist:
        friends = None

    if pk != str(request.user.pk):
        user = get_object_or_404(User, pk=pk)

        TestFormClass = testForms.TestForm

        variants1, questions = get_data('life style')
        questions1 = [i.question for i in questions]
        lifeStyleTest = TestFormClass(user, variants1)
        variants2, questions = get_data('diseases')
        questions2 = [i.question for i in questions]
        diseasesTest = TestFormClass(user, variants2)
        variants3, questions = get_data('motivation')
        questions3 = [i.question for i in questions]
        motivationTest = TestFormClass(user, variants3)

        prev_diag = diagModels.Diagnostics.objects.filter(user__exact=user)
    else:
        return redirect('/profile')

    if request.method == 'POST' and 'test' in request.POST:

        form = TestFormClass(user, variants1, data=request.POST)
        if form.is_valid():
            for_valid_form(user, form)

        form = TestFormClass(user, variants2, data=request.POST)
        if form.is_valid():
            for_valid_form(user, form)

        form = TestFormClass(user, variants3, data=request.POST)
        if form.is_valid():
            for_valid_form(user, form)

        if not request.user.userprofile.finish_test:
            check_finish_test(user)

        return redirect(request.path)

    return render(request, 'index/about_user.html', {
        'user': user,
        'friends': friends,
        'pk': pk,

        'questions1': questions1,
        'questions2': questions2,
        'questions3': questions3,
        'lifeStyleTest': lifeStyleTest,
        'diseasesTest': diseasesTest,
        'motivationTest': motivationTest,

        'prev_diag': prev_diag
    })


# end here


# pdf generation (reportlab)
def diagnostic_pdf_view(request):

    chart_data = [random.randint(0, 5) for k in range(11)]

    diagnostic_graph = mycharts.DiagnosticChartDrawing()

    diagnostic_graph.set_graph_data(chart_data)

    # a-la render
    binarystuff = diagnostic_graph.asString('pdf')

    return HttpResponse(binarystuff, 'application/pdf')


# end here


# add or remove friend
@login_required
def change_friends(request, operation, pk):
    friend = User.objects.get(pk=pk)
    if operation == 'add':
        UserFriend.make_friend(request.user, friend)
        messages.info(request, _('You have successfully added a user.'))
        return redirect('about_user', pk=pk)
    elif operation == 'remove':
        UserFriend.lose_friend(request.user, friend)
        messages.info(request, _('You have successfully removed a user.'))
    return redirect('profile')


# end here


class RegisterView(View):
    form_class = RegistrationForm
    template_name = 'index/sign_up.html'

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/home')

        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            user.userprofile.offer = True  # Если POST отправился значит точно согласились с офертой

            # check if the user was invited
            invited_user = Invitation.objects.filter(to_user_email=user.email).first()
            if invited_user:
                invited_user.success = True
                invited_user.save()

            messages.info(request, _('Thanks for registering {}. You are now logged in.'.format(user.username)))
            # cleaned data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # if credentials are correct
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)

            return HttpResponseRedirect('/')

        messages.error(request, _('Sorry, try again.'))
        return render(request, self.template_name, {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        info = get_object_or_404(UserProfile, pk=user.userprofile.pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        info.user_main_email_confirmed = True
        info.save()
        # login(request, user, backend='main.backends.EmailBackend')
        messages.info(request, _('Thank you for your email confirmation.'))
        return HttpResponseRedirect('/')
    else:
        messages.error(request, _('Activation link is invalid!'))
        return HttpResponseRedirect('/')


def activate_alt_email(request, uidb64, token, email):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        info = get_object_or_404(UserProfile, pk=user.userprofile.pk)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and alt_email_confirmation.check_token(user, token):
        info.user_alt_email_confirmed = True
        info.user_alternative_email = email
        info.save()
        messages.info(request, _('Thank you for your alt email confirmation.'))
        return HttpResponseRedirect('/')
    else:
        messages.error(request, _('Activation link is invalid!'))
        return HttpResponseRedirect('/')


class LoginView(View):
    form_class = UserLoginForm
    template_name = 'index/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/profile')
        form = self.form_class(None)

        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request):
        form = self.form_class(request.POST)

        # remember me is false
        if not request.POST.get('remember_me'):
            request.session.set_expiry(0)

        if form.is_valid():
            # cleaned data
            username = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # if credentials are correct
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
            else:
                # user login failed
                log_fail(request, username, password)
                messages.error(request, _('Sorry, try again.'))
                return render(request, self.template_name, {'form': form})

        return HttpResponseRedirect('/profile')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# TODO
# protected media
def protected_serve(request, path, document_root=settings.MEDIA_ROOT):
    try:
        # obj = UserProfile.objects.get(user=request.user.id, user_photo=path)  # private image
        obj = UserProfile.objects.get(user_photo=path)  # public image
        obj_image_url = obj.user_photo.url
        correct_image_url = obj_image_url.replace('/media/', '')
        if correct_image_url == path:
            return serve(request, path, document_root)
        return serve(request, path, document_root)
    except ObjectDoesNotExist:
        return HttpResponse(_('Sorry you don\'t have permission to access this file'))


def my_log(request, log_type='success'):
    user_agent = parse(request.META['HTTP_USER_AGENT'])

    # UserLog history type name
    log_name = LogHistoryType()
    log_name.type_name = log_type
    log_name.save()

    user_log = LogHistory()
    user_log.loghistory_type_idmoment = log_name

    if log_type == 'success':
        if not request.POST.get('remember_me'):
            user_log.user_remember_me = False
    elif log_type == 'logout':
        user_log.user_login_date = None
        user_log.user_logout_date_time = timezone.now()

    user = request.user

    user_log.user = user

    # user's ip
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ipaddress = x_forwarded_for.split(',')[-1].strip()
    else:
        ipaddress = request.META.get('REMOTE_ADDR')

    user_log.user_ip = ipaddress
    user_log.user_browser = user_agent.browser.family
    user_log.user_browser_version = user_agent.browser.version_string
    user_log.user_os = user_agent.os.family
    user_log.user_os_version = user_agent.os.version_string
    user_log.user_device = user_agent.device.family

    # authentication type
    try:
        UserSocialAuth.objects.get(user_id=request.user.id)
    except UserSocialAuth.DoesNotExist:
        user_log.user_logged_via = 'django default authentication'
    else:
        user_log.user_logged_via = 'social authentication {}'.format(
            UserSocialAuth.objects.get(user_id=request.user.id).provider
        )

    user_log.save()


def log_fail(request, username, password):
    user_agent = parse(request.META['HTTP_USER_AGENT'])

    log(user=request.user, action='LOG_FAIL',
        extra={
            'browser.family': user_agent.browser.family,
            'browser.version_string': user_agent.browser.version_string,
            'os.family': user_agent.os.family,
            'os.version_string': user_agent.os.version_string,
            'device.family': user_agent.device.family,
        })

    attempt = UserLogFail()

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ipaddress = x_forwarded_for.split(',')[-1].strip()
    else:
        ipaddress = request.META.get('REMOTE_ADDR')
    attempt.user_ip = ipaddress
    attempt.username_attempt = username
    attempt.user_failed_password = password
    attempt.save()


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    my_log(request, 'success')
    if not request.user.userprofile.user_main_email_confirmed:
        messages.warning(request, _('The email address associated with your account has not been verified.'))


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    my_log(request, 'logout')


# @receiver(user_login_failed)
# def user_login_failed_callback(sender, credentials, **kwargs):
# pass


def oferta(request):
    return render(request, 'index/oferta.html')
