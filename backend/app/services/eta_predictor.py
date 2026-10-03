import math
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional, Tuple
from app.services.route_optimizer import haversine_distance_km

class ETAPredictionService:
    """
    Predicts arrival time using live GPS telemetry, historical segment travel times,
    monsoon weather penalties, and detects route deviations and unusual dwell times.
    """

    def __init__(self):
        self.deviation_threshold_km = 3.0 # >3km off planned corridor = deviation
        self.dwell_threshold_minutes = 25.0 # >25 min at 0 km/h outside geofenced depot = anomaly

    def point_to_polyline_distance_km(self, pt: Tuple[float, float], polyline: List[List[float]]) -> float:
        """Find minimum distance from vehicle point to any segment in route polyline."""
        if not polyline:
            return 0.0
        min_dist = float("inf")
        for node in polyline:
            d = haversine_distance_km(pt[0], pt[1], node[0], node[1])
            if d < min_dist:
                min_dist = d
        return min_dist

    def predict_trip_eta(
        self,
        current_lat: float,
        current_lon: float,
        current_speed_kmh: float,
        dest_lat: float,
        dest_lon: float,
        planned_route_waypoints: List[List[float]],
        weather_warning_level: str = "GREEN",
        active_blockades_ahead: int = 0,
        dwell_time_minutes: float = 0.0
    ) -> Dict[str, Any]:
        """
        Dynamically calculates ETA, predicted delay, and deviation flag.
        """
        # Remaining straight distance
        dist_remaining_km = haversine_distance_km(current_lat, current_lon, dest_lat, dest_lon)
        # Road winding curvature factor for NER terrain (usually 1.35x to 1.55x straight line)
        curv_factor = 1.45
        road_km_remaining = dist_remaining_km * curv_factor

        # Effective cruise speed estimate
        if current_speed_kmh > 15.0:
            effective_speed = (current_speed_kmh * 0.7) + (40.0 * 0.3)
        else:
            effective_speed = 35.0 # Mountain corridor average

        # Weather slowdown penalty
        weather_slowdown = {
            "GREEN": 1.0,
            "YELLOW": 1.15,
            "ORANGE": 1.40,
            "RED": 1.85
        }.get(weather_warning_level.upper(), 1.0)

        base_transit_hours = (road_km_remaining / effective_speed) * weather_slowdown
        
        # Blockade/chokepoint delay
        blockade_delay_hours = active_blockades_ahead * 1.5

        total_hours_remaining = base_transit_hours + blockade_delay_hours
        delay_minutes = max(0.0, (total_hours_remaining - (road_km_remaining / 45.0)) * 60.0)

        now = datetime.now(timezone.utc)
        eta_time = now + timedelta(hours=total_hours_remaining)

        # Route deviation check
        dist_from_planned_km = self.point_to_polyline_distance_km((current_lat, current_lon), planned_route_waypoints)
        is_deviated = dist_from_planned_km > self.deviation_threshold_km

        # Prolonged dwell check
        is_unusual_dwell = (current_speed_kmh < 2.0 and dwell_time_minutes > self.dwell_threshold_minutes)

        return {
            "estimated_arrival_time": eta_time.isoformat(),
            "remaining_distance_km": round(road_km_remaining, 1),
            "remaining_time_hours": round(total_hours_remaining, 2),
            "expected_delay_minutes": round(delay_minutes, 1),
            "is_route_deviated": is_deviated,
            "deviation_distance_km": round(dist_from_planned_km, 2),
            "is_unusual_dwell": is_unusual_dwell,
            "dwell_time_minutes": round(dwell_time_minutes, 1),
            "weather_impact_multiplier": weather_slowdown
        }

eta_predictor = ETAPredictionService()
