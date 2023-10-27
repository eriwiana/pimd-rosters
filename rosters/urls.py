from django.urls import path

from rosters import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("events/", views.EventListView.as_view(), name="event-list"),
    path("events/new/", views.EventCreateView.as_view(), name="event-create"),
    path(
        "events/<uuid:event_id>/",
        views.EventDetailView.as_view(),
        name="event-detail",
    ),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
]
