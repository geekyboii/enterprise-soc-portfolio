#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOKI_URL="http://127.0.0.1:3100"

usage() {
  cat <<EOF
Northstar FinTech — SOC Lab Control CLI

Usage:
  ./soc-lab.sh up                   Start all enterprise assets and the SIEM stack
  ./soc-lab.sh down                 Stop the lab stack (preserves SIEM data)
  ./soc-lab.sh status               Show container health and SIEM readiness
  ./soc-lab.sh verify-onboarding    Send test events across all assets and verify SIEM ingestion
  ./soc-lab.sh query '<LogQL>' [N]  Run a LogQL SIEM query (default limit: 15 events)
EOF
}

cmd_query() {
  local expr="${1:-}"
  local limit="${2:-15}"
  if [[ -z "$expr" ]]; then
    echo "Error: provide a LogQL query, e.g. ./soc-lab.sh query '{host=\"ns-web-01\"}'"
    exit 1
  fi
  local end_ns start_ns
  end_ns="$(date +%s)000000000"
  start_ns="$(( $(date +%s) - 3600 ))000000000"

  curl -sG "${LOKI_URL}/loki/api/v1/query_range" \
    --data-urlencode "query=${expr}" \
    --data-urlencode "start=${start_ns}" \
    --data-urlencode "end=${end_ns}" \
    --data-urlencode "limit=${limit}" \
    --data-urlencode "direction=BACKWARD" | jq -r '
      if .status != "success" then
        "SIEM Query Error: " + (. | tostring)
      else
        .data.result[] |
        .stream as $s |
        .values[] |
        "[\($s.host) | \($s.log_type) | \($s.tier)] \(.[1])"
      end
    '
}

cmd_verify() {
  echo "=== Running Enterprise SIEM Log Onboarding Verification ==="
  echo "[1/3] Triggering controlled test events on ns-web-01, ns-corp-gw-01, and ns-bastion-01..."
  docker exec ns-corp-gw-01 python3 /app/telemetry.py onboarding-test
  docker exec ns-bastion-01 logger -p auth.info -t soc-onboarding "SOC onboarding verification marker on ns-bastion-01"
  echo "[2/3] Waiting 4 seconds for Promtail -> Loki ingestion..."
  sleep 4
  echo "[3/3] Checking active log streams in SIEM (ns-loki-01):"
  curl -sG "${LOKI_URL}/loki/api/v1/series" \
    --data-urlencode "match[]={job=\"northstar-soc\"}" | jq -r '
      .data[] | "  ✓ host=\(.host)  log_type=\(.log_type)  tier=\(.tier)  env=\(.env)"
    ' | sort -u
}

case "${1:-}" in
  up)
    docker compose -f "${SCRIPT_DIR}/docker-compose.yml" up -d --build
    ;;
  down)
    docker compose -f "${SCRIPT_DIR}/docker-compose.yml" down
    ;;
  status)
    docker compose -f "${SCRIPT_DIR}/docker-compose.yml" ps
    echo ""
    echo -n "Loki SIEM API:   "
    curl -s "${LOKI_URL}/ready" || echo "unreachable"
    echo ""
    echo -n "Grafana Console: "
    curl -s "http://127.0.0.1:3000/api/health" | jq -r '.database // "unreachable"' 2>/dev/null || echo "unreachable"
    ;;
  verify-onboarding)
    cmd_verify
    ;;
  query)
    cmd_query "${2:-}" "${3:-15}"
    ;;
  *)
    usage
    exit 1
    ;;
esac
