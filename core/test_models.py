from datetime import time

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from .models import (
    DowntimeReason,
    Product,
    ProductionArea,
    ProductionLine,
    Shift,
    Site,
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