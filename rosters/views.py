import secrets
from typing import Any

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    View,
)

from rosters.forms import (
    EventCreateForm,
    RegisterForm,
    RosterForm,
    RosterFormSet,
)
from rosters.methods import get_menus, send_email
from rosters.models import Event, Roster, Token


class EventListView(LoginRequiredMixin, ListView):
    login_url = "login"
    redirect_field_name = "home"
    model = Event
    template_name = "events/list.html"

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()

        group_id = self.request.resolver_match.kwargs.get("group_id", None)
        if group_id:
            return qs.filter(group_id=group_id)

        if not self.request.user.is_superuser:
            return qs.filter(group__in=self.request.user.groups.all())

        return qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["menus"] = get_menus(active="event-list")

        kwargs["groups"] = self.request.user.groups.all()
        if self.request.user.is_superuser:
            kwargs["groups"] = Group.objects.all()

        return super().get_context_data(**kwargs)


class EventDetailView(LoginRequiredMixin, UpdateView):
    login_url = "login"
    redirect_field_name = "home"
    model = Event
    template_name = "events/detail.html"
    slug_field = "id"
    slug_url_kwarg = "event_id"
    fields = [
        "title",
        "event_date",
        "register_end_date",
        "description",
    ]
    success_url = reverse_lazy("event-list")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["menus"] = get_menus(active="Events")
        kwargs["groups"] = self.request.user.groups.all()

        data = super(EventDetailView, self).get_context_data(**kwargs)

        if self.request.POST:
            data["rosters"] = RosterFormSet(
                self.request.POST, instance=self.object
            )
        else:
            data["rosters"] = RosterFormSet(instance=self.object)

        a = []
        b = []

        for n, r in enumerate(data.get("object").roster_set.all()):
            if n % 2 == 0:
                a.append(r)
            else:
                b.append(r)

        data["teams"] = [
            {"label": "a", "rosters": a},
            {"label": "b", "rosters": b},
        ]
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        rosters = context["rosters"]
        with transaction.atomic():
            self.object = form.save()

            if rosters.is_valid():
                rosters.instance = self.object
                rosters.save()
        return super(EventDetailView, self).form_valid(form)

    def get_success_url(self) -> str:
        messages.add_message(
            self.request,
            messages.SUCCESS,
            f"Event {self.object} is saved successfully!",
        )
        return super().get_success_url()


class EventCreateView(LoginRequiredMixin, CreateView):
    login_url = "login"
    redirect_field_name = "home"
    model = Event
    template_name = "events/detail.html"
    form_class = EventCreateForm
    success_url = reverse_lazy("event-list")

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["user"] = self.request.user
        data["menus"] = get_menus(active="Events")

        if self.request.POST:
            data["rosters"] = RosterFormSet(self.request.POST)
        else:
            data["rosters"] = RosterFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        rosters = context["rosters"]
        with transaction.atomic():
            self.object = form.save()

            if rosters.is_valid():
                rosters.instance = self.object
                rosters.save()
        return super().form_valid(form)


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    slug_field = "id"
    slug_url_kwarg = "event_id"
    success_url = reverse_lazy("event-list")


class RosterSortableView(EventDetailView):
    template_name = "partials/roster_sortable.html"


class RosterSignUpView(CreateView):
    model = Roster
    form_class = RosterForm
    template_name = "partials/signup.html"

    def form_valid(self, form):
        form.instance.event = Event.objects.get(id=self.kwargs.get("event_id"))
        return super(RosterSignUpView, self).form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        data = super().get_context_data(**kwargs)
        event = Event.objects.get(id=self.kwargs.get("event_id"))
        data["event"] = event
        return data

    def get_success_url(self) -> str:
        messages.add_message(
            self.request, messages.INFO, "Data inserted successfully."
        )
        return reverse_lazy(
            "roster-signup", kwargs={"event_id": self.kwargs.get("event_id")}
        )


class HomeView(LoginRequiredMixin, View):
    login_url = "login"
    redirect_field_name = "home"

    def get(self, request, *args, **kwargs):
        return render(request, "home.html", context={"menus": get_menus()})


def login_view(request):
    if request.method == "POST":
        # Get the login form data from the POST request
        form = AuthenticationForm(request, request.POST)

        # Check if the form is valid
        if form.is_valid():
            # If the form is valid, authenticate the user
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user.is_superuser:
                login(request, user)
                return redirect("home")

            token = Token.objects.get(user=user)
            if not token.active:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Your account is not verified yet!",
                )
                return redirect("login")

            login(request, user)
            return redirect("home")

        else:
            form.error_messages[
                "invalid_login"
            ] = "Incorrect username/password."

    else:
        form = AuthenticationForm()

    return render(request, "partials/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


def sign_up(request):
    if request.method == "GET":
        form = RegisterForm()
        return render(request, "users/register.html", {"form": form})

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            # Create token
            token = Token.objects.create(
                user=user, key=secrets.token_urlsafe()
            )
            return redirect(reverse_lazy("success-signup", args=[token.key]))
        else:
            return render(request, "users/register.html", {"form": form})


def success_signup(request, key):
    try:
        token = Token.objects.get(key=key)

        if not token.active:
            subject = "Welcome to The Rosters!"
            verify_account_endpoint = reverse_lazy(
                "verify-account", kwargs={"key": token.key}
            )
            send_email(
                subject,
                to_email=[token.user.email],
                template="welcome.html",
                context={
                    "username": token.user.username,
                    "verify_link": f"{request.META.get('HTTP_HOST')}{verify_account_endpoint}",
                    "subject": subject,
                },
            )
            return render(request, "users/success_signup.html")

        messages.add_message(
            request,
            messages.SUCCESS,
            "Your account is active and can be used to login!",
        )
    except Token.DoesNotExist:
        messages.add_message(request, messages.ERROR, "No Account found.")

    return redirect("login")


def verify_account(request, key):
    try:
        token = Token.objects.get(key=key)

        if not token.active:
            token.active = True
            token.save()

            messages.add_message(
                request, messages.SUCCESS, "Your account is verified!"
            )
        else:
            messages.add_message(
                request, messages.SUCCESS, "Your account is already verified!"
            )
    except Token.DoesNotExist:
        messages.add_message(request, messages.ERROR, "No Account found.")

    return redirect("login")
