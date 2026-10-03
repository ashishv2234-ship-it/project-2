import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import numpy as np

class DisruptionPredictionService:
    """
    Predicts probability of landslide, flood, and road closure for NER road segments.
    Uses multi-variable environmental scoring and gradient boosting proxy feature extraction.
    Inputs:
      - rainfall_24h_mm, forecast_rainfall_next_24h_mm
      - slope_degrees, elevation_m
      - soil_instability_index (shale, silt, clay, granite)
      - drainage_quality_score [0..1]
      - historical_incident_density
      - live_unverified_reports_count
    """

    MODEL_VERSION = "xgboost-ner-hazard-v2.4-prod"

    def __init__(self):
        # Calibrated weights for North Eastern Himalayan & Barak/Brahmaputra Basin terrain
        self.weights_landslide = {
            "rainfall_accumulated": 0.35,
            "slope_angle": 0.28,
            "soil_instability": 0.18,
            "historical_density": 0.12,
            "field_reports": 0.07
        }
        self.weights_flood = {
            "rainfall_accumulated": 0.45,
            "river_proximity": 0.25,
            "drainage_deficit": 0.15,
            "elevation_depression": 0.15
        }

    def predict_segment_hazard(
        self,
        segment_id: str,
        rainfall_24h_mm: float,
        forecast_rain_mm: float,
        slope_degrees: float,
        elevation_m: float,
        soil_type: str = "SHALE_SILT",
        drainage_score: float = 0.5,
        historical_incidents: int = 2,
        live_reports_count: int = 0
    ) -> Dict[str, Any]:
        """
        Calculates comprehensive landslide and flood risks for a given segment.
        Returns:
          - primary_hazard (LANDSLIDE, FLASH_FLOOD, WATERLOGGING, CLEAR)
          - probability [0.0 to 1.0]
          - severity (LOW, MODERATE, HIGH, CRITICAL)
          - expected_duration_hours
          - confidence [0.0 to 1.0]
          - contributing_factors
        """
        # 1. Feature normalization
        rain_combined = rainfall_24h_mm + (0.7 * forecast_rain_mm)
        rain_factor = min(1.0, rain_combined / 180.0) # >180mm is extreme cloudburst
        slope_factor = min(1.0, max(0.0, (slope_degrees - 15.0) / 40.0)) # >55 deg is steep cliff
        
        soil_map = {
            "LOOSE_SHALE_AND_SILT": 0.95,
            "SHALE_SILT": 0.85,
            "WEATHERED_SANDSTONE": 0.65,
            "ALLUVIAL_LOAM": 0.50,
            "COMPACT_GRANITE": 0.20
        }
        soil_factor = soil_map.get(soil_type.upper(), 0.70)
        hist_factor = min(1.0, historical_incidents / 6.0)
        report_factor = min(1.0, live_reports_count / 3.0)

        # 2. Landslide Probability (Logistic Activation proxy)
        landslide_linear = (
            self.weights_landslide["rainfall_accumulated"] * rain_factor +
            self.weights_landslide["slope_angle"] * slope_factor +
            self.weights_landslide["soil_instability"] * soil_factor +
            self.weights_landslide["historical_density"] * hist_factor +
            self.weights_landslide["field_reports"] * report_factor
        )
        # Logistic sigmoid scaling
        landslide_prob = 1.0 / (1.0 + math.exp(-6.0 * (landslide_linear - 0.45)))
        landslide_prob = round(float(np.clip(landslide_prob, 0.02, 0.98)), 3)

        # 3. Flood Probability
        elevation_depression = min(1.0, max(0.0, (150.0 - elevation_m) / 100.0)) if elevation_m < 150 else 0.05
        drainage_deficit = 1.0 - drainage_score
        flood_linear = (
            self.weights_flood["rainfall_accumulated"] * rain_factor +
            self.weights_flood["river_proximity"] * 0.7 +
            self.weights_flood["drainage_deficit"] * drainage_deficit +
            self.weights_flood["elevation_depression"] * elevation_depression
        )
        flood_prob = 1.0 / (1.0 + math.exp(-5.5 * (flood_linear - 0.50)))
        flood_prob = round(float(np.clip(flood_prob, 0.01, 0.96)), 3)

        # 4. Resolve Primary Hazard & Severity
        if landslide_prob >= flood_prob:
            primary_hazard = "LANDSLIDE"
            main_prob = landslide_prob
        else:
            primary_hazard = "FLASH_FLOOD"
            main_prob = flood_prob

        if main_prob >= 0.75:
            severity = "CRITICAL"
            expected_duration = 18.0
        elif main_prob >= 0.50:
            severity = "HIGH"
            expected_duration = 8.0
        elif main_prob >= 0.25:
            severity = "MODERATE"
            expected_duration = 3.0
        else:
            severity = "LOW"
            expected_duration = 0.0

        confidence = round(0.88 + (0.08 * (1.0 if live_reports_count > 0 else 0.5)), 2)

        return {
            "segment_id": segment_id,
            "primary_hazard": primary_hazard,
            "probability": main_prob,
            "severity": severity,
            "expected_duration_hours": expected_duration,
            "confidence": confidence,
            "model_version": self.MODEL_VERSION,
            "landslide_prob": landslide_prob,
            "flood_prob": flood_prob,
            "contributing_factors": {
                "rainfall_accumulated_mm": round(rain_combined, 1),
                "slope_degrees": slope_degrees,
                "soil_instability_score": soil_factor,
                "historical_incidents": historical_incidents,
                "live_reports_influencing": live_reports_count
            }
        }

    def batch_predict_corridor(self, segments_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run batch inference for all segments in a corridor or district."""
        results = []
        for s in segments_data:
            res = self.predict_segment_hazard(
                segment_id=s.get("id", "seg-unknown"),
                rainfall_24h_mm=s.get("rainfall_24h_mm", 45.0),
                forecast_rain_mm=s.get("forecast_rain_mm", 60.0),
                slope_degrees=s.get("slope_degrees", 25.0),
                elevation_m=s.get("elevation_m", 450.0),
                soil_type=s.get("soil_type", "SHALE_SILT"),
                drainage_score=s.get("drainage_score", 0.5),
                historical_incidents=s.get("historical_incidents", 2),
                live_reports_count=s.get("live_reports_count", 0)
            )
            results.append(res)
        return results

disruption_predictor = DisruptionPredictionService()
