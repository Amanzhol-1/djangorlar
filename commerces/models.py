from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from catalogs.models import Restaurant, MenuItem

User = get_user_model()


class Address(models.Model):
    """
    User's saved delivery address
    One user can have many addresses
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses", verbose_name="User")
    label = models.CharField("Label", max_length=120, help_text="Short label: Home, Office…")
    city = models.CharField("City", max_length=120)
    street = models.CharField("Street", max_length=200)
    house = models.CharField("House", max_length=50)
    apartment = models.CharField("Apartment", max_length=50, blank=True)
    entrance = models.CharField("Entrance", max_length=20, blank=True)
    floor = models.CharField("Floor", max_length=20, blank=True)
    comment = models.CharField("Comment", max_length=300, blank=True)
    lat = models.DecimalField("Latitude", max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField("Longitude", max_digits=9, decimal_places=6, null=True, blank=True)
    is_primary = models.BooleanField("Primary", default=False)
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-is_primary", "-created_at"]
        indexes = [models.Index(fields=["user", "is_primary"]), models.Index(fields=["city"])]

    def __str__(self) -> str:
        return f"{self.label}: {self.city}, {self.street} {self.house}"


class OrderStatus(models.TextChoices):
    NEW = "new", "New"
    CONFIRMED = "confirmed", "Confirmed"
    DELIVERING = "delivering", "Delivering"
    DONE = "done", "Done"
    CANCELED = "canceled", "Canceled"


class Order(models.Model):
    """
    Order placed by a user for one restaurant and delivered to one address
    Stores status and aggregated totals (subtotal, discount_total, total)
    """
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders", verbose_name="User")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="orders", verbose_name="Restaurant")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders", verbose_name="Address")

    status = models.CharField("Status", max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEW)

    subtotal = models.DecimalField(
        "Subtotal", max_digits=12, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))]
    )
    discount_total = models.DecimalField(
        "Discount total", max_digits=12, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))]
    )
    total = models.DecimalField(
        "Total", max_digits=12, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))]
    )

    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["restaurant"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.CheckConstraint(check=Q(subtotal__gte=0), name="order_subtotal_non_negative"),
            models.CheckConstraint(check=Q(discount_total__gte=0), name="order_discount_total_non_negative"),
            models.CheckConstraint(check=Q(total__gte=0), name="order_total_non_negative"),
        ]

    def __str__(self) -> str:
        return f"Order #{self.pk} ({self.get_status_display()})"


class OrderItem(models.Model):
    """
    Snapshot of a menu item inside an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Order")
    menu_item = models.ForeignKey(
        MenuItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="ordered_items", verbose_name="Menu item"
    )
    item_name = models.CharField("Item name", max_length=200)
    item_price = models.DecimalField(
        "Item price", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )
    quantity = models.PositiveIntegerField("Quantity", validators=[MinValueValidator(1)])
    line_total = models.DecimalField(
        "Line total", max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )

    class Meta:
        verbose_name = "Order item"
        verbose_name_plural = "Order items"
        indexes = [models.Index(fields=["order"]) ]
        constraints = [
            models.CheckConstraint(check=Q(item_price__gte=0), name="orderitem_price_non_negative"),
            models.CheckConstraint(check=Q(line_total__gte=0), name="orderitem_line_total_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.item_name} x{self.quantity}"


class OrderItemOption(models.Model):
    """
    Selected options for an order item (snapshot)
    Stores option name and price delta at purchase time
    """
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="options", verbose_name="Order item"
    )
    option_name = models.CharField("Option name", max_length=120)
    price_delta = models.DecimalField(
        "Price delta", max_digits=10, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))]
    )

    class Meta:
        verbose_name = "Order item option"
        verbose_name_plural = "Order item options"
        indexes = [models.Index(fields=["order_item"])]
        constraints = [
            models.CheckConstraint(check=Q(price_delta__gte=0), name="orderitemoption_price_delta_non_negative"),
        ]

    def __str__(self) -> str:
        return f"{self.option_name} (+{self.price_delta})"


class PromoCode(models.Model):
    """
    Discount code (unique)
    Supports percent_off and/or amount_off; business rules should live in services layer
    """
    code = models.CharField("Code", max_length=40, unique=True, db_index=True)
    is_active = models.BooleanField("Active", default=True)
    valid_from = models.DateField("Valid from", null=True, blank=True)
    valid_to = models.DateField("Valid to", null=True, blank=True)

    percent_off = models.DecimalField(
        "Percent off", max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))]
    )
    amount_off = models.DecimalField(
        "Amount off", max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))]
    )
    minimum_order = models.DecimalField(
        "Minimum order", max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))]
    )

    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Promo code"
        verbose_name_plural = "Promo codes"
        indexes = [models.Index(fields=["is_active"]), models.Index(fields=["valid_from", "valid_to"])]

    def __str__(self) -> str:
        return self.code


class OrderPromo(models.Model):
    """
    Through table for Order <-> PromoCode
    Ensures unique (order, promo_code) and stores applied_amount
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_promos", verbose_name="Order")
    promo_code = models.ForeignKey(PromoCode, on_delete=models.PROTECT, related_name="order_promos", verbose_name="Promo code")
    applied_amount = models.DecimalField(
        "Applied amount", max_digits=12, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))]
    )
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Order promo"
        verbose_name_plural = "Order promos"
        constraints = [
            models.UniqueConstraint(fields=["order", "promo_code"], name="uq_orderpromo_order_promocode"),
            models.CheckConstraint(check=Q(applied_amount__gte=0), name="orderpromo_applied_amount_non_negative"),
        ]
        indexes = [models.Index(fields=["order"]), models.Index(fields=["promo_code"])]

    def __str__(self) -> str:
        return f"{self.promo_code.code} -> Order #{self.order_id} = {self.applied_amount}"


class PaymentStatus(models.TextChoices):
    """
    Payment statuses enumeration
    """
    NEW = "new", "New"
    AUTHORIZED = "authorized", "Authorized"
    CAPTURED = "captured", "Captured"
    FAILED = "failed", "Failed"
    REFUNDED = "refunded", "Refunded"


class Payment(models.Model):
    """
    Payment linked to an order
    Stores amount, provider, status, and optional transaction ID
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments", verbose_name="Order")
    amount = models.DecimalField(
        "Amount", max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )
    provider = models.CharField("Provider", max_length=60, help_text="e.g., card, apple_pay, kaspi")
    status = models.CharField("Status", max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.NEW)
    transaction_id = models.CharField("Transaction ID", max_length=120, blank=True)
    created_at = models.DateTimeField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        indexes = [models.Index(fields=["order"]), models.Index(fields=["status"])]

    def __str__(self) -> str:
        return f"Payment #{self.pk} ({self.get_status_display()})"