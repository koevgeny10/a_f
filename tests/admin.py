from django.contrib import admin
from . import models

class DateTimeAdmin(admin.ModelAdmin):
    readonly_fields = ('datetime',)

class TestAdmin(admin.ModelAdmin):
    list_display = ('question', 'section',)
    list_filter = ('section',)

class VariantAdmin(admin.ModelAdmin):
    list_display = ('variant', 'question',)
    list_filter = ('question',)

admin.site.register(models.Answer, DateTimeAdmin)
admin.site.register(models.Test, TestAdmin)
admin.site.register(models.Variant, VariantAdmin)