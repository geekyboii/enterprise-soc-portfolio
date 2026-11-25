# Northstar FinTech — Live Enterprise SOC Lab

This directory contains a self-contained, reproducible Docker Compose enterprise simulation used to practice and validate real-world Tier 1 / Tier 2 SOC workflows on **Windows 11**, **macOS**, or **Linux**.

## Architecture

| Container | Network Zone & IP | Role | Telemetry Shipped |
| :--- | :--- | :--- | :--- |
| `ns-web-01` | DMZ (`10.10.10.10`) | Customer Banking Portal (`Nginx 1.27`) | Structured JSON access logs + error logs |
| `ns-bastion-01` | DMZ (`10.10.10.20`) | Linux Privileged Bastion (`OpenSSH` + `sudo`) | RFC3164 Syslog (`auth.log`) |
| `ns-corp-gw-01` | Corp (`10.10.20.10`) | Firewall, Corporate DNS & Baseline Traffic Generator | Firewall JSONL + DNS JSONL |
| `ns-promtail-01` | SecOps (`10.10.30.10`) | Enterprise Log Forwarder (`Promtail 3.1`) | Tags & ships all log streams to SIEM |
| `ns-loki-01` | SecOps (`10.10.30.20`) | Central SIEM Log Engine (`Loki 3.1`) | Indexes telemetry for LogQL queries |
| `ns-grafana-01` | SecOps (`10.10.30.30`) | SOC SIEM Console & Dashboards (`Grafana 11.2`) | Pre-provisioned SOC Overview Dashboard |

## Quick Start (Windows 11 PowerShell / macOS / Linux)

**Prerequisites:** [Git](https://git-scm.com/downloads) and [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running).

```powershell
# 1. Start the entire enterprise lab and SIEM stack
docker compose -f lab-environment/docker-compose.yml up -d --build

# 2. Check that all 6 containers are running
docker compose -f lab-environment/docker-compose.yml ps

# 3. Open the live Grafana SIEM Console in your browser:
#    http://localhost:3000

# 4. Stop the lab when finished (keeps your SIEM data saved)
docker compose -f lab-environment/docker-compose.yml down
```

## Optional Linux/WSL Helper CLI

If running inside **WSL 2 (Ubuntu)**, macOS, or Linux:

```bash
./lab-environment/soc-lab.sh up
./lab-environment/soc-lab.sh status
./lab-environment/soc-lab.sh verify-onboarding
./lab-environment/soc-lab.sh query '{host="ns-web-01", log_type="nginx_access"} | json' 10
./lab-environment/soc-lab.sh down
```
