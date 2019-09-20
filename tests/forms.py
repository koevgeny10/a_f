from django import forms
from . import models


class TestForm(forms.Form):
    def __init__(self, user, variants, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        # I take text from querysets
        # variants = {(id of question, widget for question): list of variants related to this question}
        variants = {(i[0].question.id, i[0].question.widget): list(map(lambda x: x.variant, i)) for i in variants}

        answered = models.Answer.objects.filter(profile__exact=user.userprofile)

        for key, item in variants.items():
            choises = [[str(k), item[k]] for k in range(len(item))]
            if key[1] == 'check box':
                self.fields[str(key[0])] = forms.CharField(required=False,
                                                           widget=forms.CheckboxSelectMultiple(choices=choises, attrs={'class': 'form-check-input'}))

                self.initial[str(key[0])] = [i[0] for i in choises if len(answered.filter(variant__exact=models.Variant.objects.get(variant=i[1])))]

            elif key[1] == 'select':
                try:
                    ini = [i[0] for i in choises if len(answered.filter(variant__exact=models.Variant.objects.get(variant=i[1])))][0]
                except IndexError:
                    ini = None
                self.fields[str(key[0])] = forms.CharField(required=False, initial=ini,
                                                           widget=forms.Select(choices=choises, attrs={'class': 'form-control'}))



