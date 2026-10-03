import pytest
from app.services.ml_disruption import disruption_predictor
from app.services.anomaly_detector import anomaly_detector
from app.services.alert_classifier import alert_classifier

def test_ml_disruption_prediction():
    res = disruption_predictor.predict_segment_hazard(
        segment_id="test-seg-1",
        rainfall_24h_mm=160.0,
        forecast_rain_mm=90.0,
        slope_degrees=48.0,
        elevation_m=850.0,
        soil_type="LOOSE_SHALE_AND_SILT",
        historical_incidents=4,
        live_reports_count=2
    )
    assert res["probability"] > 0.65
    assert res["severity"] in ("HIGH", "CRITICAL")
    assert res["primary_hazard"] in ("LANDSLIDE", "FLASH_FLOOD")
    assert "contributing_factors" in res

def test_anomaly_detection_cryo_breach():
    reading = {
        "speed_kmh": 45.0,
        "engine_temp_c": 84.0,
        "cryo_temp_c": -8.0, # Dangerous warming above -15C threshold
        "accuracy_m": 2.5
    }
    anomalies = anomaly_detector.analyze_telemetry_reading(
        vehicle_id="v-test",
        reg_number="AS-01-GB-4091",
        reading=reading,
        cargo_type="MEDICAL_OXYGEN"
    )
    assert any(a["type"] == "CRYO_TEMPERATURE_BREACH" for a in anomalies)

def test_alert_classification_and_deduplication():
    # First alert
    c1 = alert_classifier.classify_and_filter(
        alert_type="LANDSLIDE_WARNING",
        base_severity="CRITICAL",
        district_name="Dima Hasao",
        road_code="NH-27",
        commodity_type="MEDICAL_OXYGEN"
    )
    assert c1["is_duplicate_suppressed"] is False
    assert c1["calculated_priority"] == "DEFCON_1_CRITICAL"

    # Second identical alert in window -> suppressed
    c2 = alert_classifier.classify_and_filter(
        alert_type="LANDSLIDE_WARNING",
        base_severity="CRITICAL",
        district_name="Dima Hasao",
        road_code="NH-27",
        commodity_type="MEDICAL_OXYGEN"
    )
    assert c2["is_duplicate_suppressed"] is True
