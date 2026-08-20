# Incident 5: Resource Problem (OOMKilled)

**Incident:** `incident-lab-app` pods repeatedly `OOMKilled` after resource limits were added to the Deployment.

**Impact:** Full outage. Unlike Incidents 2 and 4, the rolling update proceeded past both replicas before the new pods' failures were caught, because kubelet briefly reports a container as started before the OOM kill lands — leaving zero healthy pods for a period.

**Symptoms:**
- `kubectl get pods` showed new pods cycling `Running` → `OOMKilled`, restart count climbing.
- Old, previously-healthy pods were terminated as part of the rollout despite the new pods never stabilizing.

**Investigation:**
1. Before making the change, `kubectl top pods` showed actual usage of **~21Mi** per pod — this measurement is what exposed the mistake before/after.
2. `kubectl get pods` — showed `STATUS: OOMKilled` directly, a distinct and explicit status (unlike Incident 1's generic `Error`).
3. `kubectl describe pod <pod>` — confirmed:
   ```
   State:       Terminated
     Reason:    OOMKilled
     Exit Code: 137
   ```
   Exit code `137` = `128 + 9` (SIGKILL) — the kernel's OOM killer terminating the process outright, not the application exiting on its own (contrast with Incident 1's `Exit Code: 1`, a normal application-level failure).

**Root Cause:**
The Deployment was given a memory `limit` of `16Mi`, set without checking actual usage. Measured real usage (~21Mi) already exceeded this limit, so every container was killed by the kernel almost immediately after starting, regardless of load.

**Resolution:**
Set `requests.memory: 64Mi` / `limits.memory: 128Mi` (and matching modest CPU values) based on the actual measured footprint plus headroom. Reapplied; both pods stable at `Running`, `RESTARTS: 0`; `kubectl top pods` confirmed real usage (~21-22Mi) comfortably inside the new limit; `/health` verified reachable.

**Preventive Action:**
- Never set resource `limits` from a guess — measure actual usage with `kubectl top pods` (or a load test under realistic traffic) before setting them, and revisit after any code/dependency change that could shift memory footprint.
- Memory limits should include meaningful headroom above steady-state usage (this fix used roughly 6x measured usage for the limit) to absorb spikes without killing the process outright.
- `OOMKilled` + `Exit Code: 137` should be an instant, unambiguous signal for on-call engineers to check `resources.limits.memory` first — it's a different failure class from a code-level crash (Incident 1) and doesn't need a code-level fix.
