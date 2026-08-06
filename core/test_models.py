from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from .models import ProductionArea, ProductionLine, Site


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