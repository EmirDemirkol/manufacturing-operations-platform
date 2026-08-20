from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import (
    AuditEvent,
    DowntimeEvent,
    DowntimeReason,
    Product,
    ProductionArea,
    ProductionEntry,
    ProductionLine,
    ProductionRun,
    QualityInspection,
    Shift,
    Site,
    WorkOrder,
)


DEMO_USERNAMES = {
    "operator": "operator_demo",
    "supervisor": "supervisor_demo",
    "quality": "quality_demo",
    "engineer": "engineer_demo",
    "manager": "manager_demo",
    "sysadmin": "sysadmin_demo",
}


class Command(BaseCommand):
    help = "Create or update the synthetic ForgeOps MVP demonstration data."

    def handle(self, *args, **options):
        User = get_user_model()

        users = {}

        for role_key, username in DEMO_USERNAMES.items():
            try:
                users[role_key] = User.objects.get(
                    username=username,
                )
            except User.DoesNotExist as error:
                raise CommandError(
                    f"Missing demonstration user: {username}. "
                    "Run 'python manage.py seed_demo_users' first."
                ) from error

        now = timezone.now()

        with transaction.atomic():
            site, _ = Site.objects.update_or_create(
                code="DEMO-DUB",
                defaults={
                    "name": "ForgeOps Demonstration Site",
                    "description": (
                        "Synthetic manufacturing site used only "
                        "for the ForgeOps portfolio demonstration."
                    ),
                    "is_active": True,
                },
            )

            area, _ = ProductionArea.objects.update_or_create(
                site=site,
                code="ASSEMBLY",
                defaults={
                    "name": "Assembly Area",
                    "description": (
                        "Synthetic assembly production area."
                    ),
                    "is_active": True,
                },
            )

            line_1, _ = ProductionLine.objects.update_or_create(
                production_area=area,
                code="LINE-01",
                defaults={
                    "name": "Assembly Line 01",
                    "description": (
                        "Primary synthetic demonstration line."
                    ),
                    "is_active": True,
                },
            )

            line_2, _ = ProductionLine.objects.update_or_create(
                production_area=area,
                code="LINE-02",
                defaults={
                    "name": "Assembly Line 02",
                    "description": (
                        "Secondary synthetic demonstration line."
                    ),
                    "is_active": True,
                },
            )

            product_100, _ = Product.objects.update_or_create(
                code="FG-100",
                defaults={
                    "name": "Demo Control Module",
                    "description": (
                        "Synthetic finished-good product used "
                        "for ForgeOps demonstration data."
                    ),
                    "is_active": True,
                },
            )

            product_200, _ = Product.objects.update_or_create(
                code="FG-200",
                defaults={
                    "name": "Demo Sensor Assembly",
                    "description": (
                        "Synthetic finished-good product used "
                        "for ForgeOps demonstration data."
                    ),
                    "is_active": True,
                },
            )

            day_shift, _ = Shift.objects.update_or_create(
                name="Day Shift",
                defaults={
                    "start_time": time(6, 0),
                    "end_time": time(14, 0),
                    "is_active": True,
                },
            )

            night_shift, _ = Shift.objects.update_or_create(
                name="Night Shift",
                defaults={
                    "start_time": time(22, 0),
                    "end_time": time(6, 0),
                    "is_active": True,
                },
            )

            equipment_reason, _ = (
                DowntimeReason.objects.update_or_create(
                    code="EQUIPMENT",
                    defaults={
                        "name": "Equipment Issue",
                        "description": (
                            "Synthetic equipment-related downtime."
                        ),
                        "is_active": True,
                    },
                )
            )

            material_reason, _ = (
                DowntimeReason.objects.update_or_create(
                    code="MATERIAL",
                    defaults={
                        "name": "Material Shortage",
                        "description": (
                            "Synthetic material-related downtime."
                        ),
                        "is_active": True,
                    },
                )
            )

            changeover_reason, _ = (
                DowntimeReason.objects.update_or_create(
                    code="CHANGEOVER",
                    defaults={
                        "name": "Changeover",
                        "description": (
                            "Synthetic planned changeover downtime."
                        ),
                        "is_active": True,
                    },
                )
            )

            completed_wo, _ = WorkOrder.objects.update_or_create(
                order_number="DEMO-WO-001",
                defaults={
                    "product": product_100,
                    "planned_quantity": 500,
                    "status": WorkOrder.Status.COMPLETED,
                    "due_date": timezone.localdate() - timedelta(days=1),
                    "notes": (
                        "Synthetic completed Work Order for "
                        "the ForgeOps MVP demonstration."
                    ),
                    "is_active": True,
                },
            )

            active_wo, _ = WorkOrder.objects.update_or_create(
                order_number="DEMO-WO-002",
                defaults={
                    "product": product_200,
                    "planned_quantity": 800,
                    "status": WorkOrder.Status.IN_PROGRESS,
                    "due_date": timezone.localdate() + timedelta(days=1),
                    "notes": (
                        "Synthetic active Work Order for "
                        "the ForgeOps MVP demonstration."
                    ),
                    "is_active": True,
                },
            )

            planned_wo, _ = WorkOrder.objects.update_or_create(
                order_number="DEMO-WO-003",
                defaults={
                    "product": product_100,
                    "planned_quantity": 350,
                    "status": WorkOrder.Status.RELEASED,
                    "due_date": timezone.localdate() + timedelta(days=3),
                    "notes": (
                        "Synthetic planned Work Order for "
                        "the ForgeOps MVP demonstration."
                    ),
                    "is_active": True,
                },
            )

            cancelled_wo, _ = WorkOrder.objects.update_or_create(
                order_number="DEMO-WO-004",
                defaults={
                    "product": product_200,
                    "planned_quantity": 250,
                    "status": WorkOrder.Status.CANCELLED,
                    "due_date": timezone.localdate() + timedelta(days=4),
                    "notes": (
                        "Synthetic cancelled Work Order for "
                        "the ForgeOps MVP demonstration."
                    ),
                    "is_active": True,
                },
            )

            completed_run = self._get_or_create_run(
               work_order=completed_wo,
               production_line=line_1,
               shift=day_shift,
               status=ProductionRun.Status.ACTIVE,
               started_at=now - timedelta(hours=8),
               ended_at=None,
               notes="DEMO-RUN-001",
            )

            active_run = self._get_or_create_run(
                work_order=active_wo,
                production_line=line_2,
                shift=day_shift,
                status=ProductionRun.Status.ACTIVE,
                started_at=now - timedelta(hours=3),
                ended_at=None,
                notes="DEMO-RUN-002",
            )

            planned_run = self._get_or_create_run(
                work_order=planned_wo,
                production_line=line_1,
                shift=night_shift,
                status=ProductionRun.Status.PLANNED,
                started_at=None,
                ended_at=None,
                notes="DEMO-RUN-003",
            )

            cancelled_run = self._get_or_create_run(
                work_order=cancelled_wo,
                production_line=line_2,
                shift=night_shift,
                status=ProductionRun.Status.CANCELLED,
                started_at=None,
                ended_at=now - timedelta(days=1),
                notes="DEMO-RUN-004",
            )

            self._get_or_create_entry(
                production_run=completed_run,
                recorded_by=users["operator"],
                good_quantity=245,
                rejected_quantity=5,
                notes="DEMO-ENTRY-001",
            )

            self._get_or_create_entry(
                production_run=completed_run,
                recorded_by=users["operator"],
                good_quantity=248,
                rejected_quantity=2,
                notes="DEMO-ENTRY-002",
            )

            self._get_or_create_entry(
                production_run=active_run,
                recorded_by=users["operator"],
                good_quantity=180,
                rejected_quantity=4,
                notes="DEMO-ENTRY-003",
            )

            self._get_or_create_entry(
                production_run=active_run,
                recorded_by=users["operator"],
                good_quantity=160,
                rejected_quantity=3,
                notes="DEMO-ENTRY-004",
            )

            closed_downtime = self._get_or_create_downtime(
                production_run=completed_run,
                downtime_reason=changeover_reason,
                started_at=now - timedelta(hours=6),
                ended_at=now - timedelta(hours=5, minutes=35),
                opened_by=users["operator"],
                closed_by=users["operator"],
                notes="DEMO-DOWNTIME-001",
            )

            open_downtime = self._get_or_create_downtime(
                production_run=active_run,
                downtime_reason=equipment_reason,
                started_at=now - timedelta(minutes=20),
                ended_at=None,
                opened_by=users["operator"],
                closed_by=None,
                notes="DEMO-DOWNTIME-002",
            )

            passed_inspection = self._get_or_create_inspection(
                production_run=completed_run,
                result=QualityInspection.Result.PASSED,
                notes=(
                    "DEMO-QUALITY-001: Synthetic final inspection passed."
                ),
                completed_by=users["quality"],
                completed_at=now - timedelta(hours=2, minutes=15),
            )

            pending_inspection = self._get_or_create_inspection(
                production_run=active_run,
                result=QualityInspection.Result.PENDING,
                notes=(
                    "DEMO-QUALITY-002: Synthetic inspection awaiting result."
                ),
                completed_by=None,
                completed_at=None,
            )

            completed_run.status = ProductionRun.Status.COMPLETED
            completed_run.ended_at = now - timedelta(hours=2)
            completed_run.full_clean()
            completed_run.save(
                update_fields=[
                    "status",
                    "ended_at",
                    "updated_at",
                ]
           )

            self._get_or_create_audit_event(
                user=users["supervisor"],
                action_type=AuditEvent.ActionType.CREATED,
                record_type="WorkOrder",
                record_identifier=completed_wo.order_number,
                description=(
                    "Synthetic demonstration AuditEvent for Work Order "
                    "creation. This record is explicitly seeded and does "
                    "not imply automatic audit generation."
                ),
            )

            self._get_or_create_audit_event(
                user=users["supervisor"],
                action_type=AuditEvent.ActionType.COMPLETED,
                record_type="ProductionRun",
                record_identifier=f"run-{completed_run.pk}",
                description=(
                    "Synthetic demonstration AuditEvent for Production "
                    "Run completion. This record is explicitly seeded."
                ),
            )

            self._get_or_create_audit_event(
                user=users["operator"],
                action_type=AuditEvent.ActionType.CLOSED,
                record_type="DowntimeEvent",
                record_identifier=f"downtime-{closed_downtime.pk}",
                description=(
                    "Synthetic demonstration AuditEvent for downtime "
                    "closure. This record is explicitly seeded."
                ),
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "ForgeOps synthetic MVP demonstration data is ready."
                )
            )

            self.stdout.write("")
            self.stdout.write("Created or updated:")
            self.stdout.write("  Site: DEMO-DUB")
            self.stdout.write("  Production Area: ASSEMBLY")
            self.stdout.write("  Production Lines: LINE-01, LINE-02")
            self.stdout.write("  Products: FG-100, FG-200")
            self.stdout.write("  Work Orders: DEMO-WO-001 to DEMO-WO-004")
            self.stdout.write(
                f"  Completed Production Run: {completed_run.pk}"
            )
            self.stdout.write(
                f"  Active Production Run: {active_run.pk}"
            )
            self.stdout.write(
                f"  Planned Production Run: {planned_run.pk}"
            )
            self.stdout.write(
                f"  Cancelled Production Run: {cancelled_run.pk}"
            )
            self.stdout.write(
                f"  Open Downtime Event: {open_downtime.pk}"
            )
            self.stdout.write(
                f"  Passed Quality Inspection: {passed_inspection.pk}"
            )
            self.stdout.write(
                f"  Pending Quality Inspection: {pending_inspection.pk}"
            )

    def _get_or_create_run(
        self,
        *,
        work_order,
        production_line,
        shift,
        status,
        started_at,
        ended_at,
        notes,
    ):
        production_run = (
            ProductionRun.objects.filter(
                work_order=work_order,
                notes=notes,
            )
            .order_by("pk")
            .first()
        )

        if production_run is None:
            production_run = ProductionRun(
                work_order=work_order,
                production_line=production_line,
                shift=shift,
                status=status,
                started_at=started_at,
                ended_at=ended_at,
                notes=notes,
            )
        else:
            production_run.production_line = production_line
            production_run.shift = shift
            production_run.status = status
            production_run.started_at = started_at
            production_run.ended_at = ended_at

        production_run.full_clean()
        production_run.save()

        return production_run

    def _get_or_create_entry(
        self,
        *,
        production_run,
        recorded_by,
        good_quantity,
        rejected_quantity,
        notes,
    ):
        production_entry = (
            ProductionEntry.objects.filter(
                production_run=production_run,
                notes=notes,
            )
            .order_by("pk")
            .first()
        )

        if production_entry is None:
            production_entry = ProductionEntry(
                production_run=production_run,
                good_quantity=good_quantity,
                rejected_quantity=rejected_quantity,
                recorded_by=recorded_by,
                notes=notes,
            )
        else:
            production_entry.good_quantity = good_quantity
            production_entry.rejected_quantity = rejected_quantity
            production_entry.recorded_by = recorded_by

        production_entry.full_clean()
        production_entry.save()

        return production_entry

    def _get_or_create_downtime(
        self,
        *,
        production_run,
        downtime_reason,
        started_at,
        ended_at,
        opened_by,
        closed_by,
        notes,
    ):
        downtime_event = (
            DowntimeEvent.objects.filter(
                production_run=production_run,
                notes=notes,
            )
            .order_by("pk")
            .first()
        )

        if downtime_event is None:
            downtime_event = DowntimeEvent(
                production_run=production_run,
                downtime_reason=downtime_reason,
                started_at=started_at,
                ended_at=ended_at,
                opened_by=opened_by,
                closed_by=closed_by,
                notes=notes,
            )
        else:
            downtime_event.downtime_reason = downtime_reason
            downtime_event.started_at = started_at
            downtime_event.ended_at = ended_at
            downtime_event.opened_by = opened_by
            downtime_event.closed_by = closed_by

        downtime_event.full_clean()
        downtime_event.save()

        return downtime_event

    def _get_or_create_inspection(
        self,
        *,
        production_run,
        result,
        notes,
        completed_by,
        completed_at,
    ):
        quality_inspection = (
            QualityInspection.objects.filter(
                production_run=production_run,
                notes=notes,
            )
            .order_by("pk")
            .first()
        )

        if quality_inspection is None:
            quality_inspection = QualityInspection(
                production_run=production_run,
                result=result,
                notes=notes,
                completed_by=completed_by,
                completed_at=completed_at,
            )
        else:
            quality_inspection.result = result
            quality_inspection.completed_by = completed_by
            quality_inspection.completed_at = completed_at

        quality_inspection.full_clean()
        quality_inspection.save()

        return quality_inspection

    def _get_or_create_audit_event(
        self,
        *,
        user,
        action_type,
        record_type,
        record_identifier,
        description,
    ):
        audit_event = (
            AuditEvent.objects.filter(
                user=user,
                action_type=action_type,
                record_type=record_type,
                record_identifier=record_identifier,
                description=description,
            )
            .order_by("pk")
            .first()
        )

        if audit_event is None:
            audit_event = AuditEvent.objects.create(
                user=user,
                action_type=action_type,
                record_type=record_type,
                record_identifier=record_identifier,
                description=description,
            )

        return audit_event