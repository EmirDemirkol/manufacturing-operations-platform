from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


code_validator = RegexValidator(
    regex=r"^[A-Z0-9_-]+$",
    message=(
        "Use uppercase letters, numbers, hyphens, "
        "and underscores only."
    ),
)


class ActiveTimestampedModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Site(ActiveTimestampedModel):
    code = models.CharField(
        max_length=20,
        unique=True,
        validators=[code_validator],
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProductionArea(ActiveTimestampedModel):
    site = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        related_name="production_areas",
    )
    code = models.CharField(
        max_length=20,
        validators=[code_validator],
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["site__code", "code"]
        constraints = [
            models.UniqueConstraint(
                fields=["site", "code"],
                name="unique_area_code_per_site",
            ),
        ]

    def __str__(self):
        return f"{self.site.code} / {self.code} - {self.name}"


class ProductionLine(ActiveTimestampedModel):
    production_area = models.ForeignKey(
        ProductionArea,
        on_delete=models.PROTECT,
        related_name="production_lines",
    )
    code = models.CharField(
        max_length=20,
        validators=[code_validator],
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = [
            "production_area__site__code",
            "production_area__code",
            "code",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["production_area", "code"],
                name="unique_line_code_per_area",
            ),
        ]

    def __str__(self):
        return (
            f"{self.production_area.site.code} / "
            f"{self.production_area.code} / "
            f"{self.code} - {self.name}"
        )


class Product(ActiveTimestampedModel):
    code = models.CharField(
        max_length=20,
        unique=True,
        validators=[code_validator],
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Shift(ActiveTimestampedModel):
    name = models.CharField(max_length=80, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["start_time", "name"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(
                    start_time=models.F("end_time")
                ),
                name="shift_start_end_different",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.start_time is not None
            and self.end_time is not None
            and self.start_time == self.end_time
        ):
            raise ValidationError(
                {
                    "end_time": (
                        "End time must be different from start time."
                    )
                }
            )

    @property
    def is_overnight(self):
        return self.end_time < self.start_time

    def __str__(self):
        return (
            f"{self.name}: "
            f"{self.start_time.strftime('%H:%M')} to "
            f"{self.end_time.strftime('%H:%M')}"
        )


class DowntimeReason(ActiveTimestampedModel):
    code = models.CharField(
        max_length=20,
        unique=True,
        validators=[code_validator],
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class WorkOrder(ActiveTimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        RELEASED = "RELEASED", "Released"
        IN_PROGRESS = "IN_PROGRESS", "In progress"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    order_number = models.CharField(
        max_length=30,
        unique=True,
        validators=[code_validator],
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="work_orders",
    )
    planned_quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    due_date = models.DateField(
        null=True,
        blank=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at", "order_number"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(planned_quantity__gt=0),
                name="work_order_planned_quantity_positive",
            ),
        ]

    def __str__(self):
        return (
            f"{self.order_number} - "
            f"{self.product.code} - "
            f"{self.product.name}"
        )


class ProductionRun(ActiveTimestampedModel):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        ACTIVE = "ACTIVE", "Active"
        PAUSED = "PAUSED", "Paused"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.PROTECT,
        related_name="production_runs",
    )
    production_line = models.ForeignKey(
        ProductionLine,
        on_delete=models.PROTECT,
        related_name="production_runs",
    )
    shift = models.ForeignKey(
        Shift,
        on_delete=models.PROTECT,
        related_name="production_runs",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    good_quantity = models.PositiveIntegerField(default=0)
    rejected_quantity = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(good_quantity__gte=0),
                name="production_run_good_quantity_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(rejected_quantity__gte=0),
                name="production_run_rejected_quantity_nonnegative",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(started_at__isnull=True)
                    | models.Q(ended_at__isnull=True)
                    | models.Q(
                        ended_at__gte=models.F("started_at")
                    )
                ),
                name="production_run_end_not_before_start",
            ),
            models.UniqueConstraint(
                fields=["work_order"],
                condition=models.Q(status="ACTIVE"),
                name="unique_active_run_per_work_order",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.started_at is not None
            and self.ended_at is not None
            and self.ended_at < self.started_at
        ):
            raise ValidationError(
                {
                    "ended_at": (
                        "End time cannot be earlier than start time."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.work_order.order_number} - "
            f"{self.production_line}"
        )