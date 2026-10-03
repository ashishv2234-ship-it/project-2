# NER-LogiSense: Role-Based Access Control (RBAC) Matrix

## 1. Overview
Access control in NER-LogiSense enforces least-privilege principles across both Command Headquarters (centralized disaster management and defense logistics) and remote tactical edge units.

---

## 2. Comprehensive Permission Matrix

| Capability / API Operation | Super Admin | State Admin | District Officer | Field Officer | Dispatcher | Driver | Viewer |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **System User Administration** | ✅ Full | ✅ State Only | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Audit Log Inspection** | ✅ Full | ✅ State | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Emergency Disaster Mode Activation** | ✅ Full | ✅ State | ✅ District Only| ❌ | ❌ | ❌ | ❌ |
| **AI Risk Model Retraining / Recompute** | ✅ Full | ✅ Full | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Optimal Route Planning** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Route Assignment & Reoptimization** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Vehicle & Driver Registration** | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Live Fleet GPS Tracking (All Convoys)**| ✅ | ✅ | ✅ District | ✅ Local Sector | ✅ | ❌ Self Only | ✅ Public |
| **Cryo Cold-Chain Telemetry Access** | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ Assigned | ❌ |
| **Field Incident Creation (Offline/Online)**| ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Hazard | ❌ |
| **Incident Verification & Approval** | ✅ | ✅ | ✅ District | ❌ | ❌ | ❌ | ❌ |
| **Road Blockade State Override** | ✅ | ✅ | ✅ | ❌ Propose | ❌ | ❌ | ❌ |
| **Emergency Broadcast Dispatch (SMS/Push)**| ✅ | ✅ | ✅ District | ❌ | ✅ Alerts | ❌ | ❌ |
| **Digital Proof of Delivery (EPOD) Sign** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **SOS Distress Beacon Trigger** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ In-Cab | ❌ |
| **Public Accessibility Dashboard View** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 3. Data Scoping & Row-Level Security (RLS)
- **District Officers:** Automatically filtered to records where `district_id == user.district_id`.
- **Field Officers:** Allowed to create reports and query nearby segments within a 50 km bounding box.
- **Drivers:** Can only query trip route waypoints and telemetry history assigned to their specific vehicle ID.
- **API Tokens:** Every API request validates both the role string in JWT claims and matches required fine-grained permissions against the endpoint decorator before database execution.
