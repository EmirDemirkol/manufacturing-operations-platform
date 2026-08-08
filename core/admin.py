from django.contrib import admin
from django.db.models import Sum

from .models import (
    DowntimeEvent,
    DowntimeReason,
    Product,
    ProductionArea,
    ProductionEntry,
    ProductionLine,
    ProductionRun,
    Shift,
    Site,
    WorkOrder,
)


# Correct Django's automatic pluralisation of ProductionEntry
# for the administration interface only.
ProductionEntry._meta.verbose_name_plural = "Production entries"


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
    list_filter = (
        "site",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
        "site__code",
        "site__name",
    )
    ordering = (
        "site__code",
        "code",
    )
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
    search_fields = (
        "code",
        "name",
        "description",
    )
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
    ordering = (
        "start_time",
        "name",
    )

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
    search_fields = (
        "code",
        "name",
        "description",
    )
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
        "total_good_quantity",
        "total_rejected_quantity",
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

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            admin_good_quantity=Sum(
                "production_entries__good_quantity"
            ),
            admin_rejected_quantity=Sum(
                "production_entries__rejected_quantity"
            ),
        )

    @admin.display(
        ordering="admin_good_quantity",
        description="Good quantity",
    )
    def total_good_quantity(self, obj):
        return obj.admin_good_quantity or 0

    @admin.display(
        ordering="admin_rejected_quantity",
        description="Rejected quantity",
    )
    def total_rejected_quantity(self, obj):
        return obj.admin_rejected_quantity or 0


@admin.register(ProductionEntry)
class ProductionEntryAdmin(admin.ModelAdmin):
    list_display = (
        "production_run",
        "good_quantity",
        "rejected_quantity",
        "recorded_by",
        "recorded_at",
    )
    list_filter = (
        "production_run__status",
        "production_run__production_line__production_area__site",
        "production_run__production_line",
        "recorded_by",
        "recorded_at",
    )
    search_fields = (
        "production_run__work_order__order_number",
        "production_run__work_order__product__code",
        "production_run__work_order__product__name",
        "production_run__production_line__code",
        "recorded_by__username",
        "recorded_by__email",
        "notes",
    )
    ordering = (
        "-recorded_at",
        "-id",
    )
    autocomplete_fields = (
        "production_run",
        "recorded_by",
    )
    list_select_related = (
        "production_run",
        "production_run__work_order",
        "production_run__work_order__product",
        "production_run__production_line",
        "recorded_by",
    )


@admin.register(DowntimeEvent)
class DowntimeEventAdmin(admin.ModelAdmin):
    list_display = (
        "production_run",
        "downtime_reason",
        "downtime_state",
        "started_at",
        "ended_at",
        "downtime_duration",
        "opened_by",
        "closed_by",
    )
    list_filter = (
        "downtime_reason",
        "production_run__status",
        "production_run__production_line__production_area__site",
        "production_run__production_line",
        "opened_by",
        "closed_by",
        "started_at",
        "ended_at",
    )
    search_fields = (
        "production_run__work_order__order_number",
        "production_run__work_order__product__code",
        "production_run__work_order__product__name",
        "production_run__production_line__code",
        "production_run__production_line__name",
        "downtime_reason__code",
        "downtime_reason__name",
        "opened_by__username",
        "opened_by__email",
        "closed_by__username",
        "closed_by__email",
        "notes",
    )
    ordering = (
        "-started_at",
        "-id",
    )
    autocomplete_fields = (
        "production_run",
        "downtime_reason",
        "opened_by",
        "closed_by",
    )
    list_select_related = (
        "production_run",
        "production_run__work_order",
        "production_run__work_order__product",
        "production_run__production_line",
        "production_run__production_line__production_area",
        "production_run__production_line__production_area__site",
        "downtime_reason",
        "opened_by",
        "closed_by",
    )

    @admin.display(description="State")
    def downtime_state(self, obj):
        if obj.ended_at is None:
            return "Open"

        return "Closed"

    @admin.display(description="Duration")
    def downtime_duration(self, obj):
        if obj.duration is None:
            return "Open"

        return obj.duration