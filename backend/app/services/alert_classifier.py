import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any


class AlertClassificationService:
    """
    Classifies, deduplicates, and aggregates alerts across NER regions.
    Prioritizes according to:
      - Commodity criticality (e.g. Cryo Oxygen vs Standard Cargo)
      - Corridor significance (Strategic NH-27, NH-6, NH-102 border arteries)
      - Disaster severity (Red alert vs caution)
    """

    def __init__(self):
        # Cache for recent alerts to detect duplicates within 30-minute window
        self._recent_alert_hashes: dict[str, datetime] = {}

    def generate_dedup_hash(
        self, alert_type: str, district: str, road_code: str | None = None
    ) -> str:
        key = f"{alert_type.upper()}:{district.lower()}:{str(road_code).lower()}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()

    def classify_and_filter(
        self,
        alert_type: str,
        base_severity: str,
        district_name: str,
        road_code: str | None = None,
        commodity_type: str | None = None,
        affected_population_est: int = 5000,
    ) -> dict[str, Any]:
        """
        Calculates priority score and checks for duplicate suppression.
        """
        now = datetime.now(UTC)
        dedup_hash = self.generate_dedup_hash(alert_type, district_name, road_code)

        # Check deduplication window (30 mins)
        is_duplicate = False
        if dedup_hash in self._recent_alert_hashes:
            last_time = self._recent_alert_hashes[dedup_hash]
            if now - last_time < timedelta(minutes=30):
                is_duplicate = True

        if not is_duplicate:
            self._recent_alert_hashes[dedup_hash] = now

        # Strategic Corridors in NER
        strategic_corridors = {"NH-27", "NH-6", "NH-102", "NH-13", "NH-10", "NH-29"}
        is_strategic = road_code and road_code.upper() in strategic_corridors

        # Commodity weight
        commodity_weights = {
            "MEDICAL_OXYGEN": 35,
            "CRYO_VACCINES": 30,
            "DISASTER_RELIEF": 25,
            "POL_FUEL": 20,
            "FOODGRAINS_FCI": 15,
        }
        comm_score = commodity_weights.get(str(commodity_type).upper(), 5)

        # Severity score
        severity_scores = {"CRITICAL": 50, "HIGH": 30, "MODERATE": 15, "LOW": 5}
        sev_score = severity_scores.get(base_severity.upper(), 20)

        # Strategic corridor boost
        corridor_score = 25 if is_strategic else 10

        # Total priority score [0 to 100+]
        total_priority = sev_score + comm_score + corridor_score

        if total_priority >= 80:
            final_priority = "DEFCON_1_CRITICAL"
        elif total_priority >= 55:
            final_priority = "HIGH"
        elif total_priority >= 35:
            final_priority = "MODERATE"
        else:
            final_priority = "LOW"

        return {
            "is_duplicate_suppressed": is_duplicate,
            "dedup_key": dedup_hash,
            "calculated_priority": final_priority,
            "priority_score": total_priority,
            "is_strategic_corridor": is_strategic,
            "broadcast_channels": ["WEBSOCKET", "PUSH"]
            + (["SMS"] if final_priority in ("HIGH", "DEFCON_1_CRITICAL") else []),
        }


alert_classifier = AlertClassificationService()
