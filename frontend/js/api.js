// NER-LogiSense: REST API Client
const API_BASE = window.location.origin.includes('8000') || window.location.origin.includes('localhost') 
  ? '/api/v1' 
  : 'http://localhost:8000/api/v1';

const API = {
  token: localStorage.getItem('ner_token') || null,

  setToken(t) {
    this.token = t;
    if (t) localStorage.setItem('ner_token', t);
    else localStorage.removeItem('ner_token');
  },

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return await res.json();
    } catch (e) {
      console.warn(`[API FAIL] ${endpoint}:`, e);
      throw e;
    }
  },

  // Auth
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    this.setToken(data.access_token);
    return data;
  },

  // Network & Accessibility
  async getAccessibilitySummary() {
    return this.request('/network/accessibility-summary');
  },

  async getRoads() {
    return this.request('/network/roads');
  },

  async getRoadSegments(roadId = null, districtId = null) {
    let q = '';
    if (roadId) q += `?road_id=${roadId}`;
    return this.request(`/network/segments${q}`);
  },

  async getBridges() {
    return this.request('/network/bridges');
  },

  async getDistrictConnectivity(districtId) {
    return this.request(`/network/districts/${districtId}/connectivity`);
  },

  async getDistricts(stateCode = null, statusFilter = null) {
    let q = [];
    if (stateCode) q.push(`state_code=${stateCode}`);
    if (statusFilter) q.push(`status_filter=${statusFilter}`);
    const qs = q.length > 0 ? `?${q.join('&')}` : '';
    return this.request(`/network/districts${qs}`);
  },

  // Weather & Risk
  async getCurrentWeather(lat = 26.14, lon = 91.73) {
    return this.request(`/weather/current?lat=${lat}&lon=${lon}`);
  },

  async getSegmentRisks() {
    return this.request('/risk/segments');
  },

  async recomputeRisks() {
    return this.request('/risk/recompute', {
      method: 'POST',
      body: JSON.stringify({ force_all: true })
    });
  },

  // Routing
  async planRoute(payload) {
    return this.request('/routes/plan', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async getEmergencyCorridors() {
    return this.request('/routes/emergency-corridors');
  },

  async assignRoute(tripId, routeOptionId) {
    return this.request('/routes/assign', {
      method: 'POST',
      body: JSON.stringify({ trip_id: tripId, route_option_id: routeOptionId })
    });
  },

  // Driver Safe Route Finder
  async getDriverCorridors() {
    return this.request('/routes/driver-corridors');
  },

  async planDriverSafeRoute(payload) {
    return this.request('/routes/driver-safest', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Vehicles & Tracking
  async getVehicles() {
    return this.request('/vehicles');
  },

  async getTripStatus(tripId) {
    return this.request(`/trips/${tripId}/status`);
  },

  // Incidents
  async getIncidents() {
    return this.request('/incidents');
  },

  async verifyIncident(incidentId, verified = true, updatedSeverity = null) {
    return this.request(`/incidents/${incidentId}/verify`, {
      method: 'POST',
      body: JSON.stringify({ verified, updated_severity: updatedSeverity })
    });
  },

  async resolveIncident(incidentId) {
    return this.request(`/incidents/${incidentId}/resolve`, {
      method: 'POST'
    });
  },

  async submitFieldReport(payload) {
    return this.request('/field-reports', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  // Alerts
  async getAlerts() {
    return this.request('/alerts');
  },

  async getEmergencyOverview() {
    return this.request('/dashboards/emergency-overview');
  },

  // Offline Sync
  async syncBatch(queueItems, deviceId = 'RUGGED-FIELD-TAB-AS04') {
    return this.request('/sync/queue', {
      method: 'POST',
      body: JSON.stringify({
        device_id: deviceId,
        sync_session_id: `SYNC-${Date.now()}`,
        queue_items: queueItems
      })
    });
  }
};
