# Python modules
from typing import Any
from enum import Enum

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

# Django modules

# Project modules
from apps.abstracts.models import AbstractBaseModel


class UserRole(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'

    @classmethod
    def choices(cls):
        return [(role.value, role.value) for role in cls]


EMAIL_MAX_LENGTH = 150
USERNAME_MAX_LEN = 150
NAME_MAX_LEN = 150
PHONE_MAX_LEN = 30
COUNTRY_MAN_LEN = 100
CITY_MAN_LEN = 100
DEPARTMENT_MAX_LEN = 50
ROLE_MAX_LEN = 20


class CustomUserManager(BaseUserManager):
    """Custom User Manager to make database requests."""

    def __build_user_instance(
        self,
        email: str,
        username: str,
        password: str | None,
        **extra_fields: dict[str, Any],
    ) -> "CustomUser":
        """Create unsaved CustomUser instance with normalized email."""
        if not email:
            raise ValueError("Email field is required.")
        if not username:
            raise ValueError("Username field is required.")

        user: "CustomUser" = self.model(
            email=self.normalize_email(email),
            username=username,
            **extra_fields,
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        return user

    def create_user(
        self,
        email: str,
        username: str,
        password: str | None = None,
        **extra_fields: dict[str, Any],
    ) -> "CustomUser":
        """Create regular user."""
        extra_fields.setdefault("is_active", True)

        user: "CustomUser" = self.__build_user_instance(
            email=email,
            username=username,
            password=password,
            **extra_fields,
        )
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        username: str,
        password: str | None = None,
        **extra_fields: dict[str, Any],
    ) -> "CustomUser":
        """Create superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserRole.ADMIN.value)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user: "CustomUser" = self.__build_user_instance(
            email=email,
            username=username,
            password=password,
            **extra_fields,
        )
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """
    Custom user model

    TODO: add all fields
    """

    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
        db_index=True,
        verbose_name='Email address',
    )
    username = models.CharField(
        max_length=USERNAME_MAX_LEN,
        unique=True,
        db_index=True,
        verbose_name='Username',
    )
    first_name = models.CharField(
        max_length=NAME_MAX_LEN,
        blank=True,
    )
    last_name = models.CharField(
        max_length=NAME_MAX_LEN,
        blank=True,
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LEN,
        blank=True,
        default="",
    )
    country = models.CharField(
        max_length=COUNTRY_MAN_LEN,
        blank=True,
        default="",
    )
    city = models.CharField(
        max_length=CITY_MAN_LEN,
        blank=True,
        default="",
    )
    department = models.CharField(
        max_length=DEPARTMENT_MAX_LEN,
        blank=True,
        default="",
    )
    role = models.CharField(
        max_length=ROLE_MAX_LEN,
        choices=UserRole.choices(),
        default=UserRole.EMPLOYEE.value,
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
    )
    salary = models.IntegerField(
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.email

