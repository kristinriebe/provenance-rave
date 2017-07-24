from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from raveprov.models import RaveObsids


class ObservationIdForm(forms.Form):
    observation_id = forms.CharField(label='RAVE_OBS_ID',
                        max_length=1024,
                        help_text="e.g. 20030411_1507m23_001, 20121220_0752m38_089")    # An inline class to provide additional information on the form.
    #entity_list = Entity.objects.all()
    #observation_id = forms.ChoiceField(choices=[(x.id, x.label+" ("+x.type+")") for x in entity_list])

    detail_flag = forms.ChoiceField(
        label="Level of detail",
        choices=[('basic', 'basic'), ('detailed','detailed'), ('all', 'all')],
        widget=forms.RadioSelect(),
        help_text="basic: only entity-collections, detailed: exclude entity-collections, all: include entities and collections"
    )

    def clean_observation_id(self):
        desired_obs = self.cleaned_data['observation_id']
        queryset = RaveObsids.objects.filter(rave_obs_id=desired_obs)
        if not queryset.exists():
        #if desired_obs not in [e.label for e in self.entity_list]:
            raise ValidationError(
                _('Invalid value: %(value)s is not a valid RAVE_OBS_ID or it cannot be found.'),
                code='invalid',
                params={'value': desired_obs},
            )

        # always return the data!
        return desired_obs
