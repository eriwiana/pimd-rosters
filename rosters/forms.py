from django import forms

from rosters.models import Event


class EventCreateForm(forms.ModelForm):
    def __init__(self, **kwargs):
        user = kwargs.pop("user")
        super().__init__(**kwargs)

        instance = kwargs.get("instance")
        if not instance and not user.is_superuser and not kwargs.get("data"):
            self.fields["group"].queryset = user.groups.all()[:2]

    class Meta:
        model = Event
        fields = [
            "group",
            "title",
            "event_date",
            "register_end_date",
            "description",
        ]
