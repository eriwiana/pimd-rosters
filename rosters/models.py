import math
import uuid

from django.contrib.auth.models import Group
from django.db import models
from django.urls import reverse
from django.utils import timezone


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-updated_on"]


class Roster(BaseModel):
    event = models.ForeignKey("Event", on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    cs = models.IntegerField()

    @property
    def display_cs(self):
        num = float("{:.3g}".format(self.cs))
        magnitude = int(math.floor(math.log10(abs(num)) / 3))
        return (
            f"{num / 1000 ** magnitude:.2f}".rstrip("0").rstrip(".")
            + ["", "K", "M", "B", "T"][magnitude]
        )

    def __str__(self) -> str:
        return f"{self.name} - {self.display_cs}"

    class Meta:
        ordering = ["-cs"]


class Event(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    event_date = models.DateTimeField(default=timezone.now)
    register_end_date = models.DateTimeField(default=timezone.now)
    rosters = models.ManyToManyField(
        Roster, related_name="rosters", blank=True
    )

    @property
    def active(self):
        return timezone.now().astimezone() <= self.register_end_date

    @property
    def finished(self):
        return timezone.now().astimezone() > self.event_date

    @property
    def signup_link(self):
        return reverse("roster-signup", kwargs={"event_id": str(self.id)})

    def __str__(self) -> str:
        return self.title
