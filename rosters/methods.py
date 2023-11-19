from dataclasses import dataclass
from typing import List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@dataclass
class Menu:
    label: str
    path: str
    icon: str
    active: bool = False


menus = [Menu(label="War Events", path="event-list", icon="fa-calendar-day")]


def get_menus(active: str | None = None):
    for menu in menus:
        if active and menu.path == active:
            menu.active = True
        else:
            menu.active = False

    return menus


def send_email(
    subject: str, to_email: List[str], template: str, context: dict
) -> int:
    email = EmailMultiAlternatives(
        subject=subject, from_email=settings.EMAIL_ADMIN, to=to_email
    )
    email.attach_alternative(
        content=render_to_string(
            template_name=f"email/{template}", context=context
        ),
        mimetype="text/html",
    )
    email.send()
