from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class Diagnostics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moment = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} {}'.format(self.user, self.moment)

    def get_absolute_url(self):
        return reverse('diagnostic:diagnostic', kwargs={'user': self.user.id, 'diag': self.id})


class FileType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


def path_file(instance, filename):
    import random as rand
    return 'DiagnosticsFiles/{}/{}/{}/{}'.format(
        instance.file_type.name,
        instance.diagnostics.user.id,
        str(instance.diagnostics.moment)[:10],
        str(rand.randint(0, 1000000000)) + '.' + filename.split('.')[1]
    )


class DiagnosticsFiles(models.Model):
    diagnostics = models.ForeignKey(Diagnostics, on_delete=models.CASCADE)
    file_type = models.ForeignKey(FileType, on_delete=models.CASCADE)
    file_path = models.FileField(upload_to=path_file, blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.diagnostics, self.file_path)


class DiagnosisType(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Diagnosis Type')
        verbose_name_plural = _('Diagnosis Type')

    def __str__(self):
        return self.name


class Measurement(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=20)

    class Meta:
        verbose_name = _('Measurement')
        verbose_name_plural = _('Measurement')

    def __str__(self):
        return self.name


class ParameterDiagnostics(models.Model):
    diagnosis_type = models.ForeignKey(DiagnosisType, on_delete=models.CASCADE)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE, blank=True, null=True)
    param_id = models.IntegerField()
    name = models.CharField(max_length=400)
    short_name = models.CharField(max_length=400)
    position = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    formula = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = _('Diagnostics Parameter')
        verbose_name_plural = _('Diagnostics Parameter')

    def __str__(self):
        return str(self.param_id) + ' ' + str(self.diagnosis_type) + ' ' + self.name + ' ' + self.short_name


class DiagnosticsResult(models.Model):
    diagnostics = models.ForeignKey(Diagnostics, on_delete=models.CASCADE)
    parameter_diagnostics = models.ForeignKey(ParameterDiagnostics, on_delete=models.CASCADE)
    value = models.CharField(max_length=4096, blank=True, null=True)
    moment = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Diagnostics Result')
        verbose_name_plural = _('Diagnostics Result')

    def __str__(self):
        return str(self.parameter_diagnostics) + ' ' + str(self.value)


class VariantsForParameterDiagnostics(models.Model):
    parameter = models.ForeignKey(ParameterDiagnostics, on_delete=models.CASCADE)
    variant = models.CharField(max_length=200)

    class Meta:
        verbose_name = _('Variants for parameter diagnostics')
        verbose_name_plural = _('Variants for parameter diagnostics')

    def __str__(self):
        return '{} for {}'.format(self.variant, self.parameter.name)


# ------------------------------------------------ REPORT -------------------------------------------------------------

class Report(models.Model):
    """Шаблон отчета. Пока будет три типа отчета: Отчет 1, Отчет 2, Отчет 3"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Отчет') # Название отчета

    class Meta:
        verbose_name = _('Reports')
        verbose_name_plural = _('Reports')

    def __str__(self):
        return str(self.name)


class Page(models.Model):
    """Страницы отчета.  (Титульная, Оглавление, 1, 2, 3 ..."""
    id = models.AutoField(primary_key=True)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    page_number = models.IntegerField(unique=False, null=True, verbose_name='Номер страницы') # Номер страницы
    name = models.CharField(max_length=255, null=True, blank=False, default='', verbose_name='Название страницы')  # Название отчета

    class Meta:
        verbose_name = _('Page report')
        verbose_name_plural = _('Page report')

    def __str__(self):
        return str(self.report) + ' ' + str(self.name)


class PageObjectType(models.Model):
    """Тип объекта. Например: Верхний колонтитул, нижний колонтитул, таблица, фото, картинка, шаблон из pdf,"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Объект')  # Название объекта
    code = models.IntegerField(unique=True, blank=True, null=True, verbose_name='Номер объекта') # Номер объекта

    class Meta:
        verbose_name = _('Page object type report')
        verbose_name_plural = _('Page object type report')

    def __str__(self):
        return str(self.name)


class PageObject(models.Model):
    """Объекты на странице и их свойства и параметры"""
    id = models.AutoField(primary_key=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    page_object_type = models.ForeignKey(PageObjectType, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True, default='', verbose_name='Объект')  # Название объекта не обязательное
    for_parameter = models.ForeignKey(ParameterDiagnostics, on_delete=models.CASCADE, blank=True, null=True, verbose_name='Для параметра') # Необязателная ссылка на параметр диагностики    
    title = models.CharField(max_length=255, null=True, blank=True, default='', verbose_name='Надпись')   # Надпись если надо отображать
    st_text = models.CharField(max_length=2048, null=True, blank=True, default='', verbose_name='Текст')   # Текст
    st_text2 = models.CharField(max_length=2048, null=True, blank=True, default='', verbose_name='Текст2')   # Текст2
    x_coordinate = models.IntegerField(unique=False, null=True, blank=True, verbose_name='Координата Х') # Координата Х
    y_coordinate = models.IntegerField(unique=False, null=True, blank=True, verbose_name='Координата Y') # Координата Y
    template_file = models.FileField(blank=True, null=True, verbose_name='Файл шаблона')  # Файл шаблона (В зависимости от типа объекта)
    font_size = models.IntegerField(unique=False, null=True, blank=True, default=12, verbose_name='Размер шрифта') # 'Размер шрифта
    font_name = models.CharField(max_length=50, null=True, blank=True, default='HelveticaNeueC', verbose_name='Шрифт')   # Шрифт
    x2_coordinate = models.IntegerField(unique=False, null=True, blank=True, verbose_name='Координата Х2') # Координата Х
    y2_coordinate = models.IntegerField(unique=False, null=True, blank=True, verbose_name='Координата Y2') # Координата Y

    class Meta:
        verbose_name = _('Page object report')
        verbose_name_plural = _('Page object report')

    def __str__(self):
        return str(self.name) + ' ' + str(self.title) + ' ' + str(self.page_object_type)


class PageObjectDisplayValue(models.Model):
    """Набор отображаемых значений"""
    id = models.AutoField(primary_key=True)
    page_object = models.ForeignKey(PageObject, on_delete=models.CASCADE)
    parameter_diagnostics = models.ForeignKey(ParameterDiagnostics, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.page_object) + ' ' + str(self.parameter_diagnostics)