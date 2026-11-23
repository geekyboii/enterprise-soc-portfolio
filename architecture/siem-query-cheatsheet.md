# Enterprise SOC — SIEM Query Logic Reference (LogQL ↔ Splunk SPL ↔ Sentinel KQL)

> **Career Tip:** Hiring managers rarely expect a junior SOC analyst to memorize every SIEM's syntax. They *do* expect you to understand **investigation logic**: filtering by host/log source, searching for suspicious keywords or status codes, parsing fields, and counting anomalies over time. Below is the exact same SOC hunt logic translated across our live lab (**Loki LogQL**) and the two most common enterprise SIEMs (**Splunk** and **Microsoft Sentinel**).

---

## 1. Filter by Host & Log Source ("Scope the Search")

| Goal | Our Lab (LogQL) | Splunk (SPL) | Microsoft Sentinel (KQL) |
| :--- | :--- | :--- | :--- |
| View all Web Portal access logs | `{host="ns-web-01", log_type="nginx_access"}` | `index=web host="ns-web-01"` | `NginxAccess_CL \| where Host == "ns-web-01"` |
| View all Linux Bastion auth logs | `{host="ns-bastion-01", log_type="linux_auth"}` | `index=linux sourcetype=linux_secure host="ns-bastion-01"` | `Syslog \| where Computer == "ns-bastion-01" and Facility == "auth"` |
| View all Tier-1 (Crown Jewel) assets | `{tier="tier-1"}` | `index=* asset_tier="tier-1"` | `union * \| where AssetTier == "tier-1"` |

---

## 2. Keyword & Failure Hunting ("Spot Suspicious Signals")

| Goal | Our Lab (LogQL) | Splunk (SPL) | Microsoft Sentinel (KQL) |
| :--- | :--- | :--- | :--- |
| Find failed SSH logins | `{log_type="linux_auth"} \|= "Failed password"` | `sourcetype=linux_secure "Failed password"` | `Syslog \| where SyslogMessage has "Failed password"` |
| Find blocked firewall traffic | `{log_type="firewall"} \| json \| action="DENY"` | `index=firewall action="DENY"` | `CommonSecurityLog \| where DeviceAction == "DENY"` |
| Find HTTP 401/403/404 web errors | `{log_type="nginx_access"} \| json \| status >= 400` | `index=web status>=400` | `NginxAccess_CL \| where StatusCode >= 400` |
| Exclude known uptime monitor noise | `{log_type="nginx_access"} \| json \| src_ip != "10.10.20.50"` | `index=web src_ip!="10.10.20.50"` | `NginxAccess_CL \| where SrcIp != "10.10.20.50"` |

---

## 3. Aggregation & Threshold Counting ("Detect Brute Force & Scanning")

| Goal | Our Lab (LogQL) | Splunk (SPL) | Microsoft Sentinel (KQL) |
| :--- | :--- | :--- | :--- |
| Count web errors by Source IP (last 5m) | `sum by (src_ip) (count_over_time({log_type="nginx_access"} \| json \| status >= 400 [5m]))` | `index=web status>=400 \| stats count by src_ip` | `NginxAccess_CL \| where StatusCode >= 400 \| summarize Attempts=count() by SrcIp` |
| Count firewall blocks by destination port | `sum by (dst_port) (count_over_time({log_type="firewall"} \| json \| action="DENY" [15m]))` | `index=firewall action=DENY \| stats count by dst_port` | `CommonSecurityLog \| where DeviceAction == "DENY" \| summarize count() by DestinationPort` |
| Count DNS lookups by queried domain | `sum by (query) (count_over_time({log_type="dns"} \| json [15m]))` | `index=dns \| stats count by query` | `DnsEvents \| summarize count() by Name` |
