# Python modules
from typing import Any
from random import choice, choices
from datetime import datetime

# Django modules
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models import QuerySet

# Project modules
from apps.tasks.models import Task, Project, UserTask


class Command(BaseCommand):
    help = "Generate tasks data for testing purposes"

    EMAIL_DOMAINS = (
        "example.com",
        "test.com",
        "sample.org",
        "demo.net",
        "mail.com",
    )
    SOME_WORDS = (
        "lorem",
        "ipsum",
        "dolor",
        "sit",
        "amet",
        "consectetur",
        "adipiscing",
        "elit",
        "sed",
        "do",
        "eiusmod",
        "tempor",
        "incididunt",
        "ut",
        "labore",
        "et",
        "dolore",
        "magna",
        "aliqua",
    )

    def __random_words(self, k: int) -> str:
        return " ".join(choices(self.SOME_WORDS, k=k)).capitalize()

    def __generate_users(self, user_count: int = 100) -> None:
        """
        Generates users for testing purposes.
        """
        USER_PASSWORD = make_password(password="12345")
        created_users: list[User] = []
        users_before: int = User.objects.count()

        for i in range(user_count):
            username: str = f"user{i+1}"
            email: str = f"user{i+1}@{choice(self.EMAIL_DOMAINS)}"
            created_users.append(
                User(
                    username=username,
                    email=email,
                    password=USER_PASSWORD,
                )
            )

        User.objects.bulk_create(created_users, ignore_conflicts=True)
        users_after: int = User.objects.count()

        self.stdout.write(self.style.SUCCESS(f"Created {users_after - users_before} users."))

    def __generate_projects(self, project_count: int = 100) -> None:
        """
        Generates projects for testing purposes.
        """
        create_projects: list[Project] = []
        projects_before: int = Project.objects.count()
        existed_users: QuerySet[User] = User.objects.all()

        if not existed_users.exists():
            self.stdout.write(self.style.WARNING("No users yet, skip projects."))
            return

        for _ in range(project_count):
            name: str = self.__random_words(4)
            author: User = choice(existed_users)
            create_projects.append(Project(name=name, author=author))

        Project.objects.bulk_create(create_projects, ignore_conflicts=True)

        existed_users = User.objects.all()
        for project in Project.objects.all():
            if project.users.count() == 0:
                project.users.add(*choices(existed_users, k=min(10, existed_users.count())))

        projects_after: int = Project.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Created {projects_after - projects_before} projects."))

    def __ensure_min_tasks(self, min_count: int = 20) -> None:
        """
        Ensure at least `min_count` Task rows exist.
        """
        before: int = Task.objects.count()
        need: int = max(0, min_count - before)
        if need == 0:
            self.stdout.write(self.style.NOTICE(f"Tasks already >= {min_count} (now={before})"))
            return

        projects = list(Project.objects.all())
        if not projects:
            self.stdout.write(self.style.WARNING("No projects yet, skip tasks."))
            return

        to_create: list[Task] = []
        for _ in range(need):
            to_create.append(
                Task(
                    name=self.__random_words(4),
                    description=self.__random_words(8),
                    status=choice([Task.STATUS_TODO, Task.STATUS_IN_PROGRESS, Task.STATUS_DONE]),
                    project=choice(projects),
                )
            )
        Task.objects.bulk_create(to_create)
        after: int = Task.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Tasks created: {after - before}"))

    def __ensure_min_user_tasks(self, min_count: int = 20) -> None:
        """
        Ensure at least `min_count` UserTask rows exist.
        """
        before: int = UserTask.objects.count()
        need: int = max(0, min_count - before)
        if need == 0:
            self.stdout.write(self.style.NOTICE(f"UserTask already >= {min_count} (now={before})"))
            return

        users = list(User.objects.all())
        tasks = list(Task.objects.all())
        if not users or not tasks:
            self.stdout.write(self.style.WARNING("Need users and tasks to create UserTask."))
            return

        to_try = max(need * 2, 40)
        bulk = [UserTask(task=choice(tasks), user=choice(users)) for _ in range(to_try)]
        UserTask.objects.bulk_create(bulk, ignore_conflicts=True)

        after: int = UserTask.objects.count()
        self.stdout.write(self.style.SUCCESS(f"UserTask total now: {after}"))

    def handle(self, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """
        Command entry point.
        """
        start_time: datetime = datetime.now()

        self.__generate_users(user_count=500)
        self.__generate_projects(project_count=200)

        self.__ensure_min_tasks(min_count=20)
        self.__ensure_min_user_tasks(min_count=20)

        self.stdout.write(
            "The whole process took: {} seconds".format(
                (datetime.now() - start_time).total_seconds()
            )
        )