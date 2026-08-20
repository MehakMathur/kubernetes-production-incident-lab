# Incident 3: Service Networking Failure (Selector/Label Mismatch)

**Incident:** `incident-lab-app` Service unreachable — connection refused on every request.

**Impact:** Full outage of the app from the client's perspective, despite both application pods being perfectly healthy and `Running`.

**Symptoms:**
- `kubectl get pods` showed both pods `1/1 Running`, `RESTARTS: 0` — nothing wrong at the pod level.
- Requests to the Service (via `kubectl port-forward svc/incident-lab-app`) failed with "connection refused."
- `kubectl get endpoints incident-lab-app` showed `ENDPOINTS: <none>`.

**Investigation:**
1. `kubectl get pods` — ruled out a pod-level problem immediately; both pods healthy.
2. `kubectl get pods --show-labels` — confirmed pods carry `app=incident-lab-app`.
3. `kubectl describe svc incident-lab-app` — showed `Selector: app=incident-lab-app-frontend` and a blank `Endpoints:` field.
4. `kubectl get endpoints incident-lab-app` — confirmed zero endpoints, meaning the Service had no pods it considered valid backends.

**Root Cause:**
The Service's `selector` (`app: incident-lab-app-frontend`) did not match the label actually applied to the pods by the Deployment (`app: incident-lab-app`). A Service computes its Endpoints purely from this label match — with zero matching pods, it has zero endpoints, and every connection to it fails, regardless of pod health.

**Resolution:**
Corrected the Service's `selector` back to `app: incident-lab-app` to match the Deployment's pod template labels. Reapplied; `kubectl get endpoints` immediately showed both pod IPs (`:5000`); `/health` verified reachable again through the Service.

**Preventive Action:**
- Keep the Service's `selector` and the Deployment's `template.metadata.labels` defined from a single shared value (e.g. a Kustomize/Helm variable) rather than duplicated literal strings in two files, so they can't silently drift apart.
- `kubectl get endpoints <service>` (or `kubectl get endpointslice`) should be a standard first check for "service unreachable but pods look fine" — it isolates label/selector issues from pod-level or app-level ones in a single command.
- Consider validating in CI that every Service's `selector` matches at least one Deployment's pod template labels in the same manifest set.
