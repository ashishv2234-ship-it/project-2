from app.schemas.auth import LoginRequest, Token, TokenRefreshRequest, OTPRequest, OTPVerify
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PreferencesUpdate
from app.schemas.network import (
    RoadResponse, RoadSegmentResponse, BridgeResponse, 
    RoadStatusEventCreate, DistrictConnectivityResponse, DistrictInfoResponse, AccessibilitySummaryResponse
)
from app.schemas.weather import (
    WeatherCurrentResponse, WeatherForecastResponse, WarningResponse, 
    SegmentRiskResponse, DistrictRiskSummaryResponse, RiskRecomputeRequest
)
from app.schemas.routing import (
    RoutePlanRequest, RouteOptionResponse, RoutePlanResult, 
    RouteAssignRequest, RouteReoptimizeRequest, EmergencyCorridorResponse,
    DriverRoutePlanRequest, DriverTurnStep, DriverSafetyChecklist, DriverSafeRouteResponse
)
from app.schemas.vehicles import (
    VehicleCreate, VehicleResponse, GPSReadingCreate, GPSBatchIngestRequest,
    ConsignmentCreate, ConsignmentResponse, TripCreate, TripResponse, 
    DeliveryProofCreate, GeofenceCreate
)
from app.schemas.incidents import (
    IncidentCreate, IncidentUpdate, IncidentVerifyRequest, IncidentResponse, 
    FieldReportCreate, FieldReportResponse, MediaUploadResponse
)
from app.schemas.alerts import (
    AlertCreate, AlertResponse, AlertNotifyRequest, NotificationResponse, 
    NotificationPreferencesRequest, EmergencyEventCreate, EmergencyEventUpdate, EmergencyEventResponse
)
from app.schemas.dashboards import (
    StateOverviewResponse, DistrictDetailResponse, LogisticsBottleneckItem, 
    EmergencyOverviewResponse, VehicleMovementResponse, AnalyticsDeliveryPerformance, AnalyticsDisruptionTrends
)
from app.schemas.offline_sync import (
    SyncQueueItem, SyncBatchRequest, SyncBatchResponse, SyncItemResult, 
    DeltaSyncRequest, DeltaSyncResponse
)
