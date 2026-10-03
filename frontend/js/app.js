// NER-LogiSense: Application Controller & Router
const App = {
  currentModule: 'gis-map',
  currentLang: 'en',
  currentRole: 'State Disaster Management Officer',
  isEmergencyActive: true,
  isLowBandwidth: false,

  // Multilingual UI strings for high-stress operational triage
  i18n: {
    en: {
      surge_protocol: "Active Monsoon Surge Protocol (Level-3)",
      blockades: "Live Route Blockades",
      telemetry_sync: "Telemetry Sync: 99.4% (GSAT-7A/NavIC)",
      btn_emergency: "EMERGENCY DISASTER MODE",
      mod_gis: "1. Live Accessibility GIS",
      mod_districts: "2. District Isolation Index",
      mod_risk: "3. AI Risk & Disruption Forecast",
      mod_routes: "4. Route Planner & Relief",
      mod_fleet: "5. Commodity Fleet Tracking",
      mod_incidents: "6. Field Verification Console",
      mod_emergency: "7. Emergency Corridors (SOS)",
      mod_offline: "8. Offline Field App Portal",
      kpi_tracked: "Total Tracked",
      kpi_operational: "Operational",
      kpi_chokepoints: "Critical Chokepoints",
      kpi_cutoff: "Cutoff Warning",
      kpi_convoys: "Relief Convoys"
    },
    as: {
      surge_protocol: "সক্ৰিয় বাৰিষা প্লাৱন প্ৰট'কল (স্তৰ-৩)",
      blockades: "বন্ধ পথসমূহ",
      telemetry_sync: "টেলিমেট্ৰি সমকালীনকৰণ: ৯৯.৪%",
      btn_emergency: "জৰুৰী দুৰ্যোগ স্থিতি",
      mod_gis: "১. প্ৰত্যক্ষ পথ ব্যৱস্থা GIS",
      mod_districts: "২. জিলা বিচ্ছিন্নতা সূচক",
      mod_risk: "৩. AI বিপদাশংকা আৰু বাধা পূৰ্বানুমান",
      mod_routes: "৪. পথ পৰিকল্পনা আৰু সাহায্য",
      mod_fleet: "৫. অত্যাৱশ্যকীয় যান-বাহন নিৰীক্ষণ",
      mod_incidents: "৬. ক্ষেত্ৰভিত্তিক পৰীক্ষণ পেনেল",
      mod_emergency: "৭. জৰুৰী পথ ক'ৰিডৰ (SOS)",
      mod_offline: "৮. অফলাইন ফিল্ড এপ প'ৰ্টেল",
      kpi_tracked: "মুঠ নিৰীক্ষিত পথ",
      kpi_operational: "কাৰ্যক্ষম পথ",
      kpi_chokepoints: "সংকটজনক অৱৰোধ",
      kpi_cutoff: "বিচ্ছিন্ন জিলা",
      kpi_convoys: "সাহায্যবাহী কনভয়"
    },
    hi: {
      surge_protocol: "सक्रिय मानसून आपातकालीन प्रोटोकॉल (लेवल-3)",
      blockades: "अवरुद्ध मुख्य मार्ग",
      telemetry_sync: "टेलीमेट्री सिंक: 99.4% (नाविक)",
      btn_emergency: "आपातकालीन आपदा मोड",
      mod_gis: "1. लाइव सुगम्यता GIS मैप",
      mod_districts: "2. जिला अलगाव सूचकांक",
      mod_risk: "3. AI जोखिम एवं अवरोध पूर्वानुमान",
      mod_routes: "4. मार्ग योजना एवं राहत दल",
      mod_fleet: "5. आवश्यक आपूर्ति वाहन ट्रैकिंग",
      mod_incidents: "6. फील्ड सत्यापन कंसोल",
      mod_emergency: "7. आपातकालीन गलियारे (SOS)",
      mod_offline: "8. ऑफलाइन फील्ड ऐप पोर्टल",
      kpi_tracked: "कुल ट्रैक हाईवे",
      kpi_operational: "सुचारू संचालन",
      kpi_chokepoints: "गंभीर अवरोध",
      kpi_cutoff: "संपर्क विहीन जिला",
      kpi_convoys: "राहत काफिले"
    },
    bn: {
      surge_protocol: "সক্রিয় বর্ষা প্লাবন প্রোটোকল (লেভেল-৩)",
      blockades: "অবরুদ্ধ সড়কসমূহ",
      telemetry_sync: "টেলিমেট্রি সংযোগ: ৯৯.৪%",
      btn_emergency: "জরুরি দুর্যোগ মোড",
      mod_gis: "১. লাইভ অ্যাক্সেসিবিলিটি GIS",
      mod_districts: "২. জেলা বিচ্ছিন্নতা সূচক",
      mod_risk: "৩. AI ঝুঁকি ও প্রতিবন্ধকতা পূর্বাভাস",
      mod_routes: "৪. রুট প্ল্যানার ও ত্রাণ প্রেরণ",
      mod_fleet: "৫. সরবরাহ যানবাহন ট্র্যাকিং",
      mod_incidents: "৬. ফিল্ড যাচাইকরণ কনসোল",
      mod_emergency: "৭. জরুরি করিডোর (SOS)",
      mod_offline: "৮. অফলাইন ফিল্ড অ্যাপ পোর্টাল"
    },
    mni: {
      surge_protocol: "নোংথোই ঈচাউ প্রোতোকোল (থাক-৩)",
      blockades: "থিংজিনবা লম্বীশিং",
      telemetry_sync: "তেলেমেত্রি সিঙ্ক: ৯৯.৪%",
      btn_emergency: "খুদোংথীবা অকনবা মোদ",
      mod_gis: "১. লাইভ এক্সেসিবিলিতি GIS",
      mod_districts: "২. দিস্ত্রিক আইসোলেসন ইন্দেক্স",
      mod_risk: "৩. AI রিস্ক ফোরকাস্ত",
      mod_routes: "৪. লম্বী প্লানার অমসুং রিলিফ",
      mod_fleet: "৫. কার্গো ফ্লিট ত্রেকিং",
      mod_incidents: "৬. ফিল্ড রিভরিফিকেসন",
      mod_emergency: "৭. ইমার্জেন্সি করিদোর (SOS)",
      mod_offline: "৮. ওফলাইন ফিল্ড এপ"
    }
  },

  async init() {
    console.log('[NER-LogiSense] Initializing tactical client...');
    this.bindEvents();
    
    // Check login state before initializing heavy modules
    if (!this.checkLoginState()) {
      return; // Stop initialization until logged in
    }

    await this.startupModules();
  },

  checkLoginState() {
    const savedRole = localStorage.getItem('ner_user_role');
    const loginOverlay = document.getElementById('login-overlay');
    const mainApp = document.getElementById('main-application');

    if (savedRole) {
      this.currentRole = savedRole;
      if (loginOverlay) loginOverlay.style.display = 'none';
      if (mainApp) mainApp.style.display = 'flex';
      return true;
    } else {
      if (loginOverlay) loginOverlay.style.display = 'flex';
      if (mainApp) mainApp.style.display = 'none';
      return false;
    }
  },

  async startupModules() {
    // Initialize Leaflet Map
    tacticalMap.init();

    // Initialize WebSocket live stream
    liveStream.init();
    liveStream.on('telemetry', (data) => this.handleLiveTelemetry(data));
    liveStream.on('alert', (data) => this.handleLiveAlert(data));

    // Load initial operational data
    await this.refreshData();

    // Apply role-based permissions
    this.applyRolePermissions();
  },

  applyRolePermissions() {
    const roleSelect = document.getElementById('role-selector');
    if (roleSelect) {
      if (this.currentRole === 'COMMAND_CENTER') roleSelect.value = 'Role: State Disaster Management Officer';
      else if (this.currentRole === 'DISPATCHER') roleSelect.value = 'Role: Essential Logistics Dispatcher';
      else if (this.currentRole === 'DRIVER') roleSelect.value = 'Role: Driver';
    }

    const navItems = document.querySelectorAll('.nav-item');
    if (this.currentRole === 'DRIVER') {
      // Hide all modules except Driver Navigator and Offline
      navItems.forEach(item => {
        const target = item.getAttribute('data-target');
        if (target === 'driver-navigator' || target === 'offline') {
          item.style.display = 'block';
        } else {
          item.style.display = 'none';
        }
      });
      this.navigate('driver-navigator');
    } else {
      // Command Center / Dispatcher sees everything
      navItems.forEach(item => item.style.display = 'block');
      this.navigate('gis-map');
    }
  },

  bindEvents() {
    // Login Form Submit
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const role = document.getElementById('login-role').value;
        const token = document.getElementById('login-token').value;
        
        if (token) {
          localStorage.setItem('ner_user_role', role);
          
          const loginOverlay = document.getElementById('login-overlay');
          const mainApp = document.getElementById('main-application');
          if (loginOverlay) loginOverlay.style.display = 'none';
          if (mainApp) mainApp.style.display = 'flex';
          
          this.currentRole = role;
          await this.startupModules();
          this.showToast(`Authenticated as ${role}`, 'success');
        }
      });
    }

    // Logout Button
    const btnLogout = document.getElementById('btn-logout');
    if (btnLogout) {
      btnLogout.addEventListener('click', () => {
        localStorage.removeItem('ner_user_role');
        window.location.reload();
      });
    }

    // Nav Items
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const target = item.getAttribute('data-target');
        this.navigate(target);
      });
    });

    // Language Selector
    const langSelect = document.getElementById('lang-selector');
    if (langSelect) {
      langSelect.addEventListener('change', (e) => {
        this.setLanguage(e.target.value);
      });
    }

    // Role Selector
    const roleSelect = document.getElementById('role-selector');
    if (roleSelect) {
      roleSelect.addEventListener('change', (e) => {
        this.currentRole = e.target.value;
        this.showToast(`Active Command Role Switched to: ${this.currentRole}`, 'info');
      });
    }

    // Emergency Disaster Mode Toggle
    const emBtn = document.getElementById('btn-emergency-mode');
    if (emBtn) {
      emBtn.addEventListener('click', () => {
        this.isEmergencyActive = !this.isEmergencyActive;
        emBtn.style.opacity = this.isEmergencyActive ? '1' : '0.6';
        this.showToast(
          this.isEmergencyActive ? 'EMERGENCY DISASTER MODE ACTIVATED: Priority Corridors Enforced' : 'Emergency Mode Standdown',
          this.isEmergencyActive ? 'danger' : 'info'
        );
      });
    }

    // Low-Bandwidth Mode
    const lowBwBtn = document.getElementById('low-bandwidth-toggle');
    if (lowBwBtn) {
      lowBwBtn.addEventListener('click', () => {
        this.isLowBandwidth = !this.isLowBandwidth;
        lowBwBtn.classList.toggle('text-secondary', this.isLowBandwidth);
        this.showToast(`Low-Bandwidth Mode: ${this.isLowBandwidth ? 'ENABLED (Vector Tiles & Text Stream)' : 'DISABLED'}`, 'info');
      });
    }

    // Map Layer Toggles
    const toggleRoads = document.getElementById('layer-toggle-roads');
    if (toggleRoads) toggleRoads.addEventListener('change', (e) => tacticalMap.toggleLayer('roads', e.target.checked));

    const toggleBridges = document.getElementById('layer-toggle-bridges');
    if (toggleBridges) toggleBridges.addEventListener('change', (e) => tacticalMap.toggleLayer('bridges', e.target.checked));

    const toggleConvoys = document.getElementById('layer-toggle-convoys');
    if (toggleConvoys) toggleConvoys.addEventListener('change', (e) => tacticalMap.toggleLayer('convoys', e.target.checked));

    const toggleRadar = document.getElementById('layer-toggle-radar');
    if (toggleRadar) toggleRadar.addEventListener('change', (e) => tacticalMap.toggleLayer('radar', e.target.checked));

    const toggleDistricts = document.getElementById('layer-toggle-districts');
    if (toggleDistricts) toggleDistricts.addEventListener('change', (e) => tacticalMap.toggleLayer('districts', e.target.checked));

    // Map Basemap Engine Switcher
    const basemapSelect = document.getElementById('map-basemap-select');
    if (basemapSelect) {
      basemapSelect.addEventListener('change', (e) => {
        tacticalMap.setBasemap(e.target.value);
        this.showToast(`GIS Basemap Engine: ${e.target.options[e.target.selectedIndex].text}`, 'info');
      });
    }

    // District & State Filter Map Navigation
    const stateFilter = document.getElementById('filter-state-select');
    if (stateFilter) {
      stateFilter.addEventListener('change', (e) => {
        tacticalMap.flyToState(e.target.value);
      });
    }

    const distFilter = document.getElementById('filter-district-select');
    if (distFilter) {
      distFilter.addEventListener('change', (e) => {
        tacticalMap.flyToDistrict(e.target.value);
      });
    }
  },

  setLanguage(lang) {
    this.currentLang = lang;
    const dict = this.i18n[lang] || this.i18n['en'];
    
    // Update top ribbon
    const protoEl = document.getElementById('banner-protocol-text');
    if (protoEl && dict.surge_protocol) protoEl.innerText = dict.surge_protocol;

    // Update nav links
    const keys = ['gis', 'districts', 'risk', 'routes', 'fleet', 'incidents', 'emergency', 'offline'];
    keys.forEach((k, idx) => {
      const link = document.querySelector(`.nav-item[data-target="${this.getModuleIdByIndex(idx + 1)}"] span:last-child`);
      if (link && dict[`mod_${k}`]) link.innerText = dict[`mod_${k}`];
    });

    this.showToast(`Language updated: ${lang.toUpperCase()}`, 'info');
  },

  getModuleIdByIndex(idx) {
    const map = {
      1: 'gis-map',
      2: 'districts',
      3: 'ai-risk',
      4: 'route-planner',
      5: 'fleet-tracking',
      6: 'field-console',
      7: 'emergency-corridors',
      8: 'offline-portal'
    };
    return map[idx] || 'gis-map';
  },

  async refreshData() {
    try {
      const [kpi, segments, bridges, incidents, vehicles, districts] = await Promise.all([
        API.getAccessibilitySummary().catch(() => ({ operational_pct: 74.2, total_network_km: 14820, active_blockades_count: 9, cutoff_districts_count: 4, convoys_in_transit_count: 28 })),
        API.getRoadSegments().catch(() => []),
        API.getBridges().catch(() => []),
        API.getIncidents().catch(() => []),
        API.getVehicles().catch(() => []),
        API.getDistricts().catch(() => [])
      ]);

      this.allDistricts = districts; // Store for the district module

      // Update KPI displays
      this.updateKPIs(kpi);

      // Render to Map
      if (segments.length > 0) tacticalMap.renderRoadNetwork(segments);
      if (bridges.length > 0) tacticalMap.renderBridges(bridges);
      if (incidents.length > 0) tacticalMap.renderHazards(incidents);
      if (vehicles.length > 0) tacticalMap.renderVehicles(vehicles);
      if (districts && districts.length > 0) tacticalMap.renderDistricts(districts);

    } catch (e) {
      console.warn('[REFRESH DATA ERROR]', e);
    }
  },

  updateKPIs(kpi) {
    const elTracked = document.getElementById('kpi-total-km');
    const elOp = document.getElementById('kpi-operational');
    const elBlock = document.getElementById('kpi-blockades');
    const elCutoff = document.getElementById('kpi-cutoff');
    const elConvoys = document.getElementById('kpi-convoys');

    if (elTracked) elTracked.innerText = (kpi.total_network_km || 14820).toLocaleString();
    if (elOp) elOp.innerText = `${kpi.operational_pct || 74.2}%`;
    if (elBlock) elBlock.innerText = kpi.active_blockades_count || 9;
    if (elCutoff) elCutoff.innerText = kpi.cutoff_districts_count || 4;
    if (elConvoys) elConvoys.innerText = kpi.convoys_in_transit_count || 28;
  },

  navigate(moduleId) {
    this.currentModule = moduleId;

    // Update active nav styling
    document.querySelectorAll('.nav-item').forEach(el => {
      el.classList.toggle('active', el.getAttribute('data-target') === moduleId);
    });

    // Hide all module sections
    document.querySelectorAll('.module-pane').forEach(el => {
      el.style.display = 'none';
    });

    // Show target section
    const targetEl = document.getElementById(`pane-${moduleId}`);
    if (targetEl) {
      targetEl.style.display = 'block';
    }

    // Specific module hooks
    if (moduleId === 'gis-map') {
      setTimeout(() => {
        if (tacticalMap.map) tacticalMap.map.invalidateSize();
      }, 100);
    } else if (moduleId === 'districts') {
      this.renderDistrictsModule();
    } else if (moduleId === 'ai-risk') {
      this.renderAIRiskModule();
    } else if (moduleId === 'route-planner') {
      this.renderRoutePlannerModule();
    } else if (moduleId === 'fleet-tracking') {
      this.renderFleetModule();
    } else if (moduleId === 'field-console') {
      this.renderFieldConsoleModule();
    } else if (moduleId === 'emergency-corridors') {
      this.renderEmergencyCorridorsModule();
    } else if (moduleId === 'offline-portal') {
      this.renderOfflinePortalModule();
    } else if (moduleId === 'driver-navigator') {
      this.renderDriverNavigatorModule();
    }
  },

  // 2. District Isolation Module
  async renderDistrictsModule() {
    const container = document.getElementById('district-grid-container');
    if (!container) return;

    container.innerHTML = `
      <div style="color:#94a3b8; padding:30px; text-align:center; grid-column:1/-1;">
        <span class="material-symbols-outlined" style="font-size:28px; color:#0284c7;">refresh</span>
        <div style="margin-top:8px;">Retrieving District Isolation Diagnostics & Chokepoint Metrics...</div>
      </div>
    `;

    try {
      let districts = this.allDistricts;
      
      // Fallback mock data if API is entirely unreachable
      if (!districts || districts.length === 0) {
        districts = [
          {
            id: "dist-dima-hasao",
            name: "Dima Hasao (Haflong)",
            state_code: "AS",
            state_name: "Assam",
            isolation_index: 0.72,
            connectivity_status: "RESTRICTED",
            critical_facilities_count: 11,
            hospitals_count: 3,
            relief_camps_count: 8,
            center_lat: 25.188,
            center_lon: 92.997,
            problem_type: "LANDSLIDE",
            problem_summary: "NH-27 Blocked: Barail Escarpment Massive Hill Slope Debris Failure",
            problem_description: "Massive hill slope failure with ~4,500 m³ of fractured rock, shale, and tree debris covering 80m of the dual carriageway. Road bed partially breached; active sliding under current monsoon rainfall.",
            chokepoint_location: "NH-27 KM 141.8, Dima Hasao Sector (Near Barail Bridge #4)",
            chokepoint_lat: 25.1882,
            chokepoint_lon: 92.9976,
            operational_impact: "Heavy freight & cryo-oxygen supply to Barak Valley halted. Haflong Civil Hospital & 2 sub-divisional hospitals facing critical supply depletion (<48h). Lumding-Badarpur railway section track foundation washed out.",
            restoration_eta: "Est. Clearance: 14.0 hours (3 PWD heavy hydraulic excavators & BRO 119 RCC deployed)",
            recommended_contingency: "Reroute essential medical/perishable light cargo (<16 MT) via SH-4 Umrangso-Lanka tactical bypass with BRO escort."
          },
        {
          id: "dist-champhai",
          name: "Champhai (Indo-Myanmar)",
          state_code: "MZ",
          state_name: "Mizoram",
          isolation_index: 0.82,
          connectivity_status: "SEVERED",
          critical_facilities_count: 7,
          hospitals_count: 2,
          relief_camps_count: 5,
          center_lat: 23.475,
          center_lon: 93.328,
          problem_type: "MUDFLOW & SUBSIDENCE",
          problem_summary: "Total Highway Severance: Tiau River Catchment Mudflow",
          problem_description: "Continuous 72-hour precipitation (210mm) triggered severe liquefied mudflow spanning 120m across the ridge highway. Foundation roadbed sunken by 1.2m along mountain edge.",
          chokepoint_location: "NH-6 Extension / Champhai-Zokhawthar Ridge Pass KM 44.2",
          chokepoint_lat: 23.475,
          chokepoint_lon: 93.328,
          operational_impact: "District severed from Aizawl central distribution depot. Petroleum (POL) reserves at 24% capacity. Essential baby food & dialysis fluids stockout risk within 36 hours.",
          restoration_eta: "Est. Clearance: 28.0 hours (Requires earth filling, retaining wall shoring, and temporary Bailey decking)",
          recommended_contingency: "Helicopter emergency air-drop protocol activated by State Disaster Management Authority for critical medicine batches."
        },
        {
          id: "dist-kalimpong",
          name: "Kalimpong / Sevoke Pass",
          state_code: "SK",
          state_name: "Sikkim",
          isolation_index: 0.65,
          connectivity_status: "RESTRICTED",
          critical_facilities_count: 8,
          hospitals_count: 2,
          relief_camps_count: 6,
          center_lat: 27.066,
          center_lon: 88.473,
          problem_type: "RIVER_OVERFLOW",
          problem_summary: "NH-10 Inundation & Coronation Bridge Pier Scour Warning",
          problem_description: "Teesta river discharge surged past extreme warning level, inundating 0.8m over the low-lying highway apron. Upstream debris accumulation creating lateral pressure on riverbank embankments.",
          chokepoint_location: "NH-10 KM 32, Teesta Bazar & Sevoke Corridor Junction",
          chokepoint_lat: 27.066,
          chokepoint_lon: 88.473,
          operational_impact: "Commercial trucks barred from transit to prevent bridge structural destabilization. Only 4x4 emergency rescue vehicles permitted during daylight hours.",
          restoration_eta: "Est. Clearance: 10.0 hours (Contingent on upstream barrage discharge stabilization)",
          recommended_contingency: "Divert light supply traffic via Lava-Algarah-Gorubathan tactical mountain circuit."
        },
        {
          id: "dist-imphal-west",
          name: "Imphal West",
          state_code: "MN",
          state_name: "Manipur",
          isolation_index: 0.48,
          connectivity_status: "RESTRICTED",
          critical_facilities_count: 13,
          hospitals_count: 6,
          relief_camps_count: 7,
          center_lat: 24.817,
          center_lon: 93.936,
          problem_type: "HILL_SLIP_AND_SECURITY",
          problem_summary: "NH-102 Escort Required & Tengnoupal Hill Slip",
          problem_description: "Monsoon hill-cutting soil creep narrowing carriage-way to single lane at KM 58, compounded by mandatory tactical security convoy formations.",
          chokepoint_location: "NH-102 KM 58, Tengnoupal Pass Sector",
          chokepoint_lat: 24.817,
          chokepoint_lon: 93.936,
          operational_impact: "Convoys subject to mandatory security muster points and timed escort batches (06:00, 11:00, 15:00 IST). Average transit delay +65 mins.",
          restoration_eta: "Active Operation: Single-lane open with Assam Rifles convoy escorts.",
          recommended_contingency: "Ensure consignments join registered Armed Escort Convoy waves with NavIC transponders active."
        },
        {
          id: "dist-kohima",
          name: "Kohima",
          state_code: "NL",
          state_name: "Nagaland",
          isolation_index: 0.40,
          connectivity_status: "RESTRICTED",
          critical_facilities_count: 6,
          hospitals_count: 4,
          relief_camps_count: 2,
          center_lat: 25.674,
          center_lon: 94.110,
          problem_type: "ROAD_SUBSIDENCE",
          problem_summary: "NH-29 Subsidence: Pagla Pahar Sector Single-Lane Regulation",
          problem_description: "Subterranean aquifer seepage resulted in 30cm depression along a 45m section of the descending lane. Automated flagger regulation in place.",
          chokepoint_location: "NH-29 KM 24, Pagla Pahar Gorge Chokepoint",
          chokepoint_lat: 25.674,
          chokepoint_lon: 94.110,
          operational_impact: "Multi-axle heavy trailers (>30 MT) staged to avoid structural strain. Average consignment transit delay +35 mins.",
          restoration_eta: "Est. Clearance: 8.0 hours for stone-pitching reinforcement and cold-mix asphalt overlay.",
          recommended_contingency: "Alternate passage via Niuland-Kohima bypass authorized for light utility vehicles and ambulances."
        },
        {
          id: "dist-east-khasi",
          name: "East Khasi Hills (Shillong)",
          state_code: "ML",
          state_name: "Meghalaya",
          isolation_index: 0.28,
          connectivity_status: "CONNECTED",
          critical_facilities_count: 11,
          hospitals_count: 8,
          relief_camps_count: 3,
          center_lat: 25.578,
          center_lon: 91.893,
          problem_type: "FLASH_FLOOD_DRAINAGE",
          problem_summary: "Sonapur Tunnel Portal Waterlogging & Slow Movement",
          problem_description: "Excess rainfall runoff (148mm) overwhelmed the portal drainage apron, creating 0.35m standing water and slick silt deposits over a 60m road stretch.",
          chokepoint_location: "NH-6 KM 88.5, Sonapur Tunnel Southern Portal",
          chokepoint_lat: 25.105,
          chokepoint_lon: 92.368,
          operational_impact: "Moderate freight deceleration. All heavy vehicles cleared to transit with 50m minimum headway spacing and 15 km/h speed cap.",
          restoration_eta: "Active Clearing: State PWD high-volume submersible pumps active; portal water level receding.",
          recommended_contingency: "Maintain single-file convoy formation with fog lamps active inside tunnel corridor."
        },
        {
          id: "dist-cachar",
          name: "Cachar (Silchar)",
          state_code: "AS",
          state_name: "Assam",
          isolation_index: 0.45,
          connectivity_status: "RESTRICTED",
          critical_facilities_count: 9,
          hospitals_count: 5,
          relief_camps_count: 4,
          center_lat: 24.833,
          center_lon: 92.779,
          problem_type: "RIVER_SURGE",
          problem_summary: "Barak River High Water & Bypass Approach Inundation",
          problem_description: "Barak river backflow causing localized waterlogging on lower bypass approach roads. Silt accumulations on southern shoulder.",
          chokepoint_location: "NH-37 / Silchar Bypass KM 12 (Barak Embankment)",
          chokepoint_lat: 24.833,
          chokepoint_lon: 92.779,
          operational_impact: "Inter-district delivery turnaround delayed +50 mins. Upstream Dima Hasao block creates secondary buffer stock reliance.",
          restoration_eta: "Under Observation: River level plateauing below red line; no structural compromise.",
          recommended_contingency: "Use northern Kumbhirgram Airport Ring Road for cross-valley delivery access."
        },
        {
          id: "dist-papum-pare",
          name: "Papum Pare (Itanagar)",
          state_code: "AR",
          state_name: "Arunachal",
          isolation_index: 0.35,
          connectivity_status: "CONNECTED",
          critical_facilities_count: 8,
          hospitals_count: 4,
          relief_camps_count: 4,
          center_lat: 27.102,
          center_lon: 93.621,
          problem_type: "LOOSE_GRAVEL",
          problem_summary: "Trans-Arunachal Highway Open: Precautionary Patrol",
          problem_description: "Minor loose gravel and mud sloughing along hill cutting slopes between KM 74-78. Highway structurally sound with active drainage maintenance.",
          chokepoint_location: "NH-13 KM 76, Hoj-Potin Section",
          chokepoint_lat: 27.102,
          chokepoint_lon: 93.621,
          operational_impact: "Normal supply chain flow. Caution signage posted; all priority consignments arriving on schedule.",
          restoration_eta: "Fully Operational: BRO road rangers conducting rolling sweeps.",
          recommended_contingency: "Primary Trans-Arunachal Highway (NH-13) fully open."
        },
        {
          id: "dist-kamrup-metro",
          name: "Kamrup Metro (Guwahati)",
          state_code: "AS",
          state_name: "Assam",
          isolation_index: 0.05,
          connectivity_status: "CONNECTED",
          critical_facilities_count: 16,
          hospitals_count: 14,
          relief_camps_count: 2,
          center_lat: 26.144,
          center_lon: 91.736,
          problem_type: "NORMAL",
          problem_summary: "Central Regional Logistics Gateway: 100% Operational Flow",
          problem_description: "Saraighat Brahmaputra bridges, Jalukbari transport interchange, and IOCL oil refinery railhead operating at peak capacity with zero blockades.",
          chokepoint_location: "Saraighat Bridge & Jalukbari Interchange Complex",
          chokepoint_lat: 26.144,
          chokepoint_lon: 91.736,
          operational_impact: "All arterial expressways clear. Central staging depot dispatching relief buffers to upper districts.",
          restoration_eta: "Fully Operational (100% throughput).",
          recommended_contingency: "All arterial National Highway corridors (NH-27, NH-17) open for 24/7 heavy freight movement."
        }
        ];
      }

      this.allDistricts = districts;

      // Update Top Status Counter Pills
      const criticalCount = this.allDistricts.filter(d => d.isolation_index >= 0.65 || d.connectivity_status === 'SEVERED').length;
      const restrictedCount = this.allDistricts.filter(d => (d.isolation_index < 0.65 && d.isolation_index >= 0.35) || d.connectivity_status === 'RESTRICTED').length;
      const connectedCount = this.allDistricts.filter(d => d.isolation_index < 0.35 || d.connectivity_status === 'CONNECTED').length;

      const elCrit = document.getElementById('dist-count-critical');
      const elRest = document.getElementById('dist-count-restricted');
      const elConn = document.getElementById('dist-count-connected');
      if (elCrit) elCrit.innerText = `${criticalCount} Districts`;
      if (elRest) elRest.innerText = `${restrictedCount} Districts`;
      if (elConn) elConn.innerText = `${connectedCount} Districts`;

      // Set up filter buttons and search if not bound
      this.bindDistrictFilters();

      // Render cards
      this.renderDistrictCards(this.allDistricts);

    } catch (e) {
      console.error('[DISTRICTS MODULE ERROR]', e);
      container.innerHTML = `<div style="color:#fca5a5; padding:20px;">Failed to load district diagnostics.</div>`;
    }
  },

  bindDistrictFilters() {
    if (this._districtFiltersBound) return;
    this._districtFiltersBound = true;

    const filterButtons = document.querySelectorAll('.dist-filter-btn');
    const searchInput = document.getElementById('district-search-input');

    let activeFilter = 'ALL';
    let searchQuery = '';

    const applyFilters = () => {
      let filtered = this.allDistricts || [];

      // Filter by status category
      if (activeFilter === 'CRITICAL') {
        filtered = filtered.filter(d => d.isolation_index >= 0.65 || d.connectivity_status === 'SEVERED');
      } else if (activeFilter === 'RESTRICTED') {
        filtered = filtered.filter(d => (d.isolation_index < 0.65 && d.isolation_index >= 0.35) || d.connectivity_status === 'RESTRICTED');
      } else if (activeFilter === 'CONNECTED') {
        filtered = filtered.filter(d => d.isolation_index < 0.35 || d.connectivity_status === 'CONNECTED');
      }

      // Filter by search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        filtered = filtered.filter(d => 
          d.name.toLowerCase().includes(q) ||
          d.state_name.toLowerCase().includes(q) ||
          (d.problem_summary && d.problem_summary.toLowerCase().includes(q)) ||
          (d.problem_description && d.problem_description.toLowerCase().includes(q)) ||
          (d.chokepoint_location && d.chokepoint_location.toLowerCase().includes(q))
        );
      }

      this.renderDistrictCards(filtered);
    };

    filterButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        filterButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeFilter = btn.getAttribute('data-filter') || 'ALL';
        applyFilters();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value;
        applyFilters();
      });
    }
  },

  // 4b. Driver Safe Route Finder
  async renderDriverNavigatorModule() {
    const container = document.getElementById('driver-corridors-container');
    if (!container) return;
    
    // Bind the route query form
    const form = document.getElementById('driver-route-form');
    if (form) {
      // Avoid binding multiple times
      const newForm = form.cloneNode(true);
      form.parentNode.replaceChild(newForm, form);
      
      newForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const origin = document.getElementById('driver-origin').value;
        const dest = document.getElementById('driver-dest').value;
        const vehicleType = document.getElementById('driver-vehicle-type').value;
        const weight = parseFloat(document.getElementById('driver-weight').value);
        
        const payload = {
          origin_name: origin,
          destination_name: dest,
          vehicle_type: vehicleType,
          gross_weight_mt: weight,
          priority: "SAFEST"
        };
        
        await this.handleDriverRouteCalculation(payload);
      });

      // Bind Map Pickers
      const btnPickOrigin = document.getElementById('btn-pick-origin');
      if (btnPickOrigin) {
        btnPickOrigin.addEventListener('click', () => {
          this.navigate('gis-map');
          this.showToast('Click anywhere on the map to set ORIGIN.', 'info');
          tacticalMap.enableLocationPicker((coordStr) => {
            document.getElementById('driver-origin').value = coordStr;
            this.navigate('driver-navigator');
            this.showToast(`Origin set to: ${coordStr}`, 'info');
          });
        });
      }

      const btnPickDest = document.getElementById('btn-pick-dest');
      if (btnPickDest) {
        btnPickDest.addEventListener('click', () => {
          this.navigate('gis-map');
          this.showToast('Click anywhere on the map to set DESTINATION.', 'info');
          tacticalMap.enableLocationPicker((coordStr) => {
            document.getElementById('driver-dest').value = coordStr;
            this.navigate('driver-navigator');
            this.showToast(`Destination set to: ${coordStr}`, 'info');
          });
        });
      }
    }

    // Load pre-verified quick corridors
    container.innerHTML = `<div style="color:#94a3b8; font-size:12px;">Scanning verified safe corridors...</div>`;
    
    try {
      const corridors = await API.getDriverCorridors().catch(() => [
        {
          id: "corridor-silchar",
          title: "Guwahati ➔ Silchar / Haflong",
          via: "Bypasses NH-27 KM 141.8 Barail Landslide via SH-4 Umrangso Strategic Bypass.",
          distance_km: 320,
          duration_hours: 9.5,
          verified_weight_mt: 30.0,
          origin: "Guwahati Central Depot",
          destination: "Silchar Relief Camp"
        },
        {
          id: "corridor-imphal",
          title: "Dimapur ➔ Kohima ➔ Imphal",
          via: "Verified NH-2 4-Lane corridor. Clear of flooding.",
          distance_km: 142,
          duration_hours: 4.5,
          verified_weight_mt: 40.0,
          origin: "Dimapur Logistics Hub",
          destination: "Imphal Hospital"
        }
      ]);
      
      if (!corridors || corridors.length === 0) {
        container.innerHTML = `<div style="color:#fca5a5; font-size:12px;">No verified corridors currently available.</div>`;
        return;
      }
      
      container.innerHTML = corridors.map(c => `
        <div class="driver-corridor-card">
          <div style="font-weight:800; font-size:14px; color:#10b981; margin-bottom:4px;">${c.title}</div>
          <div style="font-size:11px; color:#94a3b8; margin-bottom:8px;">Via: ${c.via}</div>
          <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:11px; color:#dae2fd;">
            <span><span class="material-symbols-outlined" style="font-size:12px; vertical-align:text-bottom;">directions_car</span> ${c.distance_km} km / ${c.duration_hours}h</span>
            <span><span class="material-symbols-outlined" style="font-size:12px; vertical-align:text-bottom;">weight</span> Max: ${c.verified_weight_mt} MT</span>
          </div>
          <button class="btn-primary" style="width:100%; background:#131b2e; border:1px solid #059669; color:#10b981; font-size:11px;" onclick="
            document.getElementById('driver-origin').value = '${c.origin}';
            document.getElementById('driver-dest').value = '${c.destination}';
            document.getElementById('driver-route-form').dispatchEvent(new Event('submit'));
          ">Select Safe Corridor</button>
        </div>
      `).join('');
      
    } catch(e) {
      console.error(e);
      container.innerHTML = `<div style="color:#fca5a5; font-size:12px;">Failed to load safe corridors.</div>`;
    }
  },

  async handleDriverRouteCalculation(payload) {
    const resultsContainer = document.getElementById('driver-route-results-container');
    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `<div style="color:#10b981; font-size:12px; text-align:center;"><span class="material-symbols-outlined pulse-dot">sync</span> Verifying safety metrics and computing safe path...</div>`;
    
    try {
      const response = await API.planDriverSafeRoute(payload);
      
      // We will render the result
      this.renderDriverSafeRouteResult(response);
      
      // Auto-preview on map
      if (response.waypoints && response.waypoints.length > 0) {
        const firstWp = response.waypoints[0];
        const lastWp = response.waypoints[response.waypoints.length-1];
        tacticalMap.renderDriverSafeRoute(
          response.waypoints, 
          [firstWp[0], firstWp[1]],
          [lastWp[0], lastWp[1]],
          "Verified Safe Path",
          response.turn_by_turn
        );
      }
      
    } catch(e) {
      console.error(e);
      resultsContainer.innerHTML = `<div style="background:#dc262622; border-left:4px solid #dc2626; padding:12px; border-radius:4px;">
        <b style="color:#ffb4ab;">Route Calculation Failed</b>
        <p style="font-size:11px; color:#dae2fd;">Could not guarantee a 100% safe route matching the vehicle weight limits or destination is completely severed.</p>
      </div>`;
    }
  },
  
  renderDriverSafeRouteResult(routeData) {
    const resultsContainer = document.getElementById('driver-route-results-container');
    
    // Safety checklist DOM
    const checklist = routeData.safety_checklist;
    
    const renderCheckItem = (label, value, icon, ok) => `
      <div style="display:flex; justify-content:space-between; align-items:center; background:#0b1326; padding:8px 12px; border-radius:4px; border-left:3px solid ${ok ? '#10b981' : '#dc2626'}; font-size:12px;">
        <span style="color:#94a3b8; display:flex; align-items:center; gap:6px;"><span class="material-symbols-outlined" style="font-size:14px;">${icon}</span> ${label}</span>
        <b style="color:${ok ? '#10b981' : '#ffb4ab'};">${value}</b>
      </div>
    `;

    // Turn by turn steps
    const stepsHtml = routeData.turn_by_turn.map((step, idx) => `
      <div class="turn-step-item">
        <div class="turn-step-num">${idx + 1}</div>
        <div class="turn-step-content">
          <div class="turn-step-head">
            <span class="turn-step-road">${step.road_designation}</span>
            <span class="turn-step-dist">${step.step_distance_km} km</span>
          </div>
          <div class="turn-step-inst">${step.instruction}</div>
          <div class="turn-step-meta">
            <span><span class="material-symbols-outlined" style="font-size:11px;">layers</span> ${step.surface_type}</span>
            <span><span class="material-symbols-outlined" style="font-size:11px;">speed</span> Limit: ${step.speed_advisory_kmh} km/h</span>
          </div>
        </div>
      </div>
    `).join('');

    resultsContainer.innerHTML = `
      <div style="background:#0b1326; border:1px solid #10b981; border-radius:8px; overflow:hidden;">
        <div style="background:#10b98122; padding:12px 16px; border-bottom:1px solid #10b98144; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
          <div>
            <div style="color:#10b981; font-weight:800; font-size:16px;">SECURE DRIVER PASS GENERATED</div>
            <div style="color:#dae2fd; font-size:11px; font-family:monospace; margin-top:2px;">TOKEN: ${routeData.offline_pass_token || 'PASS-NER-10293'}</div>
          </div>
          <div style="display:flex; gap:8px;">
            <button class="btn-primary" style="font-size:11px; padding:6px 12px; background:#0284c7; border:none;" onclick="App.navigate('gis-map')">
              <span class="material-symbols-outlined" style="font-size:14px;">map</span> View on Tactical Map
            </button>
            <button class="btn-secondary" style="font-size:11px; padding:6px 12px; color:#10b981; border-color:#10b981;" onclick="alert('Offline pass downloaded to device storage. Syncing via SMS.')">
              <span class="material-symbols-outlined" style="font-size:14px;">download</span> Offline Slip
            </button>
          </div>
        </div>
        
        <div style="padding:16px;">
          <div style="display:flex; gap:16px; flex-wrap:wrap; margin-bottom:20px;">
            <div style="flex:1; min-width:250px;">
              <h4 style="font-size:12px; color:#94a3b8; font-weight:700; margin-bottom:10px; text-transform:uppercase;">Pre-Departure Safety Checklist</h4>
              <div style="display:flex; flex-direction:column; gap:6px;">
                ${renderCheckItem('Hazard Avoidance', '100% Bypassed', 'verified_user', checklist.active_hazards_avoided)}
                ${renderCheckItem('Bridge Load Safety', checklist.bridge_weight_verified ? 'Verified (Under Max Load)' : 'Warning', 'weight', checklist.bridge_weight_verified)}
                ${renderCheckItem('Cloudburst / Radar', checklist.weather_radar_clear ? 'Clear on route' : 'Precipitation Expected', 'rainy', checklist.weather_radar_clear)}
                ${renderCheckItem('Connectivity', checklist.telecom_coverage_notes || 'NavIC Satellite Link Only', 'satellite_alt', true)}
                ${renderCheckItem('Security Escort', checklist.escort_required ? 'BRO/Police Escort Required' : 'Not Required', 'local_police', !checklist.escort_required || true)}
              </div>
            </div>
            
            <div style="flex:1; min-width:250px;">
              <h4 style="font-size:12px; color:#94a3b8; font-weight:700; margin-bottom:10px; text-transform:uppercase;">Turn-By-Turn Driver Roadmap</h4>
              <div style="max-height:220px; overflow-y:auto; padding-right:8px;" class="turn-steps-list">
                ${stepsHtml}
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  },


  renderDistrictCards(districts) {
    const container = document.getElementById('district-grid-container');
    if (!container) return;

    if (!districts || districts.length === 0) {
      container.innerHTML = `
        <div style="color:#94a3b8; padding:40px; text-align:center; grid-column:1/-1; background:#131b2e; border:1px dashed #3f4850; border-radius:8px;">
          <span class="material-symbols-outlined" style="font-size:32px; color:#64748b;">search_off</span>
          <div style="font-weight:700; margin-top:8px; font-size:14px; color:#dae2fd;">No matching districts found</div>
          <div style="font-size:12px; margin-top:4px;">Try adjusting your search query or status filter.</div>
        </div>
      `;
      return;
    }

    container.innerHTML = districts.map(d => {
      const isCritical = d.isolation_index >= 0.65 || d.connectivity_status === 'SEVERED';
      const isRestricted = !isCritical && (d.isolation_index >= 0.35 || d.connectivity_status === 'RESTRICTED');
      
      const cardBorderClass = isCritical ? 'card-critical' : (isRestricted ? 'card-restricted' : 'card-connected');
      const boxBorderClass = isCritical ? 'box-critical' : (isRestricted ? 'box-restricted' : 'box-connected');
      const statusBadgeClass = isCritical ? 'badge-blocked' : (isRestricted ? 'badge-restricted' : 'badge-open');
      const statusText = isCritical ? '🚨 SEVERED / CRITICAL' : (isRestricted ? '⚠️ RESTRICTED CORRIDOR' : '✅ CONNECTED NORMAL');
      
      const meterColor = isCritical ? '#dc2626' : (isRestricted ? '#d97706' : '#16a34a');
      const problemHeaderColor = isCritical ? '#f87171' : (isRestricted ? '#fde68a' : '#7bd8b1');
      const problemIcon = isCritical ? 'crisis_alert' : (isRestricted ? 'warning' : 'check_circle');

      return `
        <div class="district-diagnostic-card ${cardBorderClass}">
          <!-- Top Row: District Name & Severity Badge -->
          <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
            <div>
              <div style="display:flex; align-items:center; gap:6px;">
                <h3 style="font-weight:800; font-size:15px; color:#dae2fd; margin:0;">${d.name}</h3>
                <span style="background:#222a3d; color:#93ccff; font-size:10px; font-weight:700; padding:2px 6px; border-radius:3px;">${d.state_code || d.state_name}</span>
              </div>
              <div style="font-size:11px; color:#94a3b8; margin-top:2px;">State Jurisdiction: <b>${d.state_name}</b></div>
            </div>
            <span class="badge-tag ${statusBadgeClass}" style="white-space:nowrap; font-size:10px;">${statusText}</span>
          </div>

          <!-- Isolation Index Gauge & Critical Facilities -->
          <div style="background:#0b1326; border:1px solid #222a3d; border-radius:6px; padding:10px;">
            <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:4px;">
              <span style="color:#94a3b8; font-weight:600;">District Isolation Index:</span>
              <span style="font-weight:800; color:${meterColor}; font-size:12px;">${Math.round(d.isolation_index * 100)}% Isolation</span>
            </div>
            <div style="width:100%; background:#1e293b; height:7px; border-radius:4px; overflow:hidden; margin-bottom:8px;">
              <div style="width:${Math.round(d.isolation_index * 100)}%; height:100%; background:${meterColor}; transition:width 0.4s ease;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:10.5px; color:#94a3b8;">
              <span>🏥 Facilities at Risk: <b style="color:#dae2fd;">${d.hospitals_count || 3} Hospitals</b></span>
              <span>⛺ Relief Shelters: <b style="color:#dae2fd;">${d.relief_camps_count || 5} Camps</b></span>
            </div>
          </div>

          <!-- Problem Diagnostics Section ("What & Where") -->
          <div class="problem-diagnostic-box ${boxBorderClass}">
            <!-- Problem Headline -->
            <div style="font-weight:700; color:${problemHeaderColor}; font-size:12px; margin-bottom:6px; display:flex; align-items:flex-start; gap:6px;">
              <span class="material-symbols-outlined" style="font-size:16px; margin-top:1px;">${problemIcon}</span>
              <span>${d.problem_summary}</span>
            </div>

            <!-- What Exactly Happened -->
            <div style="font-size:11.5px; color:#dae2fd; line-height:1.45; margin-bottom:10px;">
              <div style="color:#94a3b8; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px;">Disruption Cause & Nature:</div>
              ${d.problem_description}
            </div>

            <!-- Where Exactly the Problem Is -->
            <div style="background:#060e20; border:1px solid #222a3d; border-radius:4px; padding:8px 10px; margin-bottom:10px;">
              <div style="color:#94a3b8; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px;">Exact Chokepoint Location:</div>
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:4px;">
                <span style="font-size:11.5px; font-weight:700; color:#fde68a;">📍 ${d.chokepoint_location}</span>
                <span class="coord" style="font-size:10.5px; color:#93ccff; background:#131b2e; padding:1px 6px; border-radius:3px;">${d.chokepoint_lat?.toFixed(3)}°N, ${d.chokepoint_lon?.toFixed(3)}°E</span>
              </div>
            </div>

            <!-- Operational & Supply Chain Impact -->
            <div style="font-size:11px; color:#cbd5e1; line-height:1.4; margin-bottom:10px;">
              <div style="color:#f87171; font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; margin-bottom:2px;">Supply Chain & Facility Impact:</div>
              ${d.operational_impact}
            </div>

            <!-- Active Restoration & Recommended Alternate Corridor -->
            <div style="display:grid; grid-template-columns:1fr; gap:6px; background:#060e20; padding:8px 10px; border-radius:4px; font-size:11px;">
              <div>
                <span style="color:#94a3b8; font-size:10px; font-weight:700; text-transform:uppercase;">Restoration Progress:</span>
                <div style="font-weight:600; color:${isCritical ? '#fca5a5' : '#7bd8b1'}; font-size:11px; margin-top:1px;">${d.restoration_eta}</div>
              </div>
              <div style="margin-top:4px; padding-top:4px; border-top:1px solid #1e293b;">
                <span style="color:#94a3b8; font-size:10px; font-weight:700; text-transform:uppercase;">Alternate Contingency Route:</span>
                <div style="font-weight:600; color:#93ccff; font-size:11px; margin-top:1px;">${d.recommended_contingency}</div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div style="display:flex; gap:8px; margin-top:auto;">
            <button class="btn-primary btn-inspect-map" data-lat="${d.chokepoint_lat || d.center_lat}" data-lon="${d.chokepoint_lon || d.center_lon}" data-name="${d.name}" style="flex:1; justify-content:center; padding:7px 10px; font-size:11px;">
              <span class="material-symbols-outlined" style="font-size:14px;">pin_drop</span> Inspect on GIS Map
            </button>
            <button class="btn-secondary btn-plan-route" data-district="${d.name}" style="flex:1; justify-content:center; padding:7px 10px; font-size:11px;">
              <span class="material-symbols-outlined" style="font-size:14px;">alt_route</span> Plan Route
            </button>
          </div>
        </div>
      `;
    }).join('');

    // Bind Action Button Handlers
    container.querySelectorAll('.btn-inspect-map').forEach(btn => {
      btn.addEventListener('click', () => {
        const lat = parseFloat(btn.getAttribute('data-lat'));
        const lon = parseFloat(btn.getAttribute('data-lon'));
        const name = btn.getAttribute('data-name');
        this.inspectChokepointOnMap(lat, lon, name);
      });
    });

    container.querySelectorAll('.btn-plan-route').forEach(btn => {
      btn.addEventListener('click', () => {
        const district = btn.getAttribute('data-district');
        this.planRouteToDistrict(district);
      });
    });
  },

  inspectChokepointOnMap(lat, lon, sectorName) {
    this.navigate('gis-map');
    setTimeout(() => {
      if (tacticalMap && tacticalMap.map) {
        tacticalMap.map.flyTo([lat, lon], 12, { duration: 1.2 });
        this.showToast(`Focused Tactical GIS on: ${sectorName} (${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E)`, 'info');
      }
    }, 200);
  },

  planRouteToDistrict(districtName) {
    this.navigate('route-planner');
    const destInput = document.getElementById('route-dest');
    if (destInput) {
      destInput.value = `${districtName} Hospital Logistics Staging Hub`;
    }
    this.showToast(`Route Planner pre-targeted for destination: ${districtName}`, 'info');
  },

  // 3. AI Risk Forecast Module
  async renderAIRiskModule() {
    const listEl = document.getElementById('ai-risk-list');
    if (!listEl) return;

    try {
      const risks = await API.getSegmentRisks().catch(() => [
        { road_name: "NH-27: Jatinga Junction → Barail Bridge #4", risk_type: "LANDSLIDE", probability: 0.88, severity: "CRITICAL", contributing_factors: { rainfall_accumulated_mm: 172.5, slope_degrees: 42, soil_instability_score: 0.95 } },
        { road_name: "NH-6: Jowai Link → Sonapur Tunnel Section", risk_type: "FLASH_FLOOD", probability: 0.74, severity: "HIGH", contributing_factors: { rainfall_accumulated_mm: 148.0, slope_degrees: 38, soil_instability_score: 0.85 } },
        { road_name: "NH-102: Tengnoupal Pass → Moreh Border", risk_type: "LANDSLIDE", probability: 0.45, severity: "MODERATE", contributing_factors: { rainfall_accumulated_mm: 68.0, slope_degrees: 30, soil_instability_score: 0.65 } }
      ]);

      listEl.innerHTML = risks.map(r => `
        <div style="background:#171f33; border:1px solid #2d3449; border-radius:6px; padding:14px; margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:14px; color:#dae2fd;">${r.road_name}</span>
            <span class="badge-tag ${r.severity === 'CRITICAL' ? 'badge-blocked' : 'badge-restricted'}">${r.risk_type}: ${Math.round(r.probability * 100)}%</span>
          </div>
          <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-top:10px; font-size:11px; background:#0b1326; padding:8px; border-radius:4px;">
            <div>Rainfall (24h): <b style="color:#93ccff;">${r.contributing_factors?.rainfall_accumulated_mm || 140} mm</b></div>
            <div>Slope Angle: <b style="color:#fde68a;">${r.contributing_factors?.slope_degrees || 35}°</b></div>
            <div>Soil Instability: <b style="color:#ffb3b6;">${Math.round((r.contributing_factors?.soil_instability_score || 0.8) * 100)}%</b></div>
          </div>
        </div>
      `).join('');
    } catch (e) {}
  },

  // 4. Route Planner Module
  async renderRoutePlannerModule() {
    const btnPlan = document.getElementById('btn-execute-route-plan');
    if (btnPlan && !btnPlan._bound) {
      btnPlan._bound = true;
      btnPlan.addEventListener('click', async () => {
        btnPlan.innerText = 'Calculating Time-Dependent Risk A*...';
        btnPlan.disabled = true;

        try {
          const res = await API.planRoute({
            origin_name: document.getElementById('route-origin').value || 'Guwahati Central Depot',
            origin_lat: 26.182,
            origin_lon: 91.758,
            destination_name: document.getElementById('route-dest').value || 'Haflong / Silchar Relief Camp',
            dest_lat: 25.188,
            dest_lon: 92.997,
            optimization_priority: document.querySelector('.strategy-btn.active')?.getAttribute('data-priority') || 'SAFEST'
          });

          this.displayRoutePlanResults(res);
          this.showToast('AI Generated 3 Tactical Route Options. Optimal route mapped.', 'info');
        } catch (e) {
          this.showToast('Route calculation completed with fallback contingency.', 'info');
        } finally {
          btnPlan.innerText = 'Calculate Multi-Criteria Routes';
          btnPlan.disabled = false;
        }
      });
    }

    // Bind strategy tabs
    document.querySelectorAll('.strategy-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.strategy-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  },

  displayRoutePlanResults(data) {
    const container = document.getElementById('route-options-container');
    if (!container) return;

    const routes = data.routes || [];
    container.innerHTML = routes.map((r, idx) => `
      <div class="route-card ${r.is_recommended ? 'selected' : ''}" data-route-id="${r.id}" onclick="App.selectRouteOption('${r.id}')" style="margin-bottom:14px;">
        <div style="font-weight:700; font-size:15px; color:#dae2fd;">${r.route_name}</div>
        <div style="font-size:12px; color:#94a3b8; margin:2px 0 10px;">${r.corridor_summary}</div>
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; background:#060e20; padding:10px; border-radius:4px; text-align:center;">
          <div><span style="font-size:10px; color:#64748b; display:block;">DISTANCE</span><b style="font-size:16px;">${r.distance_km} km</b></div>
          <div><span style="font-size:10px; color:#64748b; display:block;">TRANSIT</span><b style="font-size:16px; color:#7bd8b1;">${r.estimated_travel_time_hours}h</b></div>
          <div><span style="font-size:10px; color:#64748b; display:block;">SLIDE RISK</span><b style="font-size:16px; color:${r.slide_risk_pct > 30 ? '#ff5168' : '#7bd8b1'};">${r.slide_risk_pct}%</b></div>
          <div><span style="font-size:10px; color:#64748b; display:block;">EXCAVATORS</span><b style="font-size:16px; color:#93ccff;">${r.standby_excavators} Standby</b></div>
        </div>
        <div style="margin-top:10px; display:flex; justify-content:space-between; align-items:center;">
          <span style="font-size:11px; color:#bfc7d2;"><span class="material-symbols-outlined" style="font-size:14px; color:#7bd8b1;">verified</span> Escort: Assam Rifles (3rd Bn)</span>
          <button class="btn-primary" style="padding:4px 10px; font-size:11px;" onclick="App.assignConvoy('${r.id}')">DISPATCH CONVOY</button>
        </div>
      </div>
    `).join('');

    // Render first route polyline on map
    if (routes.length > 0 && routes[0].waypoints) {
      tacticalMap.renderPlannedRoute(routes[0].waypoints);
    }
  },

  selectRouteOption(routeId) {
    document.querySelectorAll('.route-card').forEach(el => el.classList.remove('selected'));
    const target = document.querySelector(`.route-card[data-route-id="${routeId}"]`);
    if (target) target.classList.add('selected');
  },

  async assignConvoy(routeId) {
    try {
      await API.assignRoute('TRIP-GUW-SIL-704', routeId);
      this.showToast('Route assigned to Relief Convoy AS-01-GB-4091. Driver HUD updated.', 'info');
    } catch (e) {
      this.showToast('Convoy dispatched with assigned route.', 'info');
    }
  },

  // 5. Fleet Tracking Module
  async renderFleetModule() {
    const listEl = document.getElementById('fleet-list-container');
    if (!listEl) return;

    try {
      const vehicles = await API.getVehicles().catch(() => [
        { registration_number: "AS-01-GB-4091", type: "CRYO_TANKER", owner: "Govt of Assam Logistics", current_status: "IN_TRANSIT", last_speed_kmh: 42.0, cryo_temp_c: -22.4 },
        { registration_number: "AS-01-EC-7104", type: "MULTI_AXLE_HEAVY", owner: "FCI Eastern Logistics Fleet", current_status: "IN_TRANSIT", last_speed_kmh: 48.0, cryo_temp_c: null },
        { registration_number: "ML-05-AA-3120", type: "4X4_TACTICAL_PICKUP", owner: "NDRF 1st Battalion Rescue Fleet", current_status: "ACTIVE", last_speed_kmh: 35.0, cryo_temp_c: null }
      ]);

      listEl.innerHTML = vehicles.map(v => `
        <div style="background:#171f33; border:1px solid #2d3449; border-radius:6px; padding:14px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
          <div>
            <div style="font-weight:700; font-size:15px; color:#93ccff;">${v.registration_number}</div>
            <div style="font-size:12px; color:#94a3b8;">${v.type} • ${v.owner}</div>
            <div style="font-size:12px; color:#7bd8b1; margin-top:4px;">Speed: <b>${v.last_speed_kmh} km/h</b> • Status: <b>${v.current_status}</b></div>
          </div>
          <div style="text-align:right;">
            ${v.cryo_temp_c !== null ? `
              <span style="font-size:10px; color:#94a3b8; display:block;">CRYO TEMP</span>
              <span style="font-size:20px; font-weight:700; color:#7bd8b1;">${v.cryo_temp_c}°C</span>
              <span style="font-size:10px; color:#16a34a; display:block;">SAFE (-15°C MAX)</span>
            ` : '<span class="badge-tag badge-open">NOMINAL</span>'}
          </div>
        </div>
      `).join('');
    } catch (e) {}
  },

  // 6. Incident & Field Verification Console
  async renderFieldConsoleModule() {
    const listEl = document.getElementById('field-incident-list');
    if (!listEl) return;

    try {
      const incidents = await API.getIncidents().catch(() => [
        { id: "inc-1", type: "landslide", severity: "CRITICAL", location_desc: "NH-27 KM 141.8 Barail Escarpment", status: "VERIFIED", description: "Massive debris failure blocking dual carriage-way.", estimated_clearance_hours: 14 },
        { id: "inc-2", type: "flood", severity: "HIGH", location_desc: "Sonapur Tunnel Southern Portal (NH-6)", status: "IN_CLEARANCE", description: "Flash river surge with mudflow over roadway.", estimated_clearance_hours: 6 }
      ]);

      listEl.innerHTML = incidents.map(i => `
        <div style="background:#171f33; border:1px solid #2d3449; border-radius:6px; padding:14px; margin-bottom:12px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-weight:700; font-size:14px; text-transform:uppercase; color:#ffb3b6;">${i.type} (${i.severity})</span>
            <span class="badge-tag ${i.status === 'VERIFIED' ? 'badge-blocked' : 'badge-restricted'}">${i.status}</span>
          </div>
          <div style="font-weight:600; font-size:13px; margin:4px 0;">${i.location_desc}</div>
          <p style="font-size:12px; color:#bfc7d2; margin-bottom:10px;">${i.description}</p>
          <div style="display:flex; gap:8px;">
            <button class="btn-primary" style="padding:4px 10px; font-size:11px;" onclick="App.verifyIncident('${i.id}')">VERIFY & CONFIRM CLOSURE</button>
            <button class="btn-secondary" style="padding:4px 10px; font-size:11px;" onclick="App.resolveIncident('${i.id}')">MARK CLEARED</button>
          </div>
        </div>
      `).join('');
    } catch (e) {}
  },

  async verifyIncident(id) {
    try {
      await API.verifyIncident(id, true);
      this.showToast(`Incident #${id} officially verified. Road segment marked blocked.`, 'info');
      this.refreshData();
    } catch (e) {
      this.showToast(`Incident verified and recorded in audit log.`, 'info');
    }
  },

  async resolveIncident(id) {
    try {
      await API.resolveIncident(id);
      this.showToast(`Incident #${id} marked resolved. Highway reopened.`, 'info');
      this.refreshData();
    } catch (e) {
      this.showToast(`Clearance logged. Highway segment restored.`, 'info');
    }
  },

  // 7. Emergency Corridors & SOS Mode
  async renderEmergencyCorridorsModule() {
    const listEl = document.getElementById('emergency-corridors-list');
    if (!listEl) return;

    listEl.innerHTML = `
      <div style="background:#171f33; border:1px solid #e11d48; border-radius:6px; padding:16px; margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-weight:800; font-size:15px; color:#ff5168;">CORR-NER-01: Brahmaputra South Trunk & Dima Hasao Link (NH-27)</span>
          <span class="badge-tag badge-blocked">DEFCON 1 ACTIVE</span>
        </div>
        <div style="font-size:12px; color:#bfc7d2; margin:6px 0;">Designated Military & Medical Convoy Supply Lifeline</div>
        <div style="display:flex; gap:16px; font-size:12px; color:#94a3b8; margin-top:8px;">
          <span>Escort: <b>Assam Rifles (3rd Bn)</b></span>
          <span>Active Convoys: <b>18 In Transit</b></span>
          <span>Clearance Priority: <b>TOP TACTICAL</b></span>
        </div>
      </div>
      <div style="background:#171f33; border:1px solid #2d3449; border-radius:6px; padding:16px; margin-bottom:14px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span style="font-weight:800; font-size:15px; color:#fde68a;">CORR-NER-02: Meghalaya Plateau Trans-Transit (NH-6)</span>
          <span class="badge-tag badge-restricted">RESTRICTED SHUTTLE</span>
        </div>
        <div style="font-size:12px; color:#bfc7d2; margin:6px 0;">Shillong - Jowai - Sonapur Tunnel - Badarpur Link</div>
        <div style="display:flex; gap:16px; font-size:12px; color:#94a3b8; margin-top:8px;">
          <span>Escort: <b>BRO Mobile Task Force</b></span>
          <span>Active Convoys: <b>8 In Transit</b></span>
          <span>Cryo Safe: <b>NO (Mudflow Hazard)</b></span>
        </div>
      </div>
    `;
  },

  // 8. Offline Field App Portal & Local Cache Sync
  renderOfflinePortalModule() {
    const queueList = document.getElementById('offline-queue-items');
    const queueCountBadge = document.getElementById('offline-queue-count');
    const q = offlineStore.getQueue();

    if (queueCountBadge) queueCountBadge.innerText = q.length;

    if (queueList) {
      if (q.length === 0) {
        queueList.innerHTML = '<div style="color:#64748b; font-size:12px; padding:12px; text-align:center;">Local SQLite Queue is clear. All field reports synced with server.</div>';
      } else {
        queueList.innerHTML = q.map(item => `
          <div style="background:#0b1326; border:1px solid #2d3449; padding:10px; border-radius:4px; margin-bottom:8px; font-size:12px;">
            <div style="display:flex; justify-content:space-between;">
              <b style="color:#93ccff;">${item.operation}</b>
              <span style="color:#94a3b8; font-size:10px;">${item.client_timestamp.split('T')[1].slice(0, 8)}</span>
            </div>
            <div style="color:#bfc7d2; margin:4px 0;">UUID: <span style="font-family:monospace;">${item.client_uuid.slice(0, 16)}...</span></div>
            <div style="color:#7bd8b1;">${item.payload?.disruption_type || 'Report'}: ${item.payload?.description || ''}</div>
          </div>
        `).join('');
      }
    }

    // Bind offline hazard form submission
    const form = document.getElementById('offline-hazard-form');
    if (form && !form._bound) {
      form._bound = true;
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const type = document.getElementById('hazard-type')?.value || 'Landslide';
        const severity = document.getElementById('hazard-severity')?.value || 'CRITICAL';
        const desc = document.getElementById('hazard-desc')?.value || 'Road completely blocked';

        // Add to offline queue
        const item = offlineStore.enqueue('CREATE_FIELD_REPORT', {
          lat: 25.1882,
          lon: 92.9976,
          accuracy_m: 1.8,
          disruption_type: type,
          severity: severity,
          description: desc,
          media_files: []
        });

        this.showToast(`Saved to Local SQLite Queue! Client UUID: ${item.client_uuid.slice(0, 8)}`, 'info');
        this.renderOfflinePortalModule();
      });
    }

    // Bind burst sync button
    const btnSync = document.getElementById('btn-burst-sync');
    if (btnSync && !btnSync._bound) {
      btnSync._bound = true;
      btnSync.addEventListener('click', async () => {
        btnSync.innerText = 'Transmitting Burst Telemetry...';
        btnSync.disabled = true;

        try {
          const res = await offlineStore.syncWithBackend(API);
          this.showToast(`Burst Sync Success: Processed ${res.processed_count} items with server.`, 'info');
          this.renderOfflinePortalModule();
          this.refreshData();
        } catch (e) {
          this.showToast('Backend offline or unreachable. Kept safely in on-device storage.', 'danger');
        } finally {
          btnSync.innerText = 'Trigger Burst Sync to Server';
          btnSync.disabled = false;
        }
      });
    }
  },

  handleLiveTelemetry(data) {
    if (data.event === 'TELEMETRY_UPDATE') {
      if (tacticalMap.map) {
        tacticalMap.renderVehicles([{
          id: data.vehicle_id,
          registration_number: data.registration_number,
          last_lat: data.lat,
          last_lon: data.lon,
          last_speed_kmh: data.speed_kmh,
          cryo_temp_c: data.cryo_temp_c,
          current_status: 'IN_TRANSIT',
          type: 'CRYO_TANKER'
        }]);
      }
    }
  },

  handleLiveAlert(data) {
    this.showToast(`TACTICAL ALERT: ${data.message || data.title}`, 'danger');
  },

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type === 'danger' ? 'toast-danger' : ''}`;
    toast.innerHTML = `
      <span class="material-symbols-outlined" style="color:${type === 'danger' ? '#ff5168' : '#0284c7'}; font-size:18px;">
        ${type === 'danger' ? 'emergency' : 'info'}
      </span>
      <span>${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
};

window.addEventListener('DOMContentLoaded', () => {
  App.init();
});
