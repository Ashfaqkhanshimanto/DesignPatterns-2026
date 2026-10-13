
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.automation.context import LocationAutomationContext
from infrastructure.persistence.models import (
    AutomationRuleRow,
    DeviceRow,
    LocationRow,
    ReadingRow,
    ZoneRow,
)


class AutomationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def location_exists(
        self,
        location_id: UUID,
    ) -> bool:
        statement = select(LocationRow.id).where(
            LocationRow.id == location_id
        )

        return self._db.scalar(statement) is not None

    def get_strategy_key(
        self,
        location_id: UUID,
    ) -> str | None:
        statement = select(
            AutomationRuleRow.strategy_key
        ).where(
            AutomationRuleRow.location_id == location_id
        )

        return self._db.scalar(statement)

    def save_strategy_key(
        self,
        location_id: UUID,
        strategy_key: str,
    ) -> None:
        statement = select(AutomationRuleRow).where(
            AutomationRuleRow.location_id == location_id
        )

        rule = self._db.scalar(statement)

        if rule is None:
            rule = AutomationRuleRow(
                location_id=location_id,
                strategy_key=strategy_key,
            )

            self._db.add(rule)

        else:
            rule.strategy_key = strategy_key

        self._db.commit()

    def get_contexts(
        self,
        location_id: UUID,
    ) -> list[LocationAutomationContext]:
        zones = self._db.scalars(
            select(ZoneRow)
            .where(
                ZoneRow.location_id == location_id
            )
            .order_by(
                ZoneRow.name,
                ZoneRow.id,
            )
        ).all()

        contexts: list[LocationAutomationContext] = []

        for zone in zones:
            sensor_ids = self._db.scalars(
                select(DeviceRow.id).where(
                    DeviceRow.zone_id == zone.id,
                    DeviceRow.role == "sensor",
                    DeviceRow.device_type == "moisture_sensor",
                )
            ).all()

            moisture = None
            missing_reason = None

            if not sensor_ids:
                missing_reason = (
                    "No moisture sensor assigned to this zone."
                )

            else:
                latest = self._db.scalar(
                    select(ReadingRow)
                    .where(
                        ReadingRow.device_id.in_(sensor_ids)
                    )
                    .order_by(
                        ReadingRow.recorded_at.desc(),
                        ReadingRow.id.desc(),
                    )
                    .limit(1)
                )

                if latest is None:
                    missing_reason = (
                        "No moisture reading stored for "
                        "sensors in this zone."
                    )

                elif latest.unit.lower() == "vwc":
                    moisture = float(latest.value)

                else:
                    missing_reason = (
                        f"Unsupported moisture unit: "
                        f"{latest.unit}. Expected vwc."
                    )

            contexts.append(
                LocationAutomationContext(
                    location_id=location_id,
                    zone_id=zone.id,
                    moisture=moisture,
                    low=float(
                        zone.moisture_threshold_low
                    ),
                    high=float(
                        zone.moisture_threshold_high
                    ),
                    missing_reason=missing_reason,
                )
            )

        return contexts
