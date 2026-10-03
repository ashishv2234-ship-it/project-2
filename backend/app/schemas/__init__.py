from app.schemas.alerts import (
    AlertCreate,
    AlertNotifyRequest,
    AlertResponse,
    EmergencyEventCreate,
    EmergencyEventResponse,
    EmergencyEventUpdate,
    NotificationPreferencesRequest,
    NotificationResponse,
)
from app.schemas.auth import (
    LoginRequest,
    OTPRequest,
    OTPVerify,
    Token,
    TokenRefreshRequest,
)
from app.schemas.dashboards import (
    AnalyticsDeliveryPerformance,
    AnalyticsDisruptionTrends,
    DistrictDetailResponse,
    EmergencyOverviewResponse,
    LogisticsBottleneckItem,
    StateOverviewResponse,
    VehicleMovementResponse,
)
from app.schemas.incidents import (
    FieldReportCreate,
    FieldReportResponse,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdate,
    IncidentVerifyRequest,
    MediaUploadResponse,
)
from app.schemas.network import (
    AccessibilitySummaryResponse,
    BridgeResponse,
    DistrictConnectivityResponse,
    DistrictInfoResponse,
    RoadResponse,
    RoadSegmentResponse,
    RoadStatusEventCreate,
)
from app.schemas.offline_sync import (
    DeltaSyncRequest,
    DeltaSyncResponse,
    SyncBatchRequest,
    SyncBatchResponse,
    SyncItemResult,
    SyncQueueItem,
)
from app.schemas.routing import (
    DriverRoutePlanRequest,
    DriverSafeRouteResponse,
    DriverSafetyChecklist,
    DriverTurnStep,
    EmergencyCorridorResponse,
    RouteAssignRequest,
    RouteOptionResponse,
    RoutePlanRequest,
    RoutePlanResult,
    RouteReoptimizeRequest,
)
from app.schemas.user import PreferencesUpdate, UserCreate, UserResponse, UserUpdate
from app.schemas.vehicles import (
    ConsignmentCreate,
    ConsignmentResponse,
    DeliveryProofCreate,
    GeofenceCreate,
    GPSBatchIngestRequest,
    GPSReadingCreate,
    TripCreate,
    TripResponse,
    VehicleCreate,
    VehicleResponse,
)
from app.schemas.weather import (
    DistrictRiskSummaryResponse,
    RiskRecomputeRequest,
    SegmentRiskResponse,
    WarningResponse,
    WeatherCurrentResponse,
    WeatherForecastResponse,
)
