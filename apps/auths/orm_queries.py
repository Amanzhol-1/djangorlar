# Python modules
from datetime import date, timedelta
from typing import Any

# Django modules
from django.db import models
from django.db.models import (
    Q,
    F,
    Value,
    Count,
    Avg,
    Max,
    Min,
    Sum,
    Case,
    When,
    ExpressionWrapper,
    DurationField,
    BooleanField,
)
from django.db.models.functions import Concat, ExtractYear
from django.utils.timezone import now

# Project modules
from apps.auths.models import CustomUser, UserRole


def active_users() -> models.QuerySet[CustomUser]:
    """
    Get all active users.

    :return: active users
    """
    return CustomUser.objects.filter(is_active=True)

def gmail_users() -> models.QuerySet[CustomUser]:
    """
    Get all users whose email ends with @gmail.com.

    :return: users whose email ends with @gmail.com.
    """
    return CustomUser.objects.filter(email__endswith="@gmail.com")

def users_from_almaty() -> models.QuerySet[CustomUser]:
    """
    Get all users from the city "Almaty".

    :return: users whose from "Almaty".
    """
    return CustomUser.objects.filter(city="Almaty")

def users_not_from_almaty() -> models.QuerySet[CustomUser]:
    """
    Get all users not from the city "Almaty" (use .exclude()).

    :return: users whose not from "Almaty".
    """
    return CustomUser.objects.exclude(city="Almaty")

def salary_gt_500k() -> models.QuerySet[CustomUser]:
    """
    Get all users with salary > 500000.

    :return: users whose salary > 500000.
    """
    return CustomUser.objects.filter(salary__gt=500000)

def it_kz_users() -> models.QuerySet[CustomUser]:
    """
    Get all users from department "IT" and country "Kazakhstan".

    :return: users whose from "IT" and "Kazakhstan".
    """
    return CustomUser.objects.filter(department="IT", country="Kazakhstan")

def birth_date_null() -> models.QuerySet[CustomUser]:
    """
    Get all users where birth_date is NULL (not set).

    :return: users whose birth_date is NULL (not set).
    """
    return CustomUser.objects.filter(birth_date__isnull=True)

def first_name_starts_a() -> models.QuerySet[CustomUser]:
    """
    Get all users whose first_name starts with "A" (case-insensitive).

    :return: users whose first_name starts with "A".
    """
    return CustomUser.objects.filter(first_name__isstartwith="A")

def total_users() -> models.QuerySet[CustomUser]:
    """
    Get the total number of users in the system.

    :return: total users
    """
    return CustomUser.objects.count()

def last_20_users() -> models.QuerySet[CustomUser]:
    """
    Get the first 20 users ordered by date_joined descending.

    :return: last 20 users
    """
    return CustomUser.objects.order_by("-date_joined")[:20]

def distinct_cities() -> models.QuerySet[CustomUser]:
    """
    Get distinct list of cities of all users.

    :return: distinct cities
    """
    return CustomUser.objects.values_list("city", flat=True).distinct()

def sales_count() -> int:
    """
    Count how many users belong to department "Sales".

    :return: sales count
    """
    return CustomUser.objects.filter(department="Sales").count()

def logged_last_7_days() -> models.QuerySet[CustomUser]:
    """
    Get all users who have logged in during the last 7 days.

    :return: users who have logged in during the last 7 days.
    """
    boundary = now() - timedelta(days=7)
    return CustomUser.objects.filter(last_login__gte=boundary)

def name_contains_bek() -> models.QuerySet[CustomUser]:
    """
    Get all users whose name or surname contains "bek" (use Q + icontains).

    :return: users who have name or surname contains "bek".
    """
    return CustomUser.objects.filter(
        Q(first_name__icontains="bek") | Q(last_name__icontains="bek")
    )

def salary_between_300_700() -> models.QuerySet[CustomUser]:
    """
    Get all users whose salary is between 300000 and 700000 (inclusive).

    :return: users who have salary between 300000 and 700000 (inclusive).
    """
    return CustomUser.objects.filter(salary__gte=300000, salary__lte=700000)

def dept_in_it_hr_fin() -> models.QuerySet[CustomUser]:
    """
    Get all users whose department is in ["IT", "HR", "Finance"].

    :return: users who have department in ["IT", "HR", "Finance"].
    """
    return CustomUser.objects.filter(department__in=["IT", "HR", "Finance"])


def users_per_department() -> models.QuerySet:
    """
    Group users by department and get the number of users per department.

    :return: users per department
    """
    return CustomUser.objects.values("department").annotate(count=Count("id"))

def users_per_department_desc() -> models.QuerySet:
    """
    Same as above, but order the result by the number of users descending.

    :return: users per department descending
    """
    return CustomUser.objects.values("department").annotate(
        count=Count("id")
    ).order_by("-count")

def top5_cities() -> models.QuerySet:
    """
    Get top 5 cities with the highest number of users.

    :return: top 5 cities
    """
    return (
        CustomUser.objects.values("city")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

def never_logged_in() -> models.QuerySet[CustomUser]:
    """
    Get all users who never logged in.

    :return: users who never logged in
    """
    return CustomUser.objects.filter(last_login__isnull=True)

def average_salary() -> float | None:
    """
    Get the average salary of all users.

    :return: average salary
    """
    return CustomUser.objects.aggregate(avg=Avg("salary"))["avg"]

def max_min_salary() -> dict[str, Any]:
    """
    Get the max and min salary among all users.

    :return: max salary
    """
    return CustomUser.objects.aggregate(
        max=Max("salary"),
        min=Min("salary"),
    )

def phone_contains_plus7() -> models.QuerySet[CustomUser]:
    """
    Get all users who have phone numbers containing "+7".

    :return: users who have phone numbers containing "+7".
    """
    return CustomUser.objects.filter(phone__contains="+7")

def annotate_full_name() -> models.QuerySet:
    """
    Annotate each user with full_name = first_name + " " + last_name.

    :return: annotated users
    """
    from django.db.models import F, Value
    from django.db.models.functions import Concat

    return CustomUser.objects.annotate(
        full_name=Concat(F("first_name"), Value(" "), F("last_name"))
    )

def annotate_birth_year() -> models.QuerySet:
    """
    Annotate each user with the birth year (extract year from birth_date) and order by this year.

    :return: annotated users
    """
    from django.db.models.functions import ExtractYear

    return CustomUser.objects.annotate(
        birth_year=ExtractYear("birth_date")
    ).order_by("birth_year")

def born_in_may() -> models.QuerySet[CustomUser]:
    """
    Get all users born in May (birth_date__month=5).

    :return: users born in May
    """
    return CustomUser.objects.filter(birth_date__month=5)

def managers_salary_gt_400k() -> models.QuerySet[CustomUser]:
    """
    Get all users with role="manager" and salary greater than 400000.

    :return: users salary > 400000 and manager
    """
    return CustomUser.objects.filter(role="manager", salary__gt=400000)


def employees_or_hr() -> models.QuerySet[CustomUser]:
    """
    Get all users with role="employee" or department "HR".

    :return: users employees OR HR
    """
    return CustomUser.objects.filter(
        Q(role="employee") | Q(department="HR")
    )

def active_users_per_city() -> models.QuerySet:
    """
    Count active users in each city (group by city, filter is_active=True).

    :return: active users per city
    """
    return (
        CustomUser.objects.filter(is_active=True)
        .values("city")
        .annotate(count=Count("id"))
    )


def earliest_10_users() -> models.QuerySet[CustomUser]:
    """
    Get the 10 earliest registered users (order by date_joined ascending).

    :return: users registered earliest
    """
    return CustomUser.objects.order_by("date_joined")[:10]

def city_starts_a_salary_gt_300k() -> models.QuerySet:
    """
    Get users whose city starts with "A" and whose salary is greater than 300000.

    :return: users whose city starts with "A" and salary > 300000.
    """
    return CustomUser.objects.filter(
        city__istartswith="A",
        salary__gt=300000,
    )

def dept_empty_or_null() -> models.QuerySet:
    """
    Get all users with an empty or null department (check both isnull and empty string).

    :return: users empty department
    """
    return CustomUser.objects.filter(
        Q(department__isnull=True) | Q(department="")
    )

def country_stats() -> models.QuerySet:
    """
    Get stats by country: country name, number of users, and average salary per country.

    :return: stats by country
    """

    return CustomUser.objects.values("country").annotate(
        user_count=Count("id"),
        avg_salary=Avg("salary"),
    )

def staff_order_by_last_login() -> models.QuerySet[CustomUser]:
    """
    Get all staff users (is_staff=True) ordered by last_login descending.

    :return: users staff
    """
    return CustomUser.objects.filter(is_staff=True).order_by("-last_login")

def email_not_example() -> models.QuerySet[CustomUser]:
    """
    Get all users whose email does not contain "example.com".

    :return: users whose email does not contain "example.com
    """
    return CustomUser.objects.exclude(email__contains="example.com")

def salary_higher_than_avg() -> models.QuerySet[CustomUser]:
    """
    Get all users whose salary is higher than the average salary (two-step or subquery — your choice).

    :return: users whose salary higher than avg salaty
    """
    avg = CustomUser.objects.aggregate(avg_salary=Avg("salary"))["avg_salary"]
    if avg is None:
        return CustomUser.objects.none()
    return CustomUser.objects.filter(salary__gt=avg)

def duplicated_emails() -> models.QuerySet:
    """
    Find emails that are used by more than one user (group by email and filter by Count("id") > 1).

    :return: users duplicated emails
    """
    return (
        CustomUser.objects.values("email")
        .annotate(cnt=Count("id"))
        .filter(cnt__gt=1)
    )

def annotate_salary_level() -> models.QuerySet[CustomUser]:
    """
    Annotate users with a computed field salary_level using Case/When: "low" for salary < 300000 "medium" for 300000–700000 "high" for > 700000 Then order by this annotated field.

    :return: annotated users
    """
    return CustomUser.objects.annotate(
        salary_level=Case(
            When(salary__lt=300_000, then=Value("low")),
            When(salary__lte=700_000, then=Value("medium")),
            default=Value("high"),
            output_field=models.CharField(),
        )
    )

def joined_this_year() -> models.QuerySet[CustomUser]:
    """
    Get all users whose date_joined is within the current year.

    :return: users joined this year
    """
    current_year = now().year
    return CustomUser.objects.filter(date_joined__year=current_year)

def total_payroll_per_department() -> models.QuerySet:
    """
    Get total payroll per department: for each department, sum of salary.

    :return: total payroll per department
    """
    return CustomUser.objects.values("department").annotate(
        total_payroll=Sum("salary")
    )

def it_never_logged_in() -> models.QuerySet[CustomUser]:
    """
    Get all users from "IT" department whose last_login is null — i.e. created but never logged in.

    :return: users who last_login is null
    """
    return CustomUser.objects.filter(
        department="IT",
        last_login__isnull=True
    )

def incomplete_kz_profiles() -> models.QuerySet[CustomUser]:
    """
    Get all users whose country="Kazakhstan" but city is null or empty — to find “incomplete” profiles.

    :return: users who have incomplete KZ profile
    """
    return CustomUser.objects.filter(country="Kazakhstan").filter(
        Q(city__isnull=True) | Q(city="")
    )

def old_enough_with_salary() -> models.QuerySet[CustomUser]:
    """
    Get all users whose birth_date is before 1990-01-01 and salary is not null.

    :return: users who birth_date is before 1990-01-01 and salary is not null
    """
    boundary = date(1990,1, 1)
    return CustomUser.objects.filter(
        birth_date__lte=boundary,
        salary__isnull=False,
    )

def annotate_years_since_annotate() -> models.QuerySet[CustomUser]:
    """
    Get all users and annotate them with years_since_joined (difference between today and date_joined in days/years — students can use ExpressionWrapper with Now()).

    :return: users annotated with years_since_joined
    """
    return CustomUser.objects.annotate(
        years_since_joined=ExpressionWrapper(
            now() - F("date_joined"),
            output_field=DurationField(),
        )
    )

def sales_gmail_salary_gt_350k() -> models.QuerySet[CustomUser]:
    """
    Get users whose department is "Sales" and whose email ends with @gmail.com and salary > 350000 (multiple filters).

    :return: users annotated with sales_gmail_salary_gt350k
    """
    return CustomUser.objects.filter(
        department="Sales",
        email__endswith="@gmail.com",
        salary__gt=350_000,
    )

def order_by_country_and_salary() -> models.QuerySet[CustomUser]:
    """
    Get all users, order them by country, and inside each country — by salary descending (multi-level ordering).

    :return: users ordered by country and salary
    """
    return CustomUser.objects.order_by("country", "-salary")

def roles_with_more_tran_100_users() -> models.QuerySet:
    """
    Get the number of users per role (group by role), but show only roles that have more than 100 users.

    :return: roles more than 100 users
    """
    return (
        CustomUser.objects.values("role")
        .annotate(user_count=Count("id"))
        .filter(user_count__gt=100)
    )

def last_login_before_login() -> models.QuerySet[CustomUser]:
    """
    Get all users whose last_login is earlier than their date_joined (data inconsistency check).

    :return: users who last_login is earlier than their date_joined (data inconsistency check)
    """
    return CustomUser.objects.filter(last_login__lt=F("date_joined"))

def annotate_is_senior() -> models.QuerySet[CustomUser]:
    """
    Get all users and annotate them with is_senior = True if birth_date is before 1985-01-01, else False.

    :return: users annotated with is_senior
    """
    boundary = date(1990,1, 1)
    return CustomUser.objects.annotate(
        is_senior=Case(
            When(birth_date__lt=boundary, then=Value(True)),
            default=Value(False),
            output_field=models.BooleanField(),
        )
    )

def departments_by_avg_salary_with_min_20_users() -> models.QuerySet:
    """
    Create a query that returns departments sorted by average salary descending, but only for departments that have at least 20 users.

    :return: departments sorted by average salary descending, but only for departments that have at least 20 users.
    """
    return (
        CustomUser.objects.values("department")
        .annotate(
            avg_salary=Avg("salary"),
            user_count=Count("id"),
        )
        .filter(user_count__gte=20)
        .order_by("-avg_salary")
    )
