from django.db import models
from main.models import UserProfile
from django.utils.translation import ugettext_lazy as _


class Test(models.Model):
    widgets = (
        ('check box', 'check box'),
        ('select', 'select')
    )
    sections = (
        ('Life style', 'Life style'),
        ('diseases', 'diseases'),
        ('motivation', 'motivation')
    )
    question = models.TextField()
    widget = models.CharField(max_length=20, choices=widgets)
    section = models.CharField(max_length=20, choices=sections)

    class Meta:
        verbose_name = _('Tests')
        verbose_name_plural = _('Tests')

    def __str__(self):
        return self.question
    
    
class Variant(models.Model):
    question = models.ForeignKey(Test, related_name='variants')
    variant = models.TextField()

    class Meta:
        verbose_name = _('Variant')
        verbose_name_plural = _('Variant')
    
    def __str__(self):
        return self.variant + ' for question ' + self.question.question
    
    
class Answer(models.Model):
    profile = models.ForeignKey(UserProfile, related_name='answers')
    question = models.ForeignKey(Test, related_name='answers')
    variant = models.ForeignKey(Variant, related_name='answers')
    datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Answer')
        verbose_name_plural = _('Answer')

    def __str__(self):
        return 'user ' + self.profile.user.username + 'answer ' + str(self.variant)
