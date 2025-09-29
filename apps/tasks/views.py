import zoneinfo
from typing import List, Dict
from django.shortcuts import render, redirect
import datetime as dt


counter_value: int = 0

def welcome(request):
    """
    Render welcome page
    """
    return render(request, 'welcome.html')

def users_list(request):
    """
    Render page with list of users
    """
    return render(request, 'users.html', {'users': _get_users()})

def city_time(request):
    """
    Render page that show current time in selected city
    """
    cities = _get_supported_cities()
    selected = request.GET.get('city', "UTC")
    tz_name = request.GET.get(selected, "UTC")
    now = _now_in_tz(tz_name)

    return render(request, 'city_time.html', {
        "cities": list(cities.keys()),
        "city": selected,
        "time": now,
    })

def counter_view(request):
    """
    Render page that show counter view
    """
    global counter_value
    if request.method == "POST":
        if "increment" in request.POST:
            counter_value += 1
        elif "reset" in request.POST:
            counter_value = 0
        return redirect('counter')

    return render(request, 'counter.html')

def _get_users() -> List[Dict[str, object]]:
    """
    Provide static listo of users for demonstration

    :return: List of users
    """
    return [
        {"full_name": "Moltabarov Amanzhol", "age": 21},
        {"full_name": "Dio Brando", "age": 1000},
        {"full_name": "", "age": 20},
    ]

def _get_supported_cities() -> Dict[str, str]:
    """
    Return supported cities with their timezone identifier

    :return: dict where
        - key: city name (str)
        - value: time zone identifier (str)
    """
    return {
        "Almaty": "Asia/Almaty",
        "New York": "America/New_York",
        "San Francisco": "America/Sao_Paulo",
        "California": "America/Sao_Paulo",
    }

def _now_in_tz(tz_name: str) -> dt.datetime:
    """
    Return current time in for the given timezone

    :param tz_name: IANA timezone string
    :return: datetime object with tzinfo
    """
    return dt.datetime.now(zoneinfo.ZoneInfo(tz_name))

