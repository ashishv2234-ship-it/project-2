// NER-LogiSense: Live WebSocket Stream Manager
class LiveStreamManager {
  constructor() {
    this.wsTelemetry = null;
    this.wsAlerts = null;
    this.isConnected = false;
    this.listeners = new Map();
  }

  init() {
    const loc = window.location;
    const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = loc.host || 'localhost:8000';
    
    // Connect Telemetry Stream
    try {
      this.wsTelemetry = new WebSocket(`${proto}//${host}/ws/telemetry`);
      this.wsTelemetry.onopen = () => {
        this.isConnected = true;
        this.emit('connection_status', { channel: 'telemetry', status: 'CONNECTED' });
      };
      this.wsTelemetry.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('telemetry', data);
        } catch (e) {}
      };
      this.wsTelemetry.onclose = () => {
        this.emit('connection_status', { channel: 'telemetry', status: 'DISCONNECTED' });
        setTimeout(() => this.init(), 5000);
      };
    } catch (e) {
      console.warn('[WS TELEMETRY] Initial fallback');
    }

    // Connect Alert Stream
    try {
      this.wsAlerts = new WebSocket(`${proto}//${host}/ws/alerts`);
      this.wsAlerts.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.emit('alert', data);
        } catch (e) {}
      };
    } catch (e) {
      console.warn('[WS ALERTS] Initial fallback');
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event, payload) {
    if (this.listeners.has(event)) {
      for (const cb of this.listeners.get(event)) {
        cb(payload);
      }
    }
  }
}

const liveStream = new LiveStreamManager();
