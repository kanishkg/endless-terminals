FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    grep \
    gawk \
    sed \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /var/log/pods

RUN cat <<'EOF' > /var/log/pods/kube-system.log
2024-03-15T08:00:01Z kube-system/kube-scheduler-control-plane-1 Started
2024-03-15T08:00:05Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-15T08:01:12Z kube-system/kube-apiserver-control-plane-1 Started
2024-03-15T08:01:15Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-15T08:02:33Z kube-system/etcd-control-plane-1 Started
2024-03-15T08:02:36Z kube-system/etcd-control-plane-1 Running
2024-03-15T08:03:44Z kube-system/kube-controller-manager-control-plane-1 Started
2024-03-15T08:03:47Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-15T08:05:00Z kube-system/coredns-5dd5756b68-x7vzq Scheduled
2024-03-15T08:05:02Z kube-system/coredns-5dd5756b68-x7vzq Pulled
2024-03-15T08:05:10Z kube-system/coredns-5dd5756b68-x7vzq Started
2024-03-15T08:05:12Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-15T08:06:00Z kube-system/coredns-5dd5756b68-abc12 Scheduled
2024-03-15T08:06:02Z kube-system/coredns-5dd5756b68-abc12 Pulled
2024-03-15T08:06:10Z kube-system/coredns-5dd5756b68-abc12 Started
2024-03-15T08:06:12Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-15T08:07:00Z kube-system/kube-proxy-7h9xt Scheduled
2024-03-15T08:07:02Z kube-system/kube-proxy-7h9xt Pulled
2024-03-15T08:07:10Z kube-system/kube-proxy-7h9xt Started
2024-03-15T08:07:12Z kube-system/kube-proxy-7h9xt Running
2024-03-15T08:08:00Z kube-system/kube-proxy-node2-abc Scheduled
2024-03-15T08:08:02Z kube-system/kube-proxy-node2-abc Pulled
2024-03-15T08:08:10Z kube-system/kube-proxy-node2-abc Started
2024-03-15T08:08:12Z kube-system/kube-proxy-node2-abc Running
2024-03-15T08:10:00Z kube-system/metrics-server-6d94bc8694-2plwm Scheduled
2024-03-15T08:10:02Z kube-system/metrics-server-6d94bc8694-2plwm Pulled
2024-03-15T08:10:10Z kube-system/metrics-server-6d94bc8694-2plwm Started
2024-03-15T08:10:12Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-15T08:12:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Scheduled
2024-03-15T08:12:02Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Pulled
2024-03-15T08:12:10Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Started
2024-03-15T08:12:12Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-15T08:15:00Z kube-system/calico-node-xyz12 Scheduled
2024-03-15T08:15:02Z kube-system/calico-node-xyz12 Pulled
2024-03-15T08:15:10Z kube-system/calico-node-xyz12 Started
2024-03-15T08:15:12Z kube-system/calico-node-xyz12 Running
2024-03-15T08:20:00Z kube-system/calico-kube-controllers-abc123 Scheduled
2024-03-15T08:20:02Z kube-system/calico-kube-controllers-abc123 Pulled
2024-03-15T08:20:10Z kube-system/calico-kube-controllers-abc123 Started
2024-03-15T08:20:12Z kube-system/calico-kube-controllers-abc123 Running
2024-03-15T09:00:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-15T09:15:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-15T09:23:41Z kube-system/coredns-5dd5756b68-x7vzq OOMKilled
2024-03-15T09:23:45Z kube-system/coredns-5dd5756b68-x7vzq CrashLoopBackOff
2024-03-15T09:24:00Z kube-system/coredns-5dd5756b68-x7vzq Pulled
2024-03-15T09:24:10Z kube-system/coredns-5dd5756b68-x7vzq Started
2024-03-15T09:24:12Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-15T09:30:00Z kube-system/kube-proxy-7h9xt Running
2024-03-15T09:45:00Z kube-system/etcd-control-plane-1 Running
2024-03-15T10:00:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-15T10:15:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-15T10:30:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-15T10:45:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-15T11:00:00Z kube-system/calico-node-xyz12 Running
2024-03-15T11:15:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-15T11:30:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-15T11:45:02Z kube-system/metrics-server-6d94bc8694-2plwm OOMKilled
2024-03-15T11:45:10Z kube-system/metrics-server-6d94bc8694-2plwm CrashLoopBackOff
2024-03-15T11:46:00Z kube-system/metrics-server-6d94bc8694-2plwm Pulled
2024-03-15T11:46:10Z kube-system/metrics-server-6d94bc8694-2plwm Started
2024-03-15T11:46:12Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-15T12:00:00Z kube-system/kube-proxy-node2-abc Running
2024-03-15T12:30:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-15T13:00:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-15T13:30:00Z kube-system/kube-proxy-7h9xt Running
2024-03-15T14:00:00Z kube-system/etcd-control-plane-1 Running
2024-03-15T14:12:58Z kube-system/kube-proxy-7h9xt OOMKilled
2024-03-15T14:13:05Z kube-system/kube-proxy-7h9xt CrashLoopBackOff
2024-03-15T14:14:00Z kube-system/kube-proxy-7h9xt Pulled
2024-03-15T14:14:10Z kube-system/kube-proxy-7h9xt Started
2024-03-15T14:14:12Z kube-system/kube-proxy-7h9xt Running
2024-03-15T14:30:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-15T15:00:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-15T15:30:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-15T16:00:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-15T16:30:00Z kube-system/calico-node-xyz12 Running
2024-03-15T17:00:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-15T17:30:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-15T18:00:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-15T18:30:00Z kube-system/kube-proxy-node2-abc Running
2024-03-15T19:00:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-15T19:30:00Z kube-system/kube-proxy-7h9xt Running
2024-03-15T20:00:00Z kube-system/etcd-control-plane-1 Running
2024-03-15T20:30:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-15T21:00:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-15T21:30:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-15T22:00:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-15T22:30:00Z kube-system/calico-node-xyz12 Running
2024-03-15T23:00:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-15T23:30:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-16T00:00:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-16T00:30:00Z kube-system/kube-proxy-node2-abc Running
2024-03-16T01:00:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-16T01:30:00Z kube-system/kube-proxy-7h9xt Running
2024-03-16T02:00:00Z kube-system/etcd-control-plane-1 Running
2024-03-16T02:33:19Z kube-system/etcd-control-plane-1 OOMKilled
2024-03-16T02:33:25Z kube-system/etcd-control-plane-1 CrashLoopBackOff
2024-03-16T02:34:00Z kube-system/etcd-control-plane-1 Pulled
2024-03-16T02:34:10Z kube-system/etcd-control-plane-1 Started
2024-03-16T02:34:12Z kube-system/etcd-control-plane-1 Running
2024-03-16T03:00:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-16T03:30:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-16T04:00:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-16T04:30:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-16T05:00:00Z kube-system/calico-node-xyz12 Running
2024-03-16T05:30:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-16T06:00:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-16T06:30:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-16T07:00:00Z kube-system/kube-proxy-node2-abc Running
2024-03-16T07:30:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-16T08:00:00Z kube-system/kube-proxy-7h9xt Running
2024-03-16T08:17:44Z kube-system/coredns-5dd5756b68-x7vzq OOMKilled
2024-03-16T08:17:50Z kube-system/coredns-5dd5756b68-x7vzq CrashLoopBackOff
2024-03-16T08:18:00Z kube-system/coredns-5dd5756b68-x7vzq Pulled
2024-03-16T08:18:10Z kube-system/coredns-5dd5756b68-x7vzq Started
2024-03-16T08:18:12Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-16T08:30:00Z kube-system/etcd-control-plane-1 Running
2024-03-16T09:00:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-16T09:30:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-16T10:00:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-16T10:30:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-16T11:00:00Z kube-system/calico-node-xyz12 Running
2024-03-16T11:30:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-16T12:00:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-16T12:30:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-16T13:00:00Z kube-system/kube-proxy-node2-abc Running
2024-03-16T13:30:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-16T14:00:00Z kube-system/kube-proxy-7h9xt Running
2024-03-16T14:30:00Z kube-system/etcd-control-plane-1 Running
2024-03-16T15:00:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-16T15:30:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-16T16:00:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-16T16:30:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-16T17:00:00Z kube-system/calico-node-xyz12 Running
2024-03-16T17:30:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-16T18:00:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-16T18:30:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-16T19:00:00Z kube-system/kube-proxy-node2-abc Running
2024-03-16T19:30:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-16T20:00:00Z kube-system/kube-proxy-7h9xt Running
2024-03-16T20:30:00Z kube-system/etcd-control-plane-1 Running
2024-03-16T21:00:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-16T21:30:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-16T22:00:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-16T22:30:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-16T23:00:00Z kube-system/calico-node-xyz12 Running
2024-03-16T23:30:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-17T00:00:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-17T00:30:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-17T01:00:00Z kube-system/kube-proxy-node2-abc Running
2024-03-17T01:30:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-17T02:00:00Z kube-system/kube-proxy-7h9xt Running
2024-03-17T02:30:00Z kube-system/etcd-control-plane-1 Running
2024-03-17T03:00:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-17T03:30:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-17T04:00:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-17T04:30:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-17T05:00:00Z kube-system/calico-node-xyz12 Running
2024-03-17T05:30:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-17T06:00:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-17T06:30:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-17T07:00:00Z kube-system/kube-proxy-node2-abc Running
2024-03-17T07:30:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-17T08:00:00Z kube-system/kube-proxy-7h9xt Running
2024-03-17T08:30:00Z kube-system/etcd-control-plane-1 Running
2024-03-17T09:00:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-17T09:30:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-17T10:00:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-17T10:30:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-17T11:00:00Z kube-system/calico-node-xyz12 Running
2024-03-17T11:30:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-17T12:00:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-17T12:30:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-17T13:00:00Z kube-system/kube-proxy-node2-abc Running
2024-03-17T13:30:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-17T14:00:00Z kube-system/kube-proxy-7h9xt Running
2024-03-17T14:30:00Z kube-system/etcd-control-plane-1 Running
2024-03-17T15:00:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-17T15:30:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-17T16:00:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-17T16:30:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-17T16:41:03Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl OOMKilled
2024-03-17T16:41:10Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl CrashLoopBackOff
2024-03-17T16:42:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Pulled
2024-03-17T16:42:10Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Started
2024-03-17T16:42:12Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-17T17:00:00Z kube-system/calico-node-xyz12 Running
2024-03-17T17:30:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-17T18:00:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-17T18:30:00Z kube-system/kube-proxy-node2-abc Running
2024-03-17T19:00:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-17T19:30:00Z kube-system/kube-proxy-7h9xt Running
2024-03-17T20:00:00Z kube-system/etcd-control-plane-1 Running
2024-03-17T20:30:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-17T21:00:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-17T21:30:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-17T22:00:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-17T22:30:00Z kube-system/calico-node-xyz12 Running
2024-03-17T23:00:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-17T23:30:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-18T00:00:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-18T00:30:00Z kube-system/kube-proxy-node2-abc Running
2024-03-18T01:00:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-18T01:30:00Z kube-system/kube-proxy-7h9xt Running
2024-03-18T02:00:00Z kube-system/etcd-control-plane-1 Running
2024-03-18T02:30:00Z kube-system/kube-scheduler-control-plane-1 Running
2024-03-18T03:00:00Z kube-system/kube-apiserver-control-plane-1 Running
2024-03-18T03:30:00Z kube-system/kube-controller-manager-control-plane-1 Running
2024-03-18T03:55:27Z kube-system/metrics-server-6d94bc8694-2plwm OOMKilled
2024-03-18T03:55:35Z kube-system/metrics-server-6d94bc8694-2plwm CrashLoopBackOff
2024-03-18T03:56:00Z kube-system/metrics-server-6d94bc8694-2plwm Pulled
2024-03-18T03:56:10Z kube-system/metrics-server-6d94bc8694-2plwm Started
2024-03-18T03:56:12Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-18T04:00:00Z kube-system/coredns-5dd5756b68-abc12 Running
2024-03-18T04:30:00Z kube-system/calico-node-xyz12 Running
2024-03-18T05:00:00Z kube-system/calico-kube-controllers-abc123 Running
2024-03-18T05:30:00Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl Running
2024-03-18T06:00:00Z kube-system/metrics-server-6d94bc8694-2plwm Running
2024-03-18T06:30:00Z kube-system/kube-proxy-node2-abc Running
2024-03-18T07:00:00Z kube-system/coredns-5dd5756b68-x7vzq Running
2024-03-18T07:30:00Z kube-system/kube-proxy-7h9xt Running
2024-03-18T08:00:00Z kube-system/etcd-control-plane-1 Running
EOF

RUN chmod 644 /var/log/pods/kube-system.log

WORKDIR /home/user

CMD ["/bin/bash"]
