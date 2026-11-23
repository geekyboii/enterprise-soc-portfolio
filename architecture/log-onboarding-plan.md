# Enterprise SIEM Log Onboarding Plan

**Organization:** Northstar FinTech  
**Compliance Drivers:** PCI-DSS v4.0 (Requirement 10 — Log and Monitor All Access), SOC 2 Type II (CC7.2 — System Monitoring)  

> **Why this matters in a real SOC:** Enterprises don't blindly ingest *every* byte of data into a SIEM (that explodes licensing costs and drowns analysts in noise). SOC teams onboard **high-signal security telemetry** explicitly mapped to real attacker behaviors (MITRE ATT&CK).

---

## Onboarded Telemetry Sources

| Log Source | Asset | File / Format | SIEM Labels | Key Security Fields | Threats Detected (MITRE ATT&CK) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Web Access Logs** | `ns-web-01` | `/var/log/nginx/access.log` (JSON) | `host="ns-web-01"`, `log_type="nginx_access"`, `tier="tier-1"` | `remote_addr`, `method`, `uri`, `status`, `user_agent`, `bytes_sent` | Web Scanning (`T1595.002`), Exploit Public-Facing App (`T1190`), SQLi / Path Traversal, Credential Stuffing (`T1110.004`) |
| **Web Error Logs** | `ns-web-01` | `/var/log/nginx/error.log` (Text) | `host="ns-web-01"`, `log_type="nginx_error"`, `tier="tier-1"` | `timestamp`, `level`, `client`, `request`, `message` | Application crashes from exploit attempts, unauthorized directory access |
| **Linux Auth & Sudo Logs** | `ns-bastion-01` | `/var/log/bastion/auth.log` (Syslog) | `host="ns-bastion-01"`, `log_type="linux_auth"`, `tier="tier-1"` | `timestamp`, `process` (`sshd`, `sudo`, `useradd`), `user`, `src_ip`, `result` | SSH Brute Force (`T1110.001`), Valid Accounts (`T1078`), Sudo Abuse (`T1548.003`), Create Account Persistence (`T1136.001`) |
| **Perimeter Firewall Logs** | `ns-corp-gw-01` | `/var/log/corp/firewall.jsonl` (JSON) | `host="ns-corp-gw-01"`, `log_type="firewall"`, `tier="tier-2"` | `src_ip`, `dst_ip`, `dst_port`, `action` (`ALLOW`/`DENY`), `bytes`, `rule_id` | Port Scanning (`T1046`), C2 Outbound Connections (`T1071`), Data Exfiltration (`T1041`) |
| **Corporate DNS Logs** | `ns-corp-gw-01` | `/var/log/corp/dns.jsonl` (JSON) | `host="ns-corp-gw-01"`, `log_type="dns"`, `tier="tier-2"` | `client_ip`, `query`, `qtype`, `rcode` (`NOERROR`/`NXDOMAIN`), `answer` | DNS Tunneling (`T1071.004`), DGA / Malware Beaconing, Phishing Domain Resolution |

---

## Retention & Log Integrity Policy

| Storage Tier | Retention Window | Purpose |
| :--- | :--- | :--- |
| **Hot Storage (SIEM Searchable)** | 90 days | Active alert triage, threat hunting, rapid incident pivoting |
| **Cold Archive (Immutable Object Storage)** | 365 days | Regulatory compliance (PCI-DSS Req. 10.5.1), long-tail breach forensics |

### Mandatory Onboarding Verification Checklist
Before marking any log source "Production Ready" in the SOC, an analyst verifies:
- [x] **Time Synchronization (UTC):** All assets log in UTC so multi-host incident timelines align accurately. *(Verified across `ns-web-01`, `ns-bastion-01`, and `ns-corp-gw-01`)*
- [x] **Structured Parsing:** Critical fields (`src_ip`, `user`, `status`, `action`) are reliably parseable in SIEM queries. *(Verified via LogQL JSON/text extraction)*
- [x] **Metadata Enrichment:** Hostname, environment (`prod`), and asset criticality (`tier-1` / `tier-2`) labels are attached. *(Verified in `ns-promtail-01` -> `ns-loki-01`)*
- [x] **Positive Test Event:** A controlled test event is generated on the asset and confirmed searchable in the SIEM within 60 seconds. *(Verified via `./lab-environment/soc-lab.sh verify-onboarding` + live SSH/sudo validation — caught and remediated missing `sshd -e` syslog routing during onboarding!)*

---

## Interview Talking Points (Phase 1)
- **Q: "Why is UTC time synchronization critical during log onboarding?"**  
  *A: During an incident, you pivot across web servers, Linux hosts, firewalls, and DNS logs. Even a 5-minute clock drift makes reconstructing the attack sequence (initial access → lateral movement → persistence) unreliable or impossible.*
- **Q: "Why JSON logs for Nginx and Firewall instead of raw unstructured text?"**  
  *A: Structured JSON eliminates fragile regex parsing, speeds up SIEM queries, and guarantees consistent field names across detections and dashboards.*
