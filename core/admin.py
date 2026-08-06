from django.contrib import admin

from .models import (
    DowntimeReason,
    Product,
    ProductionArea,
    ProductionLine,
    Shift,
    Site,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(ProductionArea)
class ProductionAreaAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "site",
        "is_active",
        "created_at",
    )
    list_filter = ("site", "is_active")
    search_fields = (
        "code",
        "name",
        "site__code",
        "site__name",
    )
    ordering = ("site__code", "code")


@admin.register(ProductionLine)
class ProductionLineAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "production_area",
        "is_active",
        "created_at",
    )
    list_filter = (
        "production_area__site",
        "production_area",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
        "production_area__code",
        "production_area__name",
        "production_area__site__code",
    )
    ordering = (
        "production_area__site__code",
        "production_area__code",
        "code",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("code", "name", "description")
    ordering = ("code",)


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_time",
        "end_time",
        "overnight",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("start_time", "name")

    @admin.display(boolean=True, description="Overnight")
    def overnight(self, obj):
        return obj.is_overnight


@admin.register(DowntimeReason)
class DowntimeReasonAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active",)
    search_fields = ("code", "name", "description")
    ordering = ("code",)
