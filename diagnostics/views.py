from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse

from diagnostics.report import *

from . import forms, models


def diagnostic(request, user, diag):
    if diag == 'new':
        currdiagnostic = models.Diagnostics.objects.create(user=User.objects.get(id=user))
    else:
        currdiagnostic = models.Diagnostics.objects.get(id=diag)

    if request.method == 'GET':

        diagnosticFormObjects = [forms.DiagnosticForm(i, currdiagnostic) for i in models.DiagnosisType.objects.all()]

        uploadform = forms.FileForm()

        ekg = models.DiagnosticsFiles.objects.filter(
            diagnostics=currdiagnostic,
            file_type=models.FileType.objects.get(name='EKG')
        )
        image_url = None
        if len(ekg) == 1:
            image_url = '/media/' + str(ekg[0].file_path).replace('.pdf', '-3_1.png')
            print(image_url)


    elif request.method == 'POST':
        if 'diagnostic' in request.POST:

            for i in models.DiagnosisType.objects.all():
                form = forms.DiagnosticForm(i, currdiagnostic, data=request.POST)
                if form.is_valid():
                    form.save(currdiagnostic)

            form = forms.FileForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                form.save(currdiagnostic)

            return redirect(reverse('diagnostic:diagnostic', kwargs={'user': user, 'diag': diag}))


    return render(request, 'diagnostics/diagnostics.html', {
        'u': user,
        'diag': currdiagnostic.id,

        'diagnosticFormObjects': diagnosticFormObjects,
        'uploadform': uploadform,
        'image_url': image_url
    })


def generate_report(request):
    from . import report

    return redirect(request.META['HTTP_REFERER'])


class DiagnosticResults(TemplateView):
    pass

def diagnostic_report_view(request, user, diag):
    if request.method == 'POST':
        ruller = bool(int(request.POST['show_ruller']))
        page_number = request.POST['page_number']
        if page_number == '':
            page_number = None
        else:
            page_number = int(page_number)
        report = DiagnosticReports()
        if 'Load_reports' in request.POST:
            return report.generate_diagnostic_reports_view(user, diag, None, page_number)
        else:
            return report.generate_diagnostic_reports_view(user, diag, ruller, page_number)
    return redirect(request.META['HTTP_REFERER'])



