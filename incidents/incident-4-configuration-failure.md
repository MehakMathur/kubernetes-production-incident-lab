# Incident 4: Configuration Failure (ConfigMap Key Mismatch)

**Incident:** New `incident-lab-app` pod stuck in `CreateContainerConfigError`.

**Impact:** No outage — old pods (from the previous, correctly-configured ReplicaSet) stayed `Running` throughout, same rolling-update protection seen in Incident 2. The deploy itself was blocked.

**Symptoms:**
- `kubectl get pods` showed the new pod stuck at `0/1`, status `ContainerCreating` → `CreateContainerConfigError`.
- Old pods, already running with the correct config, were unaffected.

**Investigation:**
1. `kubectl get pods` — spotted the stuck pod, a fourth distinct status pattern from the previous three incidents.
2. `kubectl describe pod <pod>` — `Events` showed the image had already pulled successfully (`already present on machine`), but:
   ```
   Warning  Failed  ...  Error: couldn't find key APP_MSG in ConfigMap default/incident-lab-config
   ```
   This fails even earlier in the pod lifecycle than Incident 2's `ImagePullBackOff` — the image is present, but the container spec itself can't be resolved, so no container is ever created (no logs possible, same as Incident 2, but for a different reason).

**Root Cause:**
The app's configuration was moved into a ConfigMap (`incident-lab-config`, key `APP_MESSAGE`) referenced by the Deployment via `env[].valueFrom.configMapKeyRef`. The Deployment was updated to reference the key as `APP_MSG` — a typo/rename that didn't match the actual key defined in the ConfigMap.

**Resolution:**
Corrected the `key:` field in the Deployment's `configMapKeyRef` back to `APP_MESSAGE`, matching the ConfigMap. Reapplied; the bad pod terminated, and `/` verified returning the ConfigMap-sourced message correctly.

**Preventive Action:**
- Keep ConfigMap keys and their references co-located or generated from the same source (e.g. Kustomize `configMapGenerator`) rather than hand-typed in two separate files, so a rename in one is forced to update the other.
- `CreateContainerConfigError` should be a known, documented pattern for on-call engineers: it means "check ConfigMap/Secret references," not "check the app code" — the app never even got a chance to run.
- A pre-deploy validation step (e.g. `kubectl apply --dry-run=server` or a CI check that cross-references ConfigMap keys against Deployment `configMapKeyRef` usage) would have caught this before it ever reached the cluster.
