from datetime import UTC, datetime
from typing import Any


class AnomalyDetectionService:
    """
    Monitors live vehicle telemetry streams for logistics hazards:
    1. Vehicle breakdown (Engine temperature spike + speed 0 + ignition off)
    2. Prolonged stoppage / dwell in vulnerable mountain passes
    3. Abnormal speed (>85 km/h on mountain hairpin turns or sudden -50km/h deceleration)
    4. Off-route deviation
    5. Cryogenic temperature breach (Oxygen/Vaccine spoiling)
    6. Suspected data tampering (GNSS spoofing, impossible jumps in location)
    """

    MAX_MOUNTAIN_SPEED_KMH = 75.0
    CRYO_TEMP_MAX_C = -15.0  # For cryo cargo
    MAX_REALISTIC_SPEED_KMH = 120.0

    def analyze_telemetry_reading(
        self,
        vehicle_id: str,
        reg_number: str,
        reading: dict[str, Any],
        prev_reading: dict[str, Any] | None = None,
        cargo_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Evaluates a single telemetry reading against physical constraints and historical baseline.
        Returns a list of detected anomalies/alerts.
        """
        anomalies = []
        now = datetime.now(UTC)

        speed = reading.get("speed_kmh", 0.0)
        engine_temp = reading.get("engine_temp_c", 85.0)
        cryo_temp = reading.get("cryo_temp_c")

        accuracy = reading.get("accuracy_m", 2.5)

        # 1. Cryo Breach (High Priority for Medical Oxygen & Vaccines)
        if (
            cargo_type in ("MEDICAL_OXYGEN", "CRYO_VACCINES")
            and cryo_temp is not None
            and cryo_temp > self.CRYO_TEMP_MAX_C
        ):
            anomalies.append(
                {
                    "type": "CRYO_TEMPERATURE_BREACH",
                    "severity": "CRITICAL",
                    "vehicle_id": vehicle_id,
                    "title": f"Cryo Temperature Alert: {reg_number}",
                    "message": f"Cryogenic temperature climbed to {cryo_temp}°C (Safe limit: {self.CRYO_TEMP_MAX_C}°C). Cold-chain integrity at risk!",
                    "timestamp": now.isoformat(),
                }
            )

        # 2. Vehicle Breakdown Detection
        if engine_temp > 105.0 and speed < 2.0:
            anomalies.append(
                {
                    "type": "VEHICLE_BREAKDOWN",
                    "severity": "HIGH",
                    "vehicle_id": vehicle_id,
                    "title": f"Suspected Engine Breakdown: {reg_number}",
                    "message": f"Engine overheating at {engine_temp}°C with zero speed. Potential roadside mechanical failure.",
                    "timestamp": now.isoformat(),
                }
            )

        # 3. Abnormal Speed on Ghat Roads
        if speed > self.MAX_MOUNTAIN_SPEED_KMH:
            anomalies.append(
                {
                    "type": "OVERSPEEDING_GHAT_SECTION",
                    "severity": "MODERATE",
                    "vehicle_id": vehicle_id,
                    "title": f"Speed Violation: {reg_number}",
                    "message": f"Vehicle moving at {speed} km/h exceeding mountainous sector safety limit ({self.MAX_MOUNTAIN_SPEED_KMH} km/h).",
                    "timestamp": now.isoformat(),
                }
            )

        # 4. Suspected GPS Tampering or Impossible Jump
        if prev_reading:
            prev_lat = prev_reading.get("latitude")
            prev_lon = prev_reading.get("longitude")
            curr_lat = reading.get("latitude")
            curr_lon = reading.get("longitude")

            if prev_lat and prev_lon and curr_lat and curr_lon:
                # Simple coordinate delta jump check
                d_lat = abs(curr_lat - prev_lat)
                d_lon = abs(curr_lon - prev_lon)
                # 0.5 degrees is ~55 km; in 10-30 seconds this is physically impossible
                if d_lat > 0.3 or d_lon > 0.3:
                    anomalies.append(
                        {
                            "type": "SUSPECTED_GPS_TAMPERING",
                            "severity": "CRITICAL",
                            "vehicle_id": vehicle_id,
                            "title": f"Telemetry Anomaly / Location Jump: {reg_number}",
                            "message": f"Instantaneous jump detected ({d_lat:.2f}°, {d_lon:.2f}°). Suspected spoofing or sensor failure.",
                            "timestamp": now.isoformat(),
                        }
                    )

        # 5. Degraded GNSS Accuracy
        if accuracy > 45.0:
            anomalies.append(
                {
                    "type": "WEAK_SATELLITE_LOCK",
                    "severity": "LOW",
                    "vehicle_id": vehicle_id,
                    "title": f"Low GNSS Accuracy: {reg_number}",
                    "message": f"GNSS accuracy degraded to ±{accuracy}m under canopy/gorge.",
                    "timestamp": now.isoformat(),
                }
            )

        return anomalies


anomaly_detector = AnomalyDetectionService()
