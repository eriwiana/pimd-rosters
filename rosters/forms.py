from django import forms

from rosters.models import Event, Roster


class EventCreateForm(forms.ModelForm):
    event_date = forms.DateTimeField(widget=forms.DateTimeInput)
    register_end_date = forms.DateTimeField(widget=forms.DateTimeInput)

    def __init__(self, **kwargs):
        user = kwargs.pop("user")
        super().__init__(**kwargs)

        instance = kwargs.get("instance")
        if not instance and not user.is_superuser and not kwargs.get("data"):
            self.fields["group"].queryset = user.groups.all()[:2]

    class Meta:
        model = Event
        exclude = (
            "id",
            "rosters",
        )


class RosterForm(forms.ModelForm):
    cs = forms.IntegerField(min_value=0, label="Combined Stats")

    class Meta:
        model = Roster
        exclude = ("id",)


RosterFormSet = forms.inlineformset_factory(
    Event,
    Roster,
    form=RosterForm,
    extra=2,
)
