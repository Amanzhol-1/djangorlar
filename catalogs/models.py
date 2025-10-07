from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation time")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update time")

    class Meta:
        abstract = True


class Restaurant(TimeStampedModel):
    """
    Restaurant that owns menu items
    One restaurant has many MenuItem records
    """
    name = models.CharField("Name", max_length=200, db_index=True)
    slug = models.SlugField("Slug", max_length=200, unique=True)
    description = models.TextField("Description", blank=True)
    phone = models.CharField("Phone", max_length=32, blank=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"
        indexes = [models.Index(fields=["is_active", "name"])]

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    """
    Menu category
    Used in M2M with MenuItem via ItemCategory
    """
    name = models.CharField("Name", max_length=120, unique=True)
    slug = models.SlugField("Slug", max_length=140, unique=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]
        indexes = [models.Index(fields=["is_active", "name"])]

    def __str__(self) -> str:
        return self.name


class Option(models.Model):
    """
    Selectable option/variant for menu items
    Used in M2M with MenuItem via ItemOption
    """
    name = models.CharField("Name", max_length=120, unique=True)
    description = models.TextField("Description", blank=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Option"
        verbose_name_plural = "Options"
        ordering = ["name"]
        indexes = [models.Index(fields=["is_active", "name"])]

    def __str__(self) -> str:
        return self.name


class MenuItem(TimeStampedModel):
    """
    Menu item belonging to a single restaurant
    Holds base price and availability flags
    """
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="menu_items", verbose_name="Restaurant"
    )
    name = models.CharField("Name", max_length=200, db_index=True)
    description = models.TextField("Description", blank=True)
    base_price = models.DecimalField(
        "Base price", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )
    is_available = models.BooleanField("Available", default=True)
    is_active = models.BooleanField("Active", default=True)
    categories = models.ManyToManyField(
        Category, through="ItemCategory", related_name="menu_items", blank=True, verbose_name="Categories"
    )
    options = models.ManyToManyField(
        Option, through="ItemOption", related_name="menu_items", blank=True, verbose_name="Options"
    )

    class Meta:
        verbose_name = "Menu item"
        verbose_name_plural = "Menu items"
        indexes = [
            models.Index(fields=["restaurant", "is_active"]),
            models.Index(fields=["is_available"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(base_price__gte=0), name="menuitem_base_price_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.restaurant.name})"


class ItemCategory(models.Model):
    """
    Through table for MenuItem <-> Category
    Stores an extra 'position' for sorting items inside a category
    Ensures uniqueness for (menu_item, category)
    """
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE, related_name="item_categories", verbose_name="Menu item"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="item_categories", verbose_name="Category"
    )
    position = models.PositiveIntegerField("Position", default=0)

    class Meta:
        verbose_name = "Item category link"
        verbose_name_plural = "Item category links"
        ordering = ["category__name", "position"]
        constraints = [
            models.UniqueConstraint(fields=["menu_item", "category"], name="uq_itemcategory_item_category"),
            models.CheckConstraint(check=Q(position__gte=0), name="itemcategory_position_non_negative"),
        ]
        indexes = [models.Index(fields=["category", "position"])]

    def __str__(self) -> str:
        return f"{self.menu_item} in {self.category} pos={self.position}"


class ItemOption(models.Model):
    """
    Through table for MenuItem <-> Option.
    Contains:
      - price_delta: non-negative price adjustment
      - is_default: whether preselected by default
    Ensures uniqueness for (menu_item, option).
    """
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.CASCADE, related_name="item_options", verbose_name="Menu item"
    )
    option = models.ForeignKey(
        Option, on_delete=models.CASCADE, related_name="item_options", verbose_name="Option"
    )
    price_delta = models.DecimalField(
        "Price delta", max_digits=10, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))]
    )
    is_default = models.BooleanField("Default selected", default=False)

    class Meta:
        verbose_name = "Item option link"
        verbose_name_plural = "Item option links"
        constraints = [
            models.UniqueConstraint(fields=["menu_item", "option"], name="uq_itemoption_item_option"),
            models.CheckConstraint(check=Q(price_delta__gte=0), name="itemoption_price_delta_non_negative"),
        ]
        indexes = [models.Index(fields=["menu_item"]), models.Index(fields=["option"]), models.Index(fields=["is_default"])]

    def __str__(self) -> str:
        return f"{self.option} for {self.menu_item} (+{self.price_delta})"