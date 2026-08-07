from django.contrib import admin

from .models import (
    DowntimeReason,
    Product,
    ProductionArea,
    ProductionLine,
    ProductionRun,
    Shift,
    Site,
    WorkOrder,
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
    list_select_related = ("site",)


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
    list_select_related = (
        "production_area",
        "production_area__site",
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


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "product",
        "planned_quantity",
        "status",
        "due_date",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "product",
        "is_active",
    )
    search_fields = (
        "order_number",
        "product__code",
        "product__name",
        "notes",
    )
    ordering = (
        "-created_at",
        "order_number",
    )
    autocomplete_fields = ("product",)
    list_select_related = ("product",)


@admin.register(ProductionRun)
class ProductionRunAdmin(admin.ModelAdmin):
    list_display = (
        "work_order",
        "production_line",
        "shift",
        "status",
        "good_quantity",
        "rejected_quantity",
        "started_at",
        "ended_at",
        "is_active",
        "created_at",
    )
    list_filter = (
        "status",
        "production_line__production_area__site",
        "production_line",
        "shift",
        "is_active",
    )
    search_fields = (
        "work_order__order_number",
        "work_order__product__code",
        "work_order__product__name",
        "production_line__code",
        "production_line__name",
        "production_line__production_area__code",
        "production_line__production_area__site__code",
        "shift__name",
        "notes",
    )
    ordering = ("-created_at",)
    autocomplete_fields = (
        "work_order",
        "production_line",
        "shift",
    )
    list_select_related = (
        "work_order",
        "work_order__product",
        "production_line",
        "production_line__production_area",
        "production_line__production_area__site",
        "shift",
    )
