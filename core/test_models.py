from datetime import time, timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase
from django.utils import timezone

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


class ManufacturingHierarchyModelTests(TestCase):
    def setUp(self):
        self.site = Site.objects.create(
            code="DUB01",
            name="ForgeOps Dublin Plant",
            description="Synthetic manufacturing site.",
        )

        self.area = ProductionArea.objects.create(
            site=self.site,
            code="ASSEMBLY",
            name="Final Assembly",
            description="Synthetic final assembly area.",
        )

        self.line = ProductionLine.objects.create(
            production_area=self.area,
            code="LINE-A01",
            name="Assembly Line A",
            description="Synthetic production line.",
        )

    def test_hierarchy_relationships_are_created(self):
        self.assertEqual(self.area.site, self.site)
        self.assertEqual(self.line.production_area, self.area)

        self.assertIn(
            self.area,
            self.site.production_areas.all(),
        )

        self.assertIn(
            self.line,
            self.area.production_lines.all(),
        )

    def test_site_code_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Site.objects.create(
                    code="DUB01",
                    name="Duplicate Dublin Plant",
                )

    def test_area_code_must_be_unique_within_site(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductionArea.objects.create(
                    site=self.site,
                    code="ASSEMBLY",
                    name="Duplicate Assembly Area",
                )

    def test_area_code_can_repeat_in_another_site(self):
        second_site = Site.objects.create(
            code="GAL01",
            name="ForgeOps Galway Plant",
        )

        second_area = ProductionArea.objects.create(
            site=second_site,
            code="ASSEMBLY",
            name="Galway Final Assembly",
        )

        self.assertEqual(second_area.code, "ASSEMBLY")
        self.assertEqual(second_area.site, second_site)

    def test_line_code_must_be_unique_within_area(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductionLine.objects.create(
                    production_area=self.area,
                    code="LINE-A01",
                    name="Duplicate Assembly Line",
                )

    def test_line_code_can_repeat_in_another_area(self):
        second_area = ProductionArea.objects.create(
            site=self.site,
            code="PACKAGING",
            name="Packaging",
        )

        second_line = ProductionLine.objects.create(
            production_area=second_area,
            code="LINE-A01",
            name="Packaging Line A",
        )

        self.assertEqual(second_line.code, "LINE-A01")
        self.assertEqual(second_line.production_area, second_area)

    def test_invalid_lowercase_code_is_rejected(self):
        invalid_site = Site(
            code="dub01",
            name="Invalid Site",
        )

        with self.assertRaises(ValidationError):
            invalid_site.full_clean()

    def test_parent_records_with_dependencies_are_protected(self):
        with self.assertRaises(ProtectedError):
            self.site.delete()

        with self.assertRaises(ProtectedError):
            self.area.delete()

    def test_active_status_and_timestamps_are_created(self):
        self.assertTrue(self.site.is_active)
        self.assertTrue(self.area.is_active)
        self.assertTrue(self.line.is_active)

        self.assertIsNotNone(self.site.created_at)
        self.assertIsNotNone(self.site.updated_at)

    def test_models_are_registered_in_django_admin(self):
        self.assertTrue(admin.site.is_registered(Site))
        self.assertTrue(admin.site.is_registered(ProductionArea))
        self.assertTrue(admin.site.is_registered(ProductionLine))


class OperationalReferenceModelTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            code="PRD-1001",
            name="Synthetic Medical Device Assembly",
            description=(
                "Synthetic medical-device assembly used for "
                "ForgeOps testing."
            ),
        )

        self.shift = Shift.objects.create(
            name="Night Shift",
            start_time=time(23, 0),
            end_time=time(7, 0),
        )

        self.downtime_reason = DowntimeReason.objects.create(
            code="EQUIPMENT",
            name="Equipment fault",
            description=(
                "Unplanned stoppage caused by an equipment "
                "or machine fault."
            ),
        )

    def test_reference_models_are_created(self):
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Shift.objects.count(), 1)
        self.assertEqual(DowntimeReason.objects.count(), 1)

    def test_product_code_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Product.objects.create(
                    code="PRD-1001",
                    name="Duplicate Product",
                )

    def test_downtime_reason_code_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DowntimeReason.objects.create(
                    code="EQUIPMENT",
                    name="Duplicate equipment reason",
                )

    def test_shift_name_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Shift.objects.create(
                    name="Night Shift",
                    start_time=time(22, 0),
                    end_time=time(6, 0),
                )

    def test_lowercase_product_code_is_rejected(self):
        invalid_product = Product(
            code="prd-1002",
            name="Invalid Product",
        )

        with self.assertRaises(ValidationError):
            invalid_product.full_clean()

    def test_lowercase_downtime_reason_code_is_rejected(self):
        invalid_reason = DowntimeReason(
            code="equipment",
            name="Invalid Downtime Reason",
        )

        with self.assertRaises(ValidationError):
            invalid_reason.full_clean()

    def test_blank_descriptions_are_allowed(self):
        product = Product(
            code="PRD-1002",
            name="Product Without Description",
            description="",
        )

        downtime_reason = DowntimeReason(
            code="MATERIAL",
            name="Material shortage",
            description="",
        )

        product.full_clean()
        downtime_reason.full_clean()

    def test_identical_shift_times_fail_model_validation(self):
        invalid_shift = Shift(
            name="Invalid Shift",
            start_time=time(8, 0),
            end_time=time(8, 0),
        )

        with self.assertRaises(ValidationError):
            invalid_shift.full_clean()

    def test_identical_shift_times_fail_database_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Shift.objects.create(
                    name="Invalid Database Shift",
                    start_time=time(8, 0),
                    end_time=time(8, 0),
                )

    def test_overnight_shift_is_accepted(self):
        self.shift.full_clean()

        self.assertTrue(self.shift.is_overnight)

    def test_day_shift_is_not_overnight(self):
        day_shift = Shift(
            name="Day Shift",
            start_time=time(7, 0),
            end_time=time(15, 0),
        )

        day_shift.full_clean()

        self.assertFalse(day_shift.is_overnight)

    def test_active_status_and_timestamps_are_created(self):
        records = (
            self.product,
            self.shift,
            self.downtime_reason,
        )

        for record in records:
            self.assertTrue(record.is_active)
            self.assertIsNotNone(record.created_at)
            self.assertIsNotNone(record.updated_at)

    def test_string_representations_are_readable(self):
        self.assertEqual(
            str(self.product),
            "PRD-1001 - Synthetic Medical Device Assembly",
        )

        self.assertEqual(
            str(self.shift),
            "Night Shift: 23:00 to 07:00",
        )

        self.assertEqual(
            str(self.downtime_reason),
            "EQUIPMENT - Equipment fault",
        )

    def test_reference_models_are_registered_in_django_admin(self):
        self.assertTrue(admin.site.is_registered(Product))
        self.assertTrue(admin.site.is_registered(Shift))
        self.assertTrue(admin.site.is_registered(DowntimeReason))


class WorkOrderProductionRunModelTests(TestCase):
    def setUp(self):
        self.site = Site.objects.create(
            code="DUB01",
            name="ForgeOps Dublin Plant",
            description="Synthetic manufacturing site.",
        )

        self.area = ProductionArea.objects.create(
            site=self.site,
            code="ASSEMBLY",
            name="Final Assembly",
            description="Synthetic final assembly area.",
        )

        self.line = ProductionLine.objects.create(
            production_area=self.area,
            code="LINE-A01",
            name="Assembly Line A",
            description="Synthetic production line.",
        )

        self.product = Product.objects.create(
            code="PRD-1001",
            name="Synthetic Medical Device Assembly",
            description="Synthetic product used for ForgeOps testing.",
        )

        self.shift = Shift.objects.create(
            name="Night Shift",
            start_time=time(23, 0),
            end_time=time(7, 0),
        )

        self.work_order = WorkOrder.objects.create(
            order_number="WO-2026-0001",
            product=self.product,
            planned_quantity=1000,
            status="RELEASED",
            notes="Synthetic ForgeOps work order.",
        )

    def test_work_order_is_created_with_expected_relationship(self):
        self.assertEqual(self.work_order.product, self.product)
        self.assertEqual(self.work_order.planned_quantity, 1000)
        self.assertEqual(self.work_order.status, "RELEASED")

        self.assertIn(
            self.work_order,
            self.product.work_orders.all(),
        )

    def test_work_order_defaults_are_correct(self):
        work_order = WorkOrder.objects.create(
            order_number="WO-2026-0002",
            product=self.product,
            planned_quantity=500,
        )

        self.assertEqual(work_order.status, "DRAFT")
        self.assertTrue(work_order.is_active)
        self.assertIsNone(work_order.due_date)
        self.assertEqual(work_order.notes, "")

    def test_work_order_number_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WorkOrder.objects.create(
                    order_number="WO-2026-0001",
                    product=self.product,
                    planned_quantity=500,
                )

    def test_lowercase_work_order_number_is_rejected(self):
        invalid_work_order = WorkOrder(
            order_number="wo-2026-0002",
            product=self.product,
            planned_quantity=500,
        )

        with self.assertRaises(ValidationError):
            invalid_work_order.full_clean()

    def test_planned_quantity_must_be_positive_model_validation(self):
        invalid_work_order = WorkOrder(
            order_number="WO-2026-0003",
            product=self.product,
            planned_quantity=0,
        )

        with self.assertRaises(ValidationError):
            invalid_work_order.full_clean()

    def test_planned_quantity_must_be_positive_database_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WorkOrder.objects.create(
                    order_number="WO-2026-0004",
                    product=self.product,
                    planned_quantity=0,
                )

    def test_production_run_is_created_with_expected_relationships(self):
        production_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
        )

        self.assertEqual(
            production_run.work_order,
            self.work_order,
        )

        self.assertEqual(
            production_run.production_line,
            self.line,
        )

        self.assertEqual(
            production_run.shift,
            self.shift,
        )

        self.assertIn(
            production_run,
            self.work_order.production_runs.all(),
        )

    def test_production_run_defaults_are_correct(self):
        production_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
        )

        self.assertEqual(production_run.status, "PLANNED")
        self.assertEqual(production_run.good_quantity, 0)
        self.assertEqual(production_run.rejected_quantity, 0)
        self.assertIsNone(production_run.started_at)
        self.assertIsNone(production_run.ended_at)
        self.assertTrue(production_run.is_active)

    def test_work_order_can_have_multiple_non_active_production_runs(self):
        first_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="COMPLETED",
        )

        second_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="PLANNED",
        )

        self.assertEqual(
            self.work_order.production_runs.count(),
            2,
        )

        self.assertIn(
            first_run,
            self.work_order.production_runs.all(),
        )

        self.assertIn(
            second_run,
            self.work_order.production_runs.all(),
        )

    def test_only_one_active_production_run_per_work_order(self):
        ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="ACTIVE",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductionRun.objects.create(
                    work_order=self.work_order,
                    production_line=self.line,
                    shift=self.shift,
                    status="ACTIVE",
                )

    def test_different_work_orders_may_each_have_active_run(self):
        second_work_order = WorkOrder.objects.create(
            order_number="WO-2026-0002",
            product=self.product,
            planned_quantity=500,
            status="RELEASED",
        )

        first_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="ACTIVE",
        )

        second_run = ProductionRun.objects.create(
            work_order=second_work_order,
            production_line=self.line,
            shift=self.shift,
            status="ACTIVE",
        )

        self.assertEqual(first_run.status, "ACTIVE")
        self.assertEqual(second_run.status, "ACTIVE")

    def test_production_run_totals_default_to_zero_without_entries(self):
        production_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
        )

        self.assertEqual(production_run.good_quantity, 0)
        self.assertEqual(production_run.rejected_quantity, 0)

    def test_end_time_cannot_be_before_start_time_model_validation(self):
        started_at = timezone.now()

        production_run = ProductionRun(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            started_at=started_at,
            ended_at=started_at - timedelta(hours=1),
        )

        with self.assertRaises(ValidationError):
            production_run.full_clean()

    def test_end_time_cannot_be_before_start_time_database_constraint(self):
        started_at = timezone.now()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductionRun.objects.create(
                    work_order=self.work_order,
                    production_line=self.line,
                    shift=self.shift,
                    started_at=started_at,
                    ended_at=started_at - timedelta(hours=1),
                )

    def test_valid_completed_production_run_is_accepted(self):
        started_at = timezone.now()
        ended_at = started_at + timedelta(hours=8)

        production_run = ProductionRun(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="COMPLETED",
            started_at=started_at,
            ended_at=ended_at,
        )

        production_run.full_clean()
        production_run.save()

        self.assertEqual(production_run.status, "COMPLETED")
        self.assertEqual(production_run.good_quantity, 0)
        self.assertEqual(production_run.rejected_quantity, 0)

    def test_work_order_cannot_be_deleted_while_run_exists(self):
        ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
        )

        with self.assertRaises(ProtectedError):
            self.work_order.delete()

    def test_product_cannot_be_deleted_while_work_order_exists(self):
        with self.assertRaises(ProtectedError):
            self.product.delete()

    def test_production_line_cannot_be_deleted_while_run_exists(self):
        ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
        )

        with self.assertRaises(ProtectedError):
            self.line.delete()

    def test_shift_cannot_be_deleted_while_run_exists(self):
        ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
        )

        with self.assertRaises(ProtectedError):
            self.shift.delete()

    def test_active_status_and_timestamps_are_created(self):
        production_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
        )

        records = (
            self.work_order,
            production_run,
        )

        for record in records:
            self.assertTrue(record.is_active)
            self.assertIsNotNone(record.created_at)
            self.assertIsNotNone(record.updated_at)

    def test_work_order_and_production_run_are_registered_in_admin(self):
        self.assertTrue(
            admin.site.is_registered(WorkOrder)
        )

        self.assertTrue(
            admin.site.is_registered(ProductionRun)
        )

    def test_work_order_string_representation_is_readable(self):
        representation = str(self.work_order)

        self.assertIn(
            self.work_order.order_number,
            representation,
        )

        self.assertIn(
            self.product.code,
            representation,
        )

    def test_production_run_string_representation_is_readable(self):
        production_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
        )

        representation = str(production_run)

        self.assertIn(
            self.work_order.order_number,
            representation,
        )

        self.assertIn(
            self.line.code,
            representation,
        )


class ProductionEntryModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user = user_model.objects.create_user(
            username="synthetic_operator",
            password="SyntheticTestPassword123!",
        )

        self.site = Site.objects.create(
            code="DUB01",
            name="ForgeOps Dublin Plant",
            description="Synthetic manufacturing site.",
        )

        self.area = ProductionArea.objects.create(
            site=self.site,
            code="ASSEMBLY",
            name="Final Assembly",
            description="Synthetic final assembly area.",
        )

        self.line = ProductionLine.objects.create(
            production_area=self.area,
            code="LINE-A01",
            name="Assembly Line A",
            description="Synthetic production line.",
        )

        self.product = Product.objects.create(
            code="PRD-1001",
            name="Synthetic Medical Device Assembly",
            description="Synthetic product used for ForgeOps testing.",
        )

        self.shift = Shift.objects.create(
            name="Night Shift",
            start_time=time(23, 0),
            end_time=time(7, 0),
        )

        self.work_order = WorkOrder.objects.create(
            order_number="WO-2026-0001",
            product=self.product,
            planned_quantity=1000,
            status="RELEASED",
            notes="Synthetic ForgeOps work order.",
        )

        self.production_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="ACTIVE",
            started_at=timezone.now(),
        )

    def test_production_entry_is_created_with_expected_relationships(self):
        entry = ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
            rejected_quantity=5,
            notes="Synthetic production quantity entry.",
        )

        self.assertEqual(
            entry.production_run,
            self.production_run,
        )

        self.assertEqual(
            entry.recorded_by,
            self.user,
        )

        self.assertIn(
            entry,
            self.production_run.production_entries.all(),
        )

    def test_production_entry_recorded_at_is_created_automatically(self):
        entry = ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=50,
        )

        self.assertIsNotNone(entry.recorded_at)

    def test_production_entry_defaults_are_correct(self):
        entry = ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=25,
        )

        self.assertEqual(entry.good_quantity, 25)
        self.assertEqual(entry.rejected_quantity, 0)
        self.assertEqual(entry.notes, "")

    def test_multiple_entries_can_be_recorded_for_same_production_run(self):
        first_entry = ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
        )

        second_entry = ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=90,
            rejected_quantity=10,
        )

        self.assertEqual(
            self.production_run.production_entries.count(),
            2,
        )

        self.assertIn(
            first_entry,
            self.production_run.production_entries.all(),
        )

        self.assertIn(
            second_entry,
            self.production_run.production_entries.all(),
        )

    def test_production_run_totals_are_derived_from_entries(self):
        ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=300,
            rejected_quantity=10,
        )

        ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=250,
            rejected_quantity=5,
        )

        ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=400,
            rejected_quantity=15,
        )

        self.assertEqual(
            self.production_run.good_quantity,
            950,
        )

        self.assertEqual(
            self.production_run.rejected_quantity,
            30,
        )

    def test_good_only_entry_is_valid(self):
        entry = ProductionEntry(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
            rejected_quantity=0,
        )

        entry.full_clean()
        entry.save()

        self.assertEqual(entry.good_quantity, 100)
        self.assertEqual(entry.rejected_quantity, 0)

    def test_rejected_only_entry_is_valid(self):
        entry = ProductionEntry(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=0,
            rejected_quantity=5,
        )

        entry.full_clean()
        entry.save()

        self.assertEqual(entry.good_quantity, 0)
        self.assertEqual(entry.rejected_quantity, 5)

    def test_zero_good_and_zero_rejected_fails_model_validation(self):
        entry = ProductionEntry(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=0,
            rejected_quantity=0,
        )

        with self.assertRaises(ValidationError):
            entry.full_clean()

    def test_zero_good_and_zero_rejected_fails_database_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductionEntry.objects.create(
                    production_run=self.production_run,
                    recorded_by=self.user,
                    good_quantity=0,
                    rejected_quantity=0,
                )

    def test_good_quantity_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductionEntry.objects.create(
                    production_run=self.production_run,
                    recorded_by=self.user,
                    good_quantity=-1,
                    rejected_quantity=0,
                )

    def test_rejected_quantity_cannot_be_negative(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductionEntry.objects.create(
                    production_run=self.production_run,
                    recorded_by=self.user,
                    good_quantity=0,
                    rejected_quantity=-1,
                )

    def test_entry_is_allowed_for_active_production_run(self):
        entry = ProductionEntry(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
            rejected_quantity=2,
        )

        entry.full_clean()
        entry.save()

        self.assertEqual(
            entry.production_run.status,
            "ACTIVE",
        )

    def test_entry_is_rejected_for_planned_production_run(self):
        planned_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="PLANNED",
        )

        entry = ProductionEntry(
            production_run=planned_run,
            recorded_by=self.user,
            good_quantity=100,
        )

        with self.assertRaises(ValidationError):
            entry.full_clean()

    def test_entry_is_rejected_for_paused_production_run(self):
        self.production_run.status = "PAUSED"
        self.production_run.save()

        entry = ProductionEntry(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
        )

        with self.assertRaises(ValidationError):
            entry.full_clean()

    def test_entry_is_rejected_for_completed_production_run(self):
        self.production_run.status = "COMPLETED"
        self.production_run.save()

        entry = ProductionEntry(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
        )

        with self.assertRaises(ValidationError):
            entry.full_clean()

    def test_entry_is_rejected_for_cancelled_production_run(self):
        self.production_run.status = "CANCELLED"
        self.production_run.save()

        entry = ProductionEntry(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
        )

        with self.assertRaises(ValidationError):
            entry.full_clean()

    def test_production_run_cannot_be_deleted_while_entry_exists(self):
        ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
        )

        with self.assertRaises(ProtectedError):
            self.production_run.delete()

    def test_recorded_by_user_cannot_be_deleted_while_entry_exists(self):
        ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=100,
        )

        with self.assertRaises(ProtectedError):
            self.user.delete()

    def test_production_entry_string_representation_is_readable(self):
        entry = ProductionEntry.objects.create(
            production_run=self.production_run,
            recorded_by=self.user,
            good_quantity=95,
            rejected_quantity=5,
        )

        representation = str(entry)

        self.assertIn(
            self.work_order.order_number,
            representation,
        )

        self.assertIn(
            "95",
            representation,
        )

        self.assertIn(
            "5",
            representation,
        )

    def test_production_entry_is_registered_in_django_admin(self):
        self.assertTrue(
            admin.site.is_registered(ProductionEntry)
        )


class DowntimeEventModelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.opened_by = user_model.objects.create_user(
            username="synthetic_operator",
            password="SyntheticTestPassword123!",
        )

        self.closed_by = user_model.objects.create_user(
            username="synthetic_supervisor",
            password="SyntheticTestPassword123!",
        )

        self.site = Site.objects.create(
            code="DUB01",
            name="ForgeOps Dublin Plant",
            description="Synthetic manufacturing site.",
        )

        self.area = ProductionArea.objects.create(
            site=self.site,
            code="ASSEMBLY",
            name="Final Assembly",
            description="Synthetic final assembly area.",
        )

        self.line = ProductionLine.objects.create(
            production_area=self.area,
            code="LINE-A01",
            name="Assembly Line A",
            description="Synthetic production line.",
        )

        self.product = Product.objects.create(
            code="PRD-1001",
            name="Synthetic Medical Device Assembly",
            description="Synthetic product used for ForgeOps testing.",
        )

        self.shift = Shift.objects.create(
            name="Night Shift",
            start_time=time(23, 0),
            end_time=time(7, 0),
        )

        self.downtime_reason = DowntimeReason.objects.create(
            code="EQUIPMENT",
            name="Equipment fault",
            description="Synthetic equipment downtime reason.",
        )

        self.work_order = WorkOrder.objects.create(
            order_number="WO-2026-0001",
            product=self.product,
            planned_quantity=1000,
            status="RELEASED",
            notes="Synthetic ForgeOps work order.",
        )

        self.production_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="ACTIVE",
            started_at=timezone.now(),
        )

    def test_downtime_event_is_created_with_expected_relationships(self):
        event = DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
            notes="Synthetic downtime event.",
        )

        self.assertEqual(
            event.production_run,
            self.production_run,
        )

        self.assertEqual(
            event.downtime_reason,
            self.downtime_reason,
        )

        self.assertEqual(
            event.opened_by,
            self.opened_by,
        )

        self.assertIn(
            event,
            self.production_run.downtime_events.all(),
        )

    def test_open_downtime_event_defaults_are_correct(self):
        event = DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        self.assertIsNone(event.ended_at)
        self.assertIsNone(event.closed_by)
        self.assertEqual(event.notes, "")
        self.assertIsNotNone(event.created_at)
        self.assertIsNotNone(event.updated_at)
        self.assertIsNone(event.duration)

    def test_downtime_event_is_allowed_for_active_production_run(self):
        event = DowntimeEvent(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        event.full_clean()
        event.save()

        self.assertEqual(
            event.production_run.status,
            ProductionRun.Status.ACTIVE,
        )

    def test_downtime_event_is_rejected_for_planned_production_run(self):
        planned_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.line,
            shift=self.shift,
            status="PLANNED",
        )

        event = DowntimeEvent(
            production_run=planned_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_downtime_event_is_rejected_for_paused_production_run(self):
        self.production_run.status = ProductionRun.Status.PAUSED
        self.production_run.save()

        event = DowntimeEvent(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_downtime_event_is_rejected_for_completed_production_run(self):
        self.production_run.status = ProductionRun.Status.COMPLETED
        self.production_run.save()

        event = DowntimeEvent(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_downtime_event_is_rejected_for_cancelled_production_run(self):
        self.production_run.status = ProductionRun.Status.CANCELLED
        self.production_run.save()

        event = DowntimeEvent(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_end_time_cannot_be_before_start_time_model_validation(self):
        started_at = timezone.now()

        event = DowntimeEvent(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=started_at,
            ended_at=started_at - timedelta(minutes=5),
            opened_by=self.opened_by,
            closed_by=self.closed_by,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_end_time_cannot_be_before_start_time_database_constraint(self):
        started_at = timezone.now()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DowntimeEvent.objects.create(
                    production_run=self.production_run,
                    downtime_reason=self.downtime_reason,
                    started_at=started_at,
                    ended_at=started_at - timedelta(minutes=5),
                    opened_by=self.opened_by,
                    closed_by=self.closed_by,
                )

    def test_only_one_open_downtime_event_per_production_run(self):
        DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DowntimeEvent.objects.create(
                    production_run=self.production_run,
                    downtime_reason=self.downtime_reason,
                    started_at=timezone.now(),
                    opened_by=self.opened_by,
                )

    def test_multiple_closed_downtime_events_are_allowed(self):
        first_start = timezone.now()
        second_start = first_start + timedelta(hours=1)

        first_event = DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=first_start,
            ended_at=first_start + timedelta(minutes=10),
            opened_by=self.opened_by,
            closed_by=self.closed_by,
        )

        second_event = DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=second_start,
            ended_at=second_start + timedelta(minutes=5),
            opened_by=self.opened_by,
            closed_by=self.closed_by,
        )

        self.assertEqual(
            self.production_run.downtime_events.count(),
            2,
        )

        self.assertIn(
            first_event,
            self.production_run.downtime_events.all(),
        )

        self.assertIn(
            second_event,
            self.production_run.downtime_events.all(),
        )

    def test_open_event_cannot_have_closed_by_user(self):
        event = DowntimeEvent(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
            closed_by=self.closed_by,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_closed_event_requires_closed_by_user(self):
        started_at = timezone.now()

        event = DowntimeEvent(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=started_at,
            ended_at=started_at + timedelta(minutes=10),
            opened_by=self.opened_by,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_close_state_consistency_database_constraint(self):
        started_at = timezone.now()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DowntimeEvent.objects.create(
                    production_run=self.production_run,
                    downtime_reason=self.downtime_reason,
                    started_at=started_at,
                    ended_at=started_at + timedelta(minutes=10),
                    opened_by=self.opened_by,
                )

    def test_closed_downtime_duration_is_derived(self):
        started_at = timezone.now()
        ended_at = started_at + timedelta(minutes=17)

        event = DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=started_at,
            ended_at=ended_at,
            opened_by=self.opened_by,
            closed_by=self.closed_by,
        )

        self.assertEqual(
            event.duration,
            timedelta(minutes=17),
        )

    def test_production_run_cannot_be_deleted_while_downtime_exists(self):
        DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        with self.assertRaises(ProtectedError):
            self.production_run.delete()

    def test_downtime_reason_cannot_be_deleted_while_downtime_exists(self):
        DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        with self.assertRaises(ProtectedError):
            self.downtime_reason.delete()

    def test_opened_by_user_cannot_be_deleted_while_downtime_exists(self):
        DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        with self.assertRaises(ProtectedError):
            self.opened_by.delete()

    def test_closed_by_user_cannot_be_deleted_while_downtime_exists(self):
        started_at = timezone.now()

        DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=started_at,
            ended_at=started_at + timedelta(minutes=10),
            opened_by=self.opened_by,
            closed_by=self.closed_by,
        )

        with self.assertRaises(ProtectedError):
            self.closed_by.delete()

    def test_downtime_event_string_representation_is_readable(self):
        event = DowntimeEvent.objects.create(
            production_run=self.production_run,
            downtime_reason=self.downtime_reason,
            started_at=timezone.now(),
            opened_by=self.opened_by,
        )

        representation = str(event)

        self.assertIn(
            self.work_order.order_number,
            representation,
        )

        self.assertIn(
            self.downtime_reason.code,
            representation,
        )

        self.assertIn(
            "Open",
            representation,
        )

    def test_downtime_event_is_registered_in_django_admin(self):
        self.assertTrue(
            admin.site.is_registered(DowntimeEvent)
        )