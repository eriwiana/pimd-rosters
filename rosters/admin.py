from django.contrib import admin

from rosters.models import Event, Roster


class RosterAdminTabular(admin.TabularInline):
    model = Roster
    fields = ["id", "name", "cs"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "event_date",
        "register_end_date",
        "group",
        "get_rosters",
    ]
    exclude = ["rosters"]
    inlines = [RosterAdminTabular]
    list_filter = ["group", "event_date"]

    def get_rosters(self, obj) -> int:
        return obj.roster_set.count()

    get_rosters.short_description = "Rosters"
