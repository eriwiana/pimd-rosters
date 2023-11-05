from dataclasses import dataclass


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
