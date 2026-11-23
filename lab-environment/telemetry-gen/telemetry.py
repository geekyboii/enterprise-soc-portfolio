#!/usr/bin/env python3
"""
Northstar FinTech — Enterprise Baseline Telemetry Generator (ns-corp-gw-01)
Produces realistic benign corporate web traffic, firewall logs, and DNS queries
so the SOC SIEM reflects a living enterprise environment.
"""

import json
import os
import random
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

FIREWALL_LOG = "/var/log/corp/firewall.jsonl"
DNS_LOG = "/var/log/corp/dns.jsonl"
WEB_URL = os.environ.get("WEB_TARGET", "http://ns-web-01")

BENIGN_USERS = [
    ("198.51.100.15", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128.0"),
    ("203.0.113.42", "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) Safari/605.1"),
    ("203.0.113.88", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/128.0"),
    ("10.10.20.50", "Northstar-UptimeMonitor/2.1"),
]

BENIGN_PATHS = [
    ("/", "GET"),
    ("/health", "GET"),
    ("/login", "GET"),
    ("/api/v1/accounts", "GET"),
]

BENIGN_DOMAINS = [
    ("login.microsoftonline.com", "20.190.159.0"),
    ("api.github.com", "140.82.114.6"),
    ("s3.us-east-1.amazonaws.com", "52.216.40.12"),
    ("portal.northstar-fintech.local", "10.10.10.10"),
    ("updates.ubuntu.com", "91.189.91.81"),
    ("slack.com", "54.192.20.14"),
]

CORP_WORKSTATIONS = ["10.10.20.101", "10.10.20.102", "10.10.20.105", "10.10.20.112"]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_jsonl(path: str, record: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def emit_benign_web() -> None:
    src_ip, ua = random.choice(BENIGN_USERS)
    if src_ip == "10.10.20.50":
        path, method = "/health", "GET"
    else:
        path, method = random.choice(BENIGN_PATHS)
    req = urllib.request.Request(
        f"{WEB_URL}{path}",
        method=method,
        headers={"X-Forwarded-For": src_ip, "User-Agent": ua},
    )
    try:
        with urllib.request.urlopen(req, timeout=3):
            pass
    except urllib.error.HTTPError:
        pass
    except Exception:
        pass


def emit_benign_firewall() -> None:
    src = random.choice(CORP_WORKSTATIONS)
    domain, dst_ip = random.choice(BENIGN_DOMAINS)
    # Occasional benign blocked telemetry (e.g. stray external port scan hitting perimeter DENY)
    if random.random() < 0.15:
        record = {
            "timestamp": utc_now(),
            "host": "ns-corp-gw-01",
            "event_type": "firewall",
            "src_ip": f"185.220.101.{random.randint(10, 90)}",
            "dst_ip": "10.10.10.10",
            "dst_port": random.choice([23, 445, 3389, 8080]),
            "proto": "TCP",
            "action": "DENY",
            "bytes": 60,
            "rule_id": "FW-EXT-DEFAULT-DENY",
        }
    else:
        record = {
            "timestamp": utc_now(),
            "host": "ns-corp-gw-01",
            "event_type": "firewall",
            "src_ip": src,
            "dst_ip": dst_ip,
            "dst_port": 443,
            "proto": "TCP",
            "action": "ALLOW",
            "bytes": random.randint(1200, 48000),
            "rule_id": "FW-CORP-HTTPS-OUT",
        }
    append_jsonl(FIREWALL_LOG, record)


def emit_benign_dns() -> None:
    client = random.choice(CORP_WORKSTATIONS)
    domain, answer = random.choice(BENIGN_DOMAINS)
    record = {
        "timestamp": utc_now(),
        "host": "ns-corp-gw-01",
        "event_type": "dns",
        "client_ip": client,
        "query": domain,
        "qtype": "A",
        "rcode": "NOERROR",
        "answer": answer,
    }
    append_jsonl(DNS_LOG, record)


def emit_onboarding_test() -> None:
    """Generate a single controlled marker across Web, Firewall, and DNS for SOC onboarding validation."""
    req = urllib.request.Request(
        f"{WEB_URL}/health?soc_onboarding_check=ok",
        method="GET",
        headers={"X-Forwarded-For": "10.10.20.50", "User-Agent": "Northstar-SOC-OnboardingCheck/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=3):
            pass
    except Exception:
        pass

    append_jsonl(FIREWALL_LOG, {
        "timestamp": utc_now(),
        "host": "ns-corp-gw-01",
        "event_type": "firewall",
        "src_ip": "10.10.20.50",
        "dst_ip": "10.10.10.10",
        "dst_port": 80,
        "proto": "TCP",
        "action": "ALLOW",
        "bytes": 512,
        "rule_id": "FW-SOC-ONBOARDING-TEST",
    })
    append_jsonl(DNS_LOG, {
        "timestamp": utc_now(),
        "host": "ns-corp-gw-01",
        "event_type": "dns",
        "client_ip": "10.10.20.50",
        "query": "soc-onboarding-check.northstar-fintech.local",
        "qtype": "A",
        "rcode": "NOERROR",
        "answer": "10.10.30.20",
    })
    print("Emitted SOC onboarding test events across web, firewall, and DNS.")


def run_daemon() -> None:
    print("[ns-corp-gw-01] Starting Northstar FinTech baseline telemetry generator...")
    # Seed initial baseline batch immediately on startup
    for _ in range(5):
        emit_benign_web()
        emit_benign_firewall()
        emit_benign_dns()

    while True:
        emit_benign_web()
        emit_benign_firewall()
        emit_benign_dns()
        time.sleep(8)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "daemon"
    if mode == "onboarding-test":
        emit_onboarding_test()
    else:
        run_daemon()
