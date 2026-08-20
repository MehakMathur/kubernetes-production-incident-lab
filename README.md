# Kubernetes Production Incident Lab

A hands-on project for learning how a Cloud Native Support Engineer investigates and resolves Kubernetes incidents — CrashLoopBackOff, ImagePullBackOff, networking failures, misconfiguration, and resource exhaustion — using a real Flask app deployed on a local Kubernetes cluster.

Each incident follows: **Observe → Gather evidence → Form hypothesis → Test → Find root cause → Fix → Verify → Document**.

## Structure

- `app/` — the Flask application and Dockerfile
- `kubernetes/` — Deployment/Service manifests
- `incidents/` — one markdown write-up per incident, with a full RCA
- `scripts/` — helper scripts

## Stack

Docker, kind (local Kubernetes), kubectl, Python/Flask — entirely free and local.
