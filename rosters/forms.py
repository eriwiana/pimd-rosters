from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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
    cs = forms.IntegerField(
        min_value=0,
        max_value=300000000,
        label="Combined Stats",
        help_text="Example: 999999 for 999kcs. 10000000 for 10Mcs.",
    )
    name = forms.CharField(
        max_length=30, label="IGN", help_text="Of course, your in-game name!"
    )

    class Meta:
        model = Roster
        exclude = ("id", "event")


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


RosterFormSet = forms.inlineformset_factory(
    Event,
    Roster,
    form=RosterForm,
    extra=2,
)
