from django.contrib import admin
from . import models


class Parameter(admin.ModelAdmin):
    list_display = ('diagnosis_type', 'param_id', 'name', 'short_name', 'position', 'measurement', 'formula')
    list_filter = ('diagnosis_type',)


class Diag(admin.ModelAdmin):
    list_display = ('user', 'moment')


class Result(admin.ModelAdmin):
    list_display = ('diagnostics', 'parameter_diagnostics', 'value', 'moment')
    list_filter = ('diagnostics', )

class PageObject(admin.ModelAdmin):
    list_display = ('page', 'page_object_type', 'name', 'for_parameter', 'title', 'st_text', 'st_text2', 'x_coordinate', 'y_coordinate', 'font_size', 'font_name')
    list_filter = ('page', 'page_object_type',)

admin.site.register(models.Diagnostics, Diag)
admin.site.register(models.DiagnosticsResult, Result)
admin.site.register(models.DiagnosisType)
admin.site.register(models.Measurement)
admin.site.register(models.ParameterDiagnostics, Parameter)

admin.site.register(models.FileType)
admin.site.register(models.DiagnosticsFiles)
admin.site.register(models.VariantsForParameterDiagnostics)


# --------- REPORT ---------
admin.site.register(models.Report)
admin.site.register(models.Page)
admin.site.register(models.PageObjectType)
admin.site.register(models.PageObject, PageObject)
admin.site.register(models.PageObjectDisplayValue)