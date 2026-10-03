// NER-LogiSense: Interactive Tactical GIS Map Engine
class TacticalMap {
  constructor(containerId = 'gis-map') {
    this.containerId = containerId;
    this.map = null;
    this.baseLayers = {};
    this.currentBasemap = 'tactical-dark';
    this.layers = {
      roads: null,
      bridges: null,
      convoys: null,
      hazards: null,
      radar: null,
      districts: null,
      plannedRoute: null
    };
    this.vehicleMarkers = new Map();
  }

  init(center = [25.85, 92.5], zoom = 8) {
    if (this.map) return;

    // Tactical Map Container Initialization
    this.map = L.map(this.containerId, {
      zoomControl: false,
      attributionControl: false,
      minZoom: 6,
      maxZoom: 18
    }).setView(center, zoom);

    L.control.zoom({ position: 'bottomright' }).addTo(this.map);

    // Basemap 1: Tactical Dark Canvas (Esri World Dark Gray Base & Reference - Zero API Key, No Watermark)
    const esriDarkBase = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      maxNativeZoom: 16,
      maxZoom: 18,
      attribution: 'Esri, HERE, Garmin'
    });
    const esriDarkRef = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
      maxNativeZoom: 16,
      maxZoom: 18,
      opacity: 0.85
    });
    this.baseLayers['tactical-dark'] = L.layerGroup([esriDarkBase, esriDarkRef]);

    // Basemap 2: Satellite Terrain Hybrid (Esri World Imagery + Reference)
    const esriSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxNativeZoom: 18,
      maxZoom: 18,
      attribution: 'Esri, Maxar, Earthstar Geographics'
    });
    this.baseLayers['satellite'] = L.layerGroup([esriSat, esriDarkRef]);

    // Basemap 3: OpenStreetMap High-Contrast Tactical Dark
    const osmDark = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      className: 'osm-tactical-filter',
      attribution: '&copy; OpenStreetMap contributors'
    });
    this.baseLayers['osm-dark'] = L.layerGroup([osmDark]);

    // Set Default Basemap (Tactical Dark Canvas)
    this.baseLayers['tactical-dark'].addTo(this.map);

    // Initialize Tactical GIS Overlay Groups
    this.layers.roads = L.layerGroup().addTo(this.map);
    this.layers.bridges = L.layerGroup().addTo(this.map);
    this.layers.convoys = L.layerGroup().addTo(this.map);
    this.layers.hazards = L.layerGroup().addTo(this.map);
    this.layers.radar = L.layerGroup().addTo(this.map);
    this.layers.districts = L.layerGroup().addTo(this.map);
    this.layers.plannedRoute = L.layerGroup().addTo(this.map);
    this.layers.boundary = L.layerGroup().addTo(this.map);

    // Apply official Government of India boundary masking
    fetch('https://raw.githubusercontent.com/datameet/maps/master/Country/india-land-simplified.geojson')
      .then(res => res.json())
      .then(data => {
        // Thick dark stroke to hide underlying incorrect tile borders
        L.geoJSON(data, {
          style: { color: '#0b1326', weight: 14, fillOpacity: 0, opacity: 1 }
        }).addTo(this.layers.boundary);
        // Correct boundary stroke
        L.geoJSON(data, {
          style: { color: '#334155', weight: 2, fillOpacity: 0, dashArray: '4,4' }
        }).addTo(this.layers.boundary);
      }).catch(e => console.warn('Failed to load official boundary', e));

    this.renderWeatherRadarSimulation();
  }

  setBasemap(styleName) {
    if (!this.baseLayers[styleName]) return;
    Object.values(this.baseLayers).forEach(layer => {
      if (this.map.hasLayer(layer)) this.map.removeLayer(layer);
    });
    this.baseLayers[styleName].addTo(this.map);
    this.currentBasemap = styleName;
  }

  toggleLayer(layerKey, isVisible) {
    const layer = this.layers[layerKey];
    if (!layer) return;
    if (isVisible) {
      if (!this.map.hasLayer(layer)) this.map.addLayer(layer);
    } else {
      if (this.map.hasLayer(layer)) this.map.removeLayer(layer);
    }
  }

  renderWeatherRadarSimulation() {
    this.layers.radar.clearLayers();

    // Radar watch circles over high-precipitation catchment zones
    const radarHotspots = [
      { coords: [25.188, 92.997], radius: 35000, color: '#dc2626', name: 'Barail Mountain Catchment' },
      { coords: [25.298, 91.582], radius: 45000, color: '#ea580c', name: 'Cherrapunji Orographic Surge' }
    ];

    radarHotspots.forEach(spot => {
      L.circle(spot.coords, {
        radius: spot.radius,
        color: spot.color,
        fillColor: spot.color,
        fillOpacity: 0.12,
        weight: 1.5,
        dashArray: '4, 8'
      }).bindTooltip(`<b>IMD Radar Watch:</b> ${spot.name}`, { sticky: true }).addTo(this.layers.radar);
    });
  }

  renderRoadNetwork(segments) {
    this.layers.roads.clearLayers();

    segments.forEach(seg => {
      let coords = [];
      if (seg.geometry_geojson) {
        try {
          coords = JSON.parse(seg.geometry_geojson);
        } catch (e) {}
      }
      if (!coords || coords.length === 0) {
        coords = [
          [seg.start_lat, seg.start_lon],
          [seg.end_lat, seg.end_lon]
        ];
      }

      let color = '#16a34a'; // OPEN
      let weight = 4;
      let dashArray = null;

      if (seg.current_status === 'RESTRICTED') {
        color = '#d97706';
        weight = 4;
        dashArray = '6, 6';
      } else if (seg.current_status === 'BLOCKED') {
        color = '#dc2626';
        weight = 5;
      } else if (seg.current_status === 'HIGH_RISK') {
        color = '#ea580c';
        weight = 4.5;
      }

      const polyline = L.polyline(coords, {
        color,
        weight,
        opacity: 0.9,
        dashArray
      }).addTo(this.layers.roads);

      const statusBadge = `<span class="badge-tag ${seg.current_status === 'OPEN' ? 'badge-open' : (seg.current_status === 'RESTRICTED' ? 'badge-restricted' : 'badge-blocked')}">${seg.current_status}</span>`;

      polyline.bindPopup(`
        <div style="background:#0b1326; color:#dae2fd; padding:12px; border-radius:6px; font-size:12px; min-width:230px; border-left:4px solid ${color};">
          <div style="font-weight:700; font-size:13px; margin-bottom:4px;">${seg.start_point_name} → ${seg.end_point_name}</div>
          <div style="margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <span style="color:#94a3b8;">Status:</span> ${statusBadge}
          </div>
          <div style="color:#94a3b8; font-size:11px; display:flex; flex-direction:column; gap:3px;">
            <div>Length: <b style="color:#dae2fd;">${seg.length_km} km</b></div>
            <div>Elevation: <b style="color:#dae2fd;">${seg.elevation_m} m</b> | Slope: <b>${seg.slope_degrees}°</b></div>
            <div>Slide Risk: <b style="color:${seg.landslide_risk_score > 0.6 ? '#f87171' : '#7bd8b1'};">${Math.round(seg.landslide_risk_score * 100)}%</b></div>
            <div>Expected Delay: <b style="color:#fca5a5;">+${seg.expected_delay_min} min</b></div>
          </div>
        </div>
      `);
    });
  }

  renderBridges(bridges) {
    this.layers.bridges.clearLayers();

    bridges.forEach(b => {
      const isOperational = b.status === 'OPERATIONAL';
      const isRestricted = b.status === 'WEIGHT_RESTRICTED';
      const statusColor = isOperational ? '#0284c7' : (isRestricted ? '#d97706' : '#dc2626');

      // Crisp vector SVG suspension bridge icon (eliminates missing webfont ligatures and text overflow)
      const bridgeIcon = L.divIcon({
        className: 'bridge-marker',
        html: `
          <div style="background:${statusColor}; width:26px; height:26px; border-radius:6px; border:2px solid #ffffff; display:flex; align-items:center; justify-content:center; color:#ffffff; box-shadow:0 3px 8px rgba(0,0,0,0.6); cursor:pointer;" title="${b.name}">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 17h18M3 12h18M6 12v5M18 12v5M10 12v5M14 12v5M4 12c3.5-6 7.5-7.5 8-7.5s4.5 1.5 8 7.5"/>
            </svg>
          </div>
        `,
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      });

      const m = L.marker([b.lat, b.lon], { icon: bridgeIcon, zIndexOffset: 60 }).addTo(this.layers.bridges);

      m.bindTooltip(`
        <div style="font-weight:700; color:#dae2fd;">${b.name}</div>
        <div style="font-size:10px; color:#94a3b8;">Cap: <b>${b.load_capacity_mt} MT</b> | <span style="color:${statusColor}; font-weight:600;">${b.status}</span></div>
      `, { direction: 'top', offset: [0, -10] });

      m.bindPopup(`
        <div style="background:#0b1326; color:#dae2fd; padding:12px; border-radius:6px; font-size:12px; min-width:220px; border-left:4px solid ${statusColor};">
          <div style="font-weight:800; font-size:13px; color:#dae2fd; margin-bottom:4px;">${b.name}</div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <span style="color:#94a3b8;">Condition:</span>
            <span class="badge-tag ${isOperational ? 'badge-open' : (isRestricted ? 'badge-restricted' : 'badge-blocked')}">${b.status}</span>
          </div>
          <div style="color:#94a3b8; font-size:11px; display:flex; flex-direction:column; gap:3px;">
            <div>Max Load Capacity: <b style="color:#7bd8b1;">${b.load_capacity_mt} MT</b></div>
            <div>Structural Health: <b style="color:${b.structural_health_index > 80 ? '#7bd8b1' : '#f59e0b'};">${b.structural_health_index}%</b></div>
            <div>Coordinates: <span class="coord">${b.lat.toFixed(3)}°N, ${b.lon.toFixed(3)}°E</span></div>
          </div>
        </div>
      `);

      // Interactive zoom to bridge focus on click
      m.on('click', () => {
        if (this.map.getZoom() < 11) {
          this.map.setView([b.lat, b.lon], 12);
        }
      });
    });
  }

  renderDistricts(districts) {
    this.layers.districts.clearLayers();

    districts.forEach(d => {
      // Determine color based on connectivity status or isolation index
      let statusColor = '#10b981'; // Green (Connected/Normal)
      if (d.connectivity_status === 'SEVERED' || d.isolation_index >= 0.65) {
        statusColor = '#dc2626'; // Red (Severed)
      } else if (d.connectivity_status === 'RESTRICTED' || (d.isolation_index >= 0.35 && d.isolation_index < 0.65)) {
        statusColor = '#ea580c'; // Orange (Restricted)
      }

      // Animated pulsing icon
      const districtIcon = L.divIcon({
        className: 'district-marker',
        html: `
          <div style="position:relative; width:40px; height:40px; display:flex; align-items:center; justify-content:center; cursor:pointer;" title="${d.name}">
            <div style="position:absolute; width:100%; height:100%; border-radius:50%; background:${statusColor}; opacity:0.35; animation:pulse-dot 2s infinite;"></div>
            <div style="background:#0b1326; width:28px; height:28px; border-radius:50%; border:2px solid ${statusColor}; display:flex; align-items:center; justify-content:center; position:relative; z-index:2; box-shadow:0 0 10px ${statusColor};">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="${statusColor}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2L2 7l10 5 10-5-10-5Z"></path>
                <path d="M2 17l10 5 10-5"></path>
                <path d="M2 12l10 5 10-5"></path>
              </svg>
            </div>
          </div>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 20]
      });

      const m = L.marker([d.center_lat, d.center_lon], { icon: districtIcon, zIndexOffset: 70 }).addTo(this.layers.districts);

      m.bindTooltip(`
        <div style="font-weight:800; color:#dae2fd;">${d.name}</div>
        <div style="font-size:10px; color:#94a3b8;">Isolation Index: <b style="color:${statusColor}">${d.isolation_index.toFixed(2)}</b></div>
      `, { direction: 'top', offset: [0, -15] });

      m.bindPopup(`
        <div style="background:#0b1326; color:#dae2fd; padding:12px; border-radius:6px; font-size:12px; min-width:240px; border-left:4px solid ${statusColor};">
          <div style="font-weight:800; font-size:14px; color:#dae2fd; margin-bottom:4px;">${d.name}</div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <span style="color:#94a3b8;">Status:</span>
            <span style="background:${statusColor}22; color:${statusColor}; padding:2px 6px; border-radius:4px; font-weight:700; font-size:10px; border:1px solid ${statusColor};">${d.connectivity_status}</span>
          </div>
          <div style="color:#94a3b8; font-size:11px; display:flex; flex-direction:column; gap:4px;">
            <div>Isolation Index: <b style="color:${statusColor};">${d.isolation_index.toFixed(2)}</b></div>
            <div>Critical Facilities: <b style="color:#dae2fd;">${d.critical_facilities_count}</b></div>
            <div style="margin-top:6px; padding-top:6px; border-top:1px solid #1e293b;">
              <div style="color:#dae2fd; font-weight:600; margin-bottom:2px;">Primary Chokepoint:</div>
              <div style="color:#94a3b8; line-height:1.4;">${d.problem_summary}</div>
            </div>
          </div>
        </div>
      `);
    });
  }

  renderHazards(incidents) {
    this.layers.hazards.clearLayers();

    incidents.forEach(inc => {
      const isCritical = inc.severity === 'CRITICAL';
      const color = isCritical ? '#dc2626' : (inc.severity === 'HIGH' ? '#ea580c' : '#d97706');

      // Crisp vector SVG warning marker with pulsing radar wave ring
      const hazardIcon = L.divIcon({
        className: 'hazard-marker',
        html: `
          <div style="position:relative; width:30px; height:30px; display:flex; align-items:center; justify-content:center; cursor:pointer;" title="${inc.type} (${inc.severity})">
            <div style="position:absolute; width:100%; height:100%; border-radius:50%; background:${color}; opacity:0.4; animation:pulse-dot 1.5s infinite;"></div>
            <div style="background:${color}; width:24px; height:24px; border-radius:50%; border:2px solid #ffffff; display:flex; align-items:center; justify-content:center; position:relative; z-index:2; box-shadow:0 3px 8px rgba(0,0,0,0.6);">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
          </div>
        `,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
      });

      const m = L.marker([inc.lat, inc.lon], { icon: hazardIcon, zIndexOffset: 120 }).addTo(this.layers.hazards);

      m.bindTooltip(`
        <div style="font-weight:700; color:${color}; text-transform:uppercase;">${inc.type} [${inc.severity}]</div>
        <div style="font-size:10px; color:#dae2fd;">${inc.location_desc}</div>
      `, { direction: 'top', offset: [0, -12] });

      m.bindPopup(`
        <div style="background:#0b1326; color:#dae2fd; padding:12px; border-radius:6px; font-size:12px; min-width:240px; border-left:4px solid ${color};">
          <div style="font-weight:800; font-size:13px; text-transform:uppercase; color:${color}; margin-bottom:4px;">${inc.type} (${inc.severity})</div>
          <div style="font-weight:600; margin-bottom:6px; color:#dae2fd;">${inc.location_desc}</div>
          <p style="color:#bfc7d2; font-size:11px; margin-bottom:8px; line-height:1.4;">${inc.description}</p>
          <div style="font-size:11px; color:#94a3b8; display:flex; justify-content:space-between;">
            <span>Est. Clearance:</span>
            <b style="color:#fca5a5;">${inc.estimated_clearance_hours} hours</b>
          </div>
        </div>
      `);

      // Interactive zoom to hazard focus on click
      m.on('click', () => {
        if (this.map.getZoom() < 11) {
          this.map.setView([inc.lat, inc.lon], 12);
        }
      });
    });
  }

  renderVehicles(vehicles) {
    vehicles.forEach(v => {
      if (!v.last_lat || !v.last_lon) return;

      const isCryo = v.type === 'CRYO_TANKER';
      const bgColor = isCryo ? '#0284c7' : '#059669';

      // Crisp vector SVG truck/convoy marker
      const markerHtml = `
        <div style="background:${bgColor}; border:2px solid #ffffff; border-radius:6px; width:28px; height:28px; display:flex; align-items:center; justify-content:center; color:#fff; box-shadow:0 3px 8px rgba(0,0,0,0.6); cursor:pointer;" title="${v.registration_number}">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M1 3h15v13H1z"/>
            <path d="M16 8h4l3 3v5h-7V8z"/>
            <circle cx="5.5" cy="18.5" r="2.5"/>
            <circle cx="18.5" cy="18.5" r="2.5"/>
          </svg>
        </div>
      `;

      const icon = L.divIcon({
        className: 'vehicle-marker',
        html: markerHtml,
        iconSize: [28, 28],
        iconAnchor: [14, 14]
      });

      if (this.vehicleMarkers.has(v.id)) {
        const m = this.vehicleMarkers.get(v.id);
        m.setLatLng([v.last_lat, v.last_lon]);
      } else {
        const m = L.marker([v.last_lat, v.last_lon], { icon, zIndexOffset: 90 }).addTo(this.layers.convoys);

        m.bindTooltip(`
          <div style="font-weight:700; color:#93ccff;">${v.registration_number}</div>
          <div style="font-size:10px; color:#dae2fd;">${v.type} | ${v.last_speed_kmh} km/h</div>
        `, { direction: 'top', offset: [0, -12] });

        m.bindPopup(`
          <div style="background:#0b1326; color:#dae2fd; padding:12px; border-radius:6px; font-size:12px; min-width:210px; border-left:4px solid ${bgColor};">
            <div style="font-weight:700; font-size:13px; color:#93ccff; margin-bottom:4px;">${v.registration_number}</div>
            <div style="color:#94a3b8; font-size:11px; display:flex; flex-direction:column; gap:3px;">
              <div>Consignment: <b>${v.type}</b></div>
              <div>Telemetry Speed: <b style="color:#7bd8b1;">${v.last_speed_kmh} km/h</b></div>
              ${v.cryo_temp_c !== null ? `<div>Cryo Chamber: <b style="color:#93ccff;">${v.cryo_temp_c}°C</b></div>` : ''}
            </div>
            <div style="margin-top:6px;"><span class="badge-tag badge-open">${v.current_status}</span></div>
          </div>
        `);
        this.vehicleMarkers.set(v.id, m);
      }
    });
  }

  renderPlannedRoute(waypoints, color = '#0284c7') {
    this.layers.plannedRoute.clearLayers();
    if (!waypoints || waypoints.length === 0) return;

    const line = L.polyline(waypoints, {
      color,
      weight: 6,
      opacity: 0.95
    }).addTo(this.layers.plannedRoute);

    this.map.fitBounds(line.getBounds(), { padding: [50, 50] });
  }

  async renderDriverSafeRoute(waypoints, startCoord, endCoord, corridorName, turnSteps = []) {
    this.layers.plannedRoute.clearLayers();
    if (!waypoints || waypoints.length === 0) return;

    let routeLineCoords = waypoints;

    // Attempt to fetch actual road geometry from OSRM to snap to real roads
    try {
      // OSRM expects coordinates in lng,lat format
      const coordString = waypoints.map(wp => `${wp[1].toFixed(5)},${wp[0].toFixed(5)}`).join(';');
      const response = await fetch(`https://router.project-osrm.org/route/v1/driving/${coordString}?overview=full&geometries=geojson`);
      if (response.ok) {
        const data = await response.json();
        if (data.routes && data.routes.length > 0) {
          // OSRM returns GeoJSON which is [lng, lat], Leaflet needs [lat, lng]
          routeLineCoords = data.routes[0].geometry.coordinates.map(coord => [coord[1], coord[0]]);
        }
      }
    } catch (e) {
      console.warn('Failed to fetch OSRM routing, falling back to straight lines', e);
    }

    // Outer glow line
    L.polyline(routeLineCoords, {
      color: '#10b981',
      weight: 9,
      opacity: 0.35,
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(this.layers.plannedRoute);

    // Inner bright tactical safe line
    const line = L.polyline(routeLineCoords, {
      color: '#34d399',
      weight: 5,
      opacity: 1.0,
      dashArray: '8, 6',
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(this.layers.plannedRoute);

    // Start Marker (Origin Green Flag)
    if (startCoord && startCoord[0]) {
      const startMarker = L.circleMarker(startCoord, {
        radius: 8,
        color: '#ffffff',
        weight: 2,
        fillColor: '#10b981',
        fillOpacity: 1
      }).addTo(this.layers.plannedRoute);
      startMarker.bindTooltip(`<b>ORIGIN:</b> Verified Safe Departure`, { permanent: false, direction: 'top' });
    }

    // End Marker (Destination Blue Check)
    if (endCoord && endCoord[0]) {
      const endMarker = L.circleMarker(endCoord, {
        radius: 8,
        color: '#ffffff',
        weight: 2,
        fillColor: '#0284c7',
        fillOpacity: 1
      }).addTo(this.layers.plannedRoute);
      endMarker.bindTooltip(`<b>DESTINATION:</b> Secured Terminal`, { permanent: false, direction: 'top' });
    }

    // Add turn waypoint markers if provided
    turnSteps.forEach((step, idx) => {
      if (step.lat && step.lon) {
        const stepMarker = L.circleMarker([step.lat, step.lon], {
          radius: 5,
          color: '#064e3b',
          weight: 1.5,
          fillColor: '#6ee7b7',
          fillOpacity: 0.9
        }).addTo(this.layers.plannedRoute);
        stepMarker.bindTooltip(`
          <div style="font-size:11px;">
            <b style="color:#0284c7;">Step ${idx + 1}: ${step.road_designation}</b><br/>
            <span>${step.instruction}</span><br/>
            <span style="color:#94a3b8;">${step.step_distance_km} km | ${step.surface_type} | Limit: ${step.speed_advisory_kmh} km/h</span>
          </div>
        `, { direction: 'top' });
      }
    });

    this.map.fitBounds(line.getBounds(), { padding: [60, 60] });
  }

  flyToDistrict(districtKey) {
    const centers = {
      'dima-hasao': { center: [25.18, 93.02], zoom: 10 },
      'east-khasi': { center: [25.57, 91.88], zoom: 10 },
      'champhai': { center: [23.46, 93.33], zoom: 10 },
      'papum-pare': { center: [27.10, 93.62], zoom: 10 },
      'kalimpong': { center: [27.06, 88.47], zoom: 10 },
      'all': { center: [25.85, 92.5], zoom: 8 }
    };
    const target = centers[districtKey] || centers['all'];
    this.map.flyTo(target.center, target.zoom, { duration: 1.2 });
  }

  flyToState(stateCode) {
    const stateCenters = {
      'AS': { center: [26.15, 92.5], zoom: 8 },
      'ML': { center: [25.57, 91.88], zoom: 9 },
      'AR': { center: [27.5, 94.5], zoom: 8 },
      'NL': { center: [26.1, 94.2], zoom: 9 },
      'MN': { center: [24.8, 93.9], zoom: 9 },
      'MZ': { center: [23.5, 92.9], zoom: 9 },
      'TR': { center: [23.8, 91.3], zoom: 9 },
      'SK': { center: [27.5, 88.5], zoom: 9 },
      'all': { center: [25.85, 92.5], zoom: 8 }
    };
    const target = stateCenters[stateCode] || stateCenters['all'];
    this.map.flyTo(target.center, target.zoom, { duration: 1.2 });
  }

  enableLocationPicker(callback) {
    if (this._pickerCallback) {
      this.disableLocationPicker();
    }
    
    this._pickerCallback = callback;
    document.getElementById('gis-map').style.cursor = 'crosshair';
    
    // Use a named function so we can remove it specifically
    this._pickerHandler = (e) => {
      const lat = e.latlng.lat.toFixed(5);
      const lng = e.latlng.lng.toFixed(5);
      
      const callback = this._pickerCallback;
      this.disableLocationPicker();
      
      if (callback) {
        callback(`${lat}, ${lng}`);
      }
    };
    
    // Slight timeout to prevent immediate firing if click bubbled
    setTimeout(() => {
      this.map.on('click', this._pickerHandler);
    }, 100);
  }
  
  disableLocationPicker() {
    document.getElementById('gis-map').style.cursor = '';
    if (this._pickerHandler) {
      this.map.off('click', this._pickerHandler);
      this._pickerHandler = null;
    }
    this._pickerCallback = null;
  }
}

const tacticalMap = new TacticalMap();
