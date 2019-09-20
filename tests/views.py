from django.shortcuts import render
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings
from . import forms, models

class TestView(LoginRequiredMixin, FormView):
    form_class = forms.TestForm
    template_name = 'tests/tests.html'
    success_url = '/tests'
    redirect_field_name = None


    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        variants = self.get_data()
        return form_class(variants, **self.get_form_kwargs())

    def get_data(self):

        # I take querysets
        answers = models.Answer.objects.filter(profile__exact=self.request.user.userprofile)
        questions = models.Test.objects.all()
        questions = [i for i in questions if not len(answers.filter(question__exact=i))]
        variants = [j.variants.all() for j in questions]

        # I take text from querysets
        self.questions = [i.question for i in questions]

        # variants = {id of question: list of variants related to this question}
        variants = {i[0].question.id: list(map(lambda x: x.variant, i)) for i in variants}
        return variants


    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['questions'] = self.questions
        return context

    def form_valid(self, form):
        if form.is_valid():
            for question, variants in form.cleaned_data.items():
                try:
                    variants = eval(variants)
                except SyntaxError:
                    pass
                if type(variants) is list:
                    question = models.Test.objects.get(id=int(question))
                    for i in variants:
                        variant = question.variants.all()[int(i)]
                        models.Answer(profile=self.request.user.userprofile,
                                      question=question,
                                      variant=variant).save()

        answers = models.Answer.objects.filter(profile__exact=self.request.user.userprofile)
        questions = models.Test.objects.all()
        for i in questions:
            if len(answers.filter(question__exact=i)):
                pass
            else: break
        else:
            self.success_url = '/' # ???????????
            # Send email
            send_mail(
                'Passing test at agefree',
                'Congratulation, you have successfuly pass the test',
                settings.DEFAULT_FROM_EMAIL,
                [self.request.user.email]
            )
        return super(self.__class__, self).form_valid(form)

    #def post(self, request, *args, **kwargs):
