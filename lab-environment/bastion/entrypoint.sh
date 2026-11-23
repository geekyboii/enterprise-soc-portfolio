#!/bin/sh
set -e

mkdir -p /var/log/bastion
touch /var/log/bastion/auth.log
chmod 644 /var/log/bastion/auth.log

# Start BusyBox syslogd writing RFC3164 syslog events (sshd, sudo, useradd) to shared SIEM log volume
syslogd -O /var/log/bastion/auth.log -S

# Log startup marker for SOC onboarding verification
logger -p auth.info -t bastion-init "ns-bastion-01 security logging initialized (UTC)"

# Run OpenSSH daemon in foreground (logging to syslogd -> /var/log/bastion/auth.log)
exec /usr/sbin/sshd -D
