FROM alpine:3.20

RUN apk add --no-cache openssh-server sudo shadow bash && \
    ssh-keygen -A && \
    mkdir -p /var/log/bastion /run/sshd

# Create realistic enterprise accounts
RUN useradd -m -s /bin/bash admin-ops && echo "admin-ops:OpsSecure!2026" | chpasswd && \
    useradd -m -s /bin/bash svc-backup && echo "svc-backup:BackupSvc!2026" | chpasswd && \
    useradd -m -s /bin/bash jdoe && echo "jdoe:UserPass!2026" | chpasswd && \
    echo "admin-ops ALL=(ALL) NOPASSWD: /usr/bin/id, /bin/ls, /usr/bin/cat /etc/os-release" > /etc/sudoers.d/admin-ops && \
    chmod 440 /etc/sudoers.d/admin-ops

# Configure OpenSSH for enterprise security logging
RUN sed -i 's/#LogLevel INFO/LogLevel VERBOSE/' /etc/ssh/sshd_config && \
    sed -i 's/#SyslogFacility AUTH/SyslogFacility AUTH/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
