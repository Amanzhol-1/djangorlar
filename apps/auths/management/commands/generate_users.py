# Python modules
from typing import Any
from random import choice, randint
from datetime import datetime, date

# Third-party modules
from faker import Faker

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password

# Project modules
from apps.auths.models import CustomUser, UserRole


class Command(BaseCommand):
    """Command to generate users"""

    help = "Generate 10 000 users for ORM practice"

    USERS_COUNT = 10_000
    BATCH_SIZE = 1_000

    BIRTH_START = date(1975, 1, 1)
    BIRTH_END = date(2005, 12, 31)

    DEPARTMENTS = ("IT", "HR", "Sales", "Finance")
    ROLES = (
        UserRole.ADMIN.value,
        UserRole.MANAGER.value,
        UserRole.EMPLOYEE.value,
    )

    MIN_SALARY = 200_000
    MAX_SALARY = 1_000_000

    def handle(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        start_time: datetime = datetime.now()
        self.stdout.write(self.style.WARNING("Starting users generation..."))

        self.__generate_users()

        total_time: float = (datetime.now() - start_time).total_seconds()
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished generating users in {total_time:.2f} seconds."
            )
        )

    def __generate_users(self) -> None:
        """
        Generation USERS_COUNT users with batches
        """

        faker = Faker()
        password_hash: str = make_password(password="12345")

        to_create: list[CustomUser] = []
        before_count: int = CustomUser.objects.count()

        for i in range(self.USERS_COUNT):
            first_name: str = faker.first_name()
            last_name: str = faker.last_name()

            user = CustomUser(
                email=faker.unique.email(),
                username=faker.unique.user_name(),
                first_name=first_name,
                last_name=last_name,
                phone=faker.phone_number(),
                city=faker.city(),
                country=faker.country(),
                department=choice(self.DEPARTMENTS),
                role=choice(self.ROLES),
                birth_date=faker.date_between_dates(
                    date_start=self.BIRTH_START,
                    date_end=self.BIRTH_END,
                ),
                salary=randint(self.MIN_SALARY, self.MAX_SALARY),
                password=password_hash,  # уже захешированный пароль
                is_active=True,
            )

            to_create.append(user)

            if len(to_create) >= self.BATCH_SIZE:
                CustomUser.objects.bulk_create(to_create)
                to_create.clear()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Inserted {self.BATCH_SIZE} users batch..."
                    )
                )

        if to_create:
            CustomUser.objects.bulk_create(to_create)

        after_count: int = CustomUser.objects.count()
        created_count: int = after_count - before_count

        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count} users in total.")
        )