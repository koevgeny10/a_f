from django import forms
from . import models
import re

class DiagnosticForm(forms.Form):
    def __init__(self, diag_type, diagnostic, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.parameters = {}
        k = 1
        field_order = []
        self.type = diag_type.name
        for i in models.ParameterDiagnostics.objects.filter(diagnosis_type__exact=diag_type, formula__exact=''):
            self.parameters[i.name] = i
            choises = i.variantsforparameterdiagnostics_set.all()
            if len(choises) != 0:
                choises = [[i.variant, i.variant] for i in choises]
                try:
                    initial = models.DiagnosticsResult.objects.get(diagnostics=diagnostic, parameter_diagnostics=i).value
                except models.DiagnosticsResult.DoesNotExist:
                    initial = None

                self.fields[i.name] = forms.CharField(
                    required=False,
                    initial=initial,
                    widget=forms.Select(choices=choises, attrs={'class': 'col-lg-2', 'form': 'diagnostic'}),
                    label='{}'.format(i.name)
                )

            elif 'Заключение' in i.name or 'Рекомендации' in i.name:
                try:
                    initial = models.DiagnosticsResult.objects.get(diagnostics=diagnostic, parameter_diagnostics=i).value
                except models.DiagnosticsResult.DoesNotExist:
                    initial = None

                self.fields['{}_{}'.format(i.pk,i.name)] = forms.CharField(
                    required=False,
                    widget=forms.Textarea(attrs={'class': 'col-lg-6', 'form': 'diagnostic'}),
                    label='{}'.format(i.name),
                    initial=initial
                )

            else:
                try:
                    initial = models.DiagnosticsResult.objects.get(diagnostics=diagnostic, parameter_diagnostics=i).value
                except models.DiagnosticsResult.DoesNotExist:
                    initial = None

                self.fields[i.name] = forms.DecimalField(
                    required=False,
                    widget=forms.NumberInput(attrs={'class': 'col-lg-2', 'form': 'diagnostic'}),
                    label='{}'.format(i.name),
                    initial=initial
                )

            field_order.append(k)
            k += 1

        for key, item in self.parameters.items():
            if item.position is None:
                continue
            for i, v in enumerate(field_order):
                if item.position == v:
                    field_order[i] = key
                    break
        for i, v in enumerate(field_order):
            if type(v) is int:
                field_order.pop(i)
        self.order_fields(field_order)



    def count_formuls(self, i, diagnostic):
        formula = i.formula
        j = 0
        execformula = ''
        while j < len(formula):
            if formula[j] == '[':
                param = ''
                while formula[j + 1] != ']':
                    j += 1
                    param += formula[j]
                try:
                    param = models.DiagnosticsResult.objects.get(
                        parameter_diagnostics=models.ParameterDiagnostics.objects.get(param_id=int(param)),
                        diagnostics=diagnostic
                    )
                except models.DiagnosticsResult.DoesNotExist:
                    return None
                execformula += param.value
                j += 2
                continue
            execformula += formula[j]
            j += 1

        value = eval(execformula)
        models.DiagnosticsResult.objects.update_or_create(
            parameter_diagnostics=i,
            diagnostics=diagnostic,
            defaults={'value': str(value)}
        )


    def save(self, diagnostic):
        for name, value in self.cleaned_data.items():
            if value is None:
                continue

            if 'Заключение' in name or 'Рекомендации' in name:
                reg = re.compile("(\d*)_.*")
                params = reg.findall(name)
                models.DiagnosticsResult.objects.update_or_create(
                    parameter_diagnostics=models.ParameterDiagnostics.objects.get(pk=int(params[0])),
                    diagnostics=diagnostic,
                    defaults={'value': value}
                )
            else:
                # try:
                models.DiagnosticsResult.objects.update_or_create(
                    parameter_diagnostics=self.parameters[name],
                    diagnostics=diagnostic,
                    defaults={'value': value}
                )
                # except models.ParameterDiagnostics.MultipleObjectsReturned:
                #     a = models.ParameterDiagnostics.objects.filter(name__exact=name)
                #     for i in a:
                #         if i.name == name:
                #             models.DiagnosticsResult.objects.update_or_create(
                #                 parameter_diagnostics=i,
                #                 diagnostics=diagnostic,
                #                 defaults={'value': value}
                #             )

        for i in models.ParameterDiagnostics.objects.exclude(formula__exact=''):
            self.count_formuls(i, diagnostic)


class FileForm(forms.Form):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.type = 'Files'
        for i in models.FileType.objects.all():
            self.fields[i.name] = forms.FileField(
                required=False,
                label='{}'.format(i.name),
                widget=forms.ClearableFileInput(
                    attrs={'form': 'diagnostic'}
                )
            )

    def save(self, diagnostic):
        #print(self.cleaned_data.items())
        for name, file in self.cleaned_data.items():
            if file is None:
                continue
            else:
                models.DiagnosticsFiles.objects.update_or_create(
                    diagnostics=diagnostic,
                    file_type=models.FileType.objects.get(name=name),
                    file_path=file
                )

        for i in models.DiagnosticsFiles.objects.filter(diagnostics__exact=diagnostic):
            if i.file_type == models.FileType.objects.get(name='Tanita'):
                self.tanita(i, diagnostic)
            elif i.file_type == models.FileType.objects.get(name='Fitmate'):
                self.fitmate(i, diagnostic)
            elif i.file_type == models.FileType.objects.get(name='Synevo'):
                self.blood(i, diagnostic)
            elif i.file_type == models.FileType.objects.get(name='EKG'):
                self.ekg(i, diagnostic)

    def tanita(self, file, diagnostic):
        from docx import Document
        import re

        trans = {
            'Воде в теле': 'Вода в организме',
            'Жир тела': 'Жир в организме'

        }

        doc = Document(file.file_path)
        muscles = False
        fat = False
        i = 0
        j = 0

        for para in doc.paragraphs:
            try:
                name = re.search('[А-Яа-я]([А-Яа-я]| )+', para.text).group(0)

                value = float(re.search('([0-9]|,)+', para.text).group(0).replace(',', '.'))
            except AttributeError:
                continue

            if fat:
                name = 'Жир ' + name.lower()
                i += 1
                if i == 5:
                    fat = False

            if muscles:
                name = 'Мышцы ' + name.lower()
                j += 1
                if j == 5:
                    muscles = False

            if 'Жир' in name and i is not 5:
                fat = True

            if 'Мышечная масса' in name and j is not 5:
                muscles = True

            try:
                models.DiagnosticsResult.objects.update_or_create(
                    parameter_diagnostics=models.ParameterDiagnostics.objects.get(
                        name__iexact=name if name not in trans else trans[name]
                    ),
                    diagnostics=diagnostic,
                    defaults={'value': value}
                )
            except models.ParameterDiagnostics.MultipleObjectsReturned:
                a = models.ParameterDiagnostics.objects.filter(
                    name__exact=name if name not in trans else trans[name]
                )
                for i in a:
                    if i.name == name if name not in trans else trans[name]:
                        models.DiagnosticsResult.objects.update_or_create(
                            parameter_diagnostics=i,
                            diagnostics=diagnostic,
                            defaults={'value': value}
                        )
            except models.ParameterDiagnostics.DoesNotExist:
                pass



    def fitmate(self, file, diagnostic):
        import subprocess
        import re

        path = str(file.file_path)
        newpath = path.replace('.pdf', '.html')

        subprocess.call('/usr/bin/pdftohtml {} -i {}'.format(
            '/opt/agefree/media_folder/' + path,
            '/opt/agefree/media_folder/' + newpath
        ).split(' '))

        with open('/opt/agefree/media_folder/' + newpath.replace('.html', 's.html'), encoding='utf-8') as file:
            text = file.read()

        param = {}
        kard = '<b>Кардио-респираторный тест&#160;(ml/Kg/min)</b><br/>\n'

        i = text.find(kard)
        value = float(re.search('([0-9]|,)+', text[i + len(kard):]).group(0).replace(',', '.'))
        param['МПК'] = value

        other = '<b>Итог</b><br/>\nНаша организация выражает вам благодарность за участие в в программе оценки данной фитнес-системы. В частности, ваши результаты следующие:<br/>\n'

        i = text.find(other)
        text = text[i + len(other):]

        chss = '<b>ЧСС покоя</b><br/>\n'
        i = text.find(chss)
        value = float(re.search('([0-9]|,)+', text[i + len(chss):]).group(0).replace(',', '.'))
        param['ЧСС'] = value

        sad = '<b>САД</b><br/>\n'
        i = text.find(sad)
        value = float(re.search('([0-9]|,)+', text[i + len(sad):]).group(0).replace(',', '.'))
        param['САД'] = value

        dad = '<b>ДАД</b><br/>\n'
        i = text.find(dad)
        value = float(re.search('([0-9]|,)+', text[i + len(dad):]).group(0).replace(',', '.'))
        param['ДАД'] = value

        VO2 = '<b>VO2/кг</b><br/>\n'
        i = text.find(VO2)
        value = float(re.search('([0-9]|,)+', text[i + len(VO2):]).group(0).replace(',', '.'))
        param['VO2'] = value

        for name, value in param.items():
            try:
                models.DiagnosticsResult.objects.update_or_create(
                    parameter_diagnostics=models.ParameterDiagnostics.objects.get(
                        name__iexact=name
                    ),
                    diagnostics=diagnostic,
                    defaults={'value': value}
                )
            except models.ParameterDiagnostics.MultipleObjectsReturned:
                a = models.ParameterDiagnostics.objects.filter(
                    name__exact=name
                )
                for i in a:
                    if i.name == name:
                        models.DiagnosticsResult.objects.update_or_create(
                            parameter_diagnostics=i,
                            diagnostics=diagnostic,
                            defaults={'value': value}
                        )
            except models.ParameterDiagnostics.DoesNotExist:
                pass

    def blood(self, file, diagnostic):
        import subprocess
        import re

        path = str(file.file_path)
        newpath = path.replace('.pdf', '.html')

        subprocess.call('/usr/bin/pdftohtml {} -i {}'.format(
            '/opt/agefree/media_folder/' + path,
            '/opt/agefree/media_folder/' + newpath
        ).split(' '))

        with open('/opt/agefree/media_folder/' + newpath.replace('.html', 's.html'), encoding='utf-8') as file:
            text = file.read()

        param = {}

        point = '<b>Холестерин</b><br/>'
        search = text.find(point)
        value = float(re.search('([0-9]|\.)+', text[search + len(point):]).group(0))
        print(value)
        param[393] = value

        point = '<b>Ліпопротеїди&#160;високої&#160;щільності&#160;(ЛПВЩ,&#160;</b><br/>'
        point2 = '<b>Референтний&#160;інтервал</b><br/>'
        search = text[:text.find(point)].rfind(point2)
        value = float(re.search('([0-9]|\.)+', text[search + len(point2):]).group(0))
        print(value)
        param[394] = value

        point = '<b>Ліпопротеїди&#160;низької&#160;щільності&#160;(ЛПНЩ,&#160;</b><br/>'
        point2 = '\n'
        search = text[:text.find(point)].rfind(point2)
        search = text[:search].rfind(point2)
        search = text[:search].rfind(point2)
        value = float(re.search('([0-9]|\.)+', text[search + len(point2):]).group(0))
        print(value)
        param[395] = value

        point = '<b>Тригліцериди</b><br/>'
        search = text.find(point)
        value = float(re.search('([0-9]|\.)+', text[search + len(point):]).group(0))
        print(value)
        param[396] = value

        point = '<b>Глюкоза&#160;(сироватка)</b><br/>'
        search = text.find(point)
        value = float(re.search('([0-9]|\.)+', text[search + len(point):]).group(0))
        print(value)
        param[397] = value

        for param_id, value in param.items():
            models.DiagnosticsResult.objects.update_or_create(
                parameter_diagnostics=models.ParameterDiagnostics.objects.get(param_id=param_id),
                diagnostics=diagnostic,
                defaults={'value': value}
            )

    def ekg(self, file, diagnostic):
        import subprocess

        path = str(file.file_path)
        newpath = path.replace('.pdf', '.html')

        subprocess.call('/usr/bin/pdftohtml {} {}'.format(
            '/opt/agefree/media_folder/' + path,
            '/opt/agefree/media_folder/' + newpath
        ).split(' '))