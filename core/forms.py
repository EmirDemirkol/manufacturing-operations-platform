from django import forms

from .models import (
    DowntimeEvent,
    DowntimeReason,
    Product,
    ProductionEntry,
    ProductionLine,
    ProductionRun,
    QualityInspection,
    Shift,
    WorkOrder,
)


class WorkOrderForm(forms.ModelForm):
    class Meta:
        model = WorkOrder
        fields = [
            "order_number",
            "product",
            "planned_quantity",
            "status",
            "due_date",
            "notes",
        ]
        widgets = {
            "due_date": forms.DateInput(
                attrs={"type": "date"},
            ),
            "notes": forms.Textarea(
                attrs={"rows": 4},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].queryset = (
            Product.objects.filter(is_active=True)
            .order_by("code")
        )


class ProductionRunForm(forms.ModelForm):
    class Meta:
        model = ProductionRun
        fields = [
            "production_line",
            "shift",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(
                attrs={"rows": 4},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["production_line"].queryset = (
            ProductionLine.objects.filter(is_active=True)
            .select_related("production_area__site")
            .order_by(
                "production_area__site__code",
                "production_area__code",
                "code",
            )
        )

        self.fields["shift"].queryset = (
            Shift.objects.filter(is_active=True)
            .order_by("name")
        )


class ProductionEntryForm(forms.ModelForm):
    class Meta:
        model = ProductionEntry
        fields = [
            "good_quantity",
            "rejected_quantity",
        ]
        widgets = {
            "good_quantity": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": 1,
                },
            ),
            "rejected_quantity": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": 1,
                },
            ),
        }


class DowntimeEventForm(forms.ModelForm):
    class Meta:
        model = DowntimeEvent
        fields = [
            "downtime_reason",
            "started_at",
            "notes",
        ]
        widgets = {
            "started_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["downtime_reason"].queryset = (
            DowntimeReason.objects.filter(is_active=True)
            .order_by("code")
        )

        self.fields["started_at"].input_formats = [
            "%Y-%m-%dT%H:%M",
        ]


class QualityInspectionCreateForm(forms.ModelForm):
    class Meta:
        model = QualityInspection
        fields = [
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                },
            ),
        }


class QualityInspectionCompleteForm(forms.ModelForm):
    class Meta:
        model = QualityInspection
        fields = [
            "result",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 4,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["result"].choices = [
            (
                QualityInspection.Result.PASSED,
                QualityInspection.Result.PASSED.label,
            ),
            (
                QualityInspection.Result.FAILED,
                QualityInspection.Result.FAILED.label,
            ),
        ]