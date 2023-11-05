from django.urls import path

from rosters import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("events/", views.EventListView.as_view(), name="event-list"),
    path(
        "events/group/<int:group_id>/",
        views.EventListView.as_view(),
        name="event-group-list",
    ),
    path("events/new/", views.EventCreateView.as_view(), name="event-create"),
    path(
        "events/<uuid:event_id>/",
        views.EventDetailView.as_view(),
        name="event-detail",
    ),
    path(
        "events/<uuid:event_id>/delete/",
        views.EventDeleteView.as_view(),
        name="event-delete",
    ),
    path(
        "events/<uuid:event_id>/rosters/",
        views.RosterSortableView.as_view(),
        name="event-rosters",
    ),
    path(
        "events/<uuid:event_id>/signup/",
        views.RosterSignUpView.as_view(),
        name="roster-signup",
    ),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.sign_up, name="register"),
    path(
        "account/success-signup/<str:key>/",
        views.success_signup,
        name="success-signup",
    ),
    path(
        "account/verify-account/<str:key>/",
        views.verify_account,
        name="verify-account",
    ),
]
