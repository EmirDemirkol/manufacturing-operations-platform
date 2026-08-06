from django.core.validators import RegexValidator
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
