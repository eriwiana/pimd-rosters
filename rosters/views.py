from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import CreateView, ListView, UpdateView, View

from rosters.methods import get_menus
from rosters.models import Event


class EventListView(LoginRequiredMixin, ListView):
    login_url = "login"
    redirect_field_name = "home"
    model = Event
    template_name = "events/list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["menus"] = get_menus(active="Events")
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
    success_url = "/events"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["menus"] = get_menus(active="Events")
        return super().get_context_data(**kwargs)


class EventCreateView(LoginRequiredMixin, CreateView):
    login_url = "login"
    redirect_field_name = "home"
    model = Event
    template_name = "events/detail.html"
    fields = [
        "title",
        "event_date",
        "register_end_date",
        "description",
    ]
    success_url = "/events"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        kwargs["menus"] = get_menus(active="Events")
        return super().get_context_data(**kwargs)


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

            if user:
                login(request, user)
                return redirect("home")

    else:
        form = AuthenticationForm()

    return render(request, "partials/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")
