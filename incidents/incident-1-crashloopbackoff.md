# Incident 1: CrashLoopBackOff

**Incident:** `incident-lab-app` pods stuck in `CrashLoopBackOff` after deploying `v2`.

**Impact:** All replicas down. `/health` and `/` unreachable through the Service — full outage of the app.

**Symptoms:**
- `kubectl get pods` showed `READY 0/1`, `STATUS Error`, restart count climbing rapidly.
- Old (`v1`) pods terminating while new (`v2`) pods repeatedly crashed on startup.

**Investigation:**
1. `kubectl get pods` — confirmed restarts climbing on the new ReplicaSet's pods, first sign of a crash loop.
2. `kubectl describe pod <pod>` —
   - `Exit Code: 1` (a clean application-level failure, not `137`/OOMKilled).
   - `Environment:` block only listed `APP_MESSAGE` — `REQUIRED_CONFIG` was missing.
   - `Events` showed `Warning  BackOff  ...  Back-off restarting failed container` — the mechanism behind `CrashLoopBackOff`.
3. `kubectl logs <pod>` — showed the actual Python traceback:
   ```
   KeyError: 'REQUIRED_CONFIG'
   ```
   at `app.py:9`, raised at import time, before Flask starts.

**Root Cause:**
`v2` of the app added a hard requirement on a `REQUIRED_CONFIG` environment variable (`os.environ["REQUIRED_CONFIG"]`, no default). The Kubernetes Deployment manifest was not updated to set this variable when the image was bumped to `v2`, so every container exited immediately on startup with `KeyError`, triggering Kubernetes' crash-loop backoff.

**Resolution:**
Added `REQUIRED_CONFIG` to the Deployment's `env:` block and re-applied. Rollout succeeded; pods reached `Running` with `RESTARTS: 0`; `/health` verified reachable through the Service.

**Preventive Action:**
- Application code changes that add new required configuration should ship in the same change/PR as the corresponding manifest update, and ideally be caught in CI (e.g. a check that diffs required env vars in code against what the Deployment sets).
- Prefer failing config validation with a clear startup log message over an unhandled `KeyError`, so `kubectl logs` immediately shows "missing config X" instead of a raw traceback.
- Consider a readiness probe on `/health` so Kubernetes (and dashboards) reflect "not ready" distinctly from "crashing," giving faster signal separation between config errors and slow-starting-but-healthy pods.
