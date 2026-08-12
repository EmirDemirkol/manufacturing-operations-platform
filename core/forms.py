from django import forms

from .models import Product, WorkOrder


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