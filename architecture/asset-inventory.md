# Enterprise Asset Inventory & Criticality Classification (CMDB)

**Organization:** Northstar FinTech (Simulated Enterprise)  
**Document Owner:** Security Operations Center (SOC) & IT Infrastructure  
**Review Cadence:** Quarterly / Upon Major Architecture Change  

> **Why this matters in a real SOC:** An analyst cannot prioritize an alert without knowing *what* the host does, *who* owns it, and *how critical* it is to the business. A failed login on a Tier-1 Admin Bastion or Customer Payment Portal is triaged very differently from a test sandbox.

---

## Criticality Tiers (Business Impact)

| Tier | Definition | Target SOC Triage SLA | Escalation Path |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Crown Jewel)** | Internet-facing production apps, privileged access gateways, or security infrastructure. Compromise causes direct financial, regulatory (PCI-DSS/SOC 2), or domain-wide impact. | **15 minutes** | Immediate escalation to Tier 2 SOC + Infrastructure On-Call |
| **Tier 2 (Business Critical)** | Core internal corporate services (DNS, Firewall, Identity logs, internal APIs). Compromise enables lateral movement or data exfiltration. | **30 minutes** | Escalate to Tier 2 SOC + Network/IAM Owner |
| **Tier 3 (Standard)** | Non-production dev/staging systems or low-privilege internal utilities. | **4 hours** | Standard ticket to System Owner |

---

## Enterprise Asset Registry

| Hostname | Role & Technology | Network Zone | Container / Internal IP | Exposed Services | Criticality | Asset Owner | Expected Baseline Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ns-web-01` | Customer Banking Portal & Public API (`Nginx 1.27`) | DMZ (`10.10.10.0/24`) | `10.10.10.10` | `80/tcp` (HTTP) | **Tier 1** | Web Platform Team | High volume of `GET /`, `/login`, `/api/v1/accounts`, `/health`; steady `200`/`302` responses; occasional user `401` on typos. |
| `ns-bastion-01` | Linux Privileged Jump Host (`OpenSSH` + `sudo`) | DMZ Mgmt (`10.10.10.0/24`) | `10.10.10.20` | `22/tcp` (SSH) | **Tier 1** | Cloud & Linux Ops | Low volume of SSH key logins from known corporate VPN IPs (`198.51.100.10–20`) during business hours (`08:00–19:00 UTC`); rare authorized `sudo` commands. |
| `ns-corp-gw-01` | Perimeter Firewall, Internal DNS Resolver & IdP Gateway | Corporate (`10.10.20.0/24`) | `10.10.20.10` | Telemetry Generator / GW | **Tier 2** | Network Security Team | Normal outbound HTTPS (`443`), standard business domain DNS lookups, scheduled backup jobs (`02:00 UTC`), normal SSO logins. |
| `ns-promtail-01` | Enterprise Log Forwarder (`Promtail 3.1`) | SecOps (`10.10.30.0/24`) | `10.10.30.10` | Internal Collector | **Tier 1** | SOC Engineering | Continuously tails asset log directories and ships tagged streams to `ns-loki-01`. Drop in ingestion = P1 Blind-Spot alert. |
| `ns-loki-01` | Central SIEM Log Engine (`Grafana Loki 3.1`) | SecOps (`10.10.30.0/24`) | `10.10.30.20` | `3100/tcp` (Internal API) | **Tier 1** | SOC Engineering | Indexes incoming telemetry and serves LogQL search queries for SOC analysts. |
| `ns-grafana-01` | SOC SIEM Console & Alerting (`Grafana 11.2`) | SecOps (`10.10.30.0/24`) | `10.10.30.30` | `3000/tcp` (SOC UI) | **Tier 1** | SOC Operations | Analyst investigation console, dashboards, and alert rule evaluation. |

---

## Known Benign Actors & Maintenance Windows (False-Positive Context)

Real SOCs maintain an **Allowlist / Context Register** so analysts don't chase authorized activity:

| Source IP / Account | Owner | Purpose | Normal Schedule |
| :--- | :--- | :--- | :--- |
| `10.10.20.50` (`svc-monitor`) | SRE / Uptime Monitoring | Hits `GET /health` on `ns-web-01` every 60s | 24/7 |
| `198.51.100.15` (`admin-ops`) | Linux Ops On-Call | Authorized SSH bastion administration | Business hours + scheduled Sunday `02:00–03:00 UTC` patching |
| `10.10.20.60` (`svc-backup`) | Infrastructure Team | Nightly automated backup transfer | Daily `02:00 UTC` |

---

## Interview Talking Points (Phase 1)
- **Q: "What is the first thing you check when an alert fires on an unfamiliar hostname?"**  
  *A: Check the CMDB / Asset Inventory to understand business criticality, network zone (internet-facing vs. internal), asset owner, and expected baseline behavior — because context determines severity and escalation SLA.*
- **Q: "Why is the SIEM log shipper (`ns-promtail-01`) classified as Tier 1?"**  
  *A: If an attacker disables log forwarding or a shipper silently fails, the SOC goes blind (MITRE ATT&CK `T1562.001` — Impair Defenses). Telemetry health is itself a Tier-1 security control.*
