# Incident 2: ImagePullBackOff

**Incident:** New `incident-lab-app` pod stuck in `ImagePullBackOff` after a Deployment update.

**Impact:** No user-facing outage — the Deployment's rolling-update strategy kept both existing `v2` pods `Running` and never terminated them, since the new pod never became ready. The blast radius was "deploy stuck," not "app down."

**Symptoms:**
- `kubectl get pods` showed a new pod stuck at `0/1`, status `ErrImagePull` transitioning to `ImagePullBackOff`.
- Restart count stayed at `0` (the container was never able to start, so it never had the chance to crash/restart).
- Old pods remained `Running` and unaffected throughout.

**Investigation:**
1. `kubectl get pods` — spotted the new pod stuck at `0/1`, distinct pattern from Incident 1 (no restarts climbing, since there's no container to restart yet).
2. `kubectl logs <pod>` was not useful here — no container ever started, so there were no application logs to read. This absence is itself a diagnostic signal: no logs + image-related pod state → look at pull events, not app code.
3. `kubectl describe pod <pod>` — the `Events` section had the full story:
   ```
   Failed to pull image "incident-lab-app:v3": failed to pull and unpack image
   "docker.io/library/incident-lab-app:v3": failed to resolve reference
   "docker.io/library/incident-lab-app:v3": pull access denied, repository does
   not exist or may require authorization
   ```

**Root Cause:**
The Deployment manifest was updated to reference `incident-lab-app:v3`, an image tag that was never built or loaded into the cluster. Since this image only exists locally/in-cluster (not on a public registry), the pull failed identically on every retry, and Kubernetes backed off retrying — `ImagePullBackOff`.

**Resolution:**
Reverted the Deployment's image reference to `incident-lab-app:v2`, which was already built and loaded into the kind cluster. Reapplied; rollout completed, bad pod terminated, both replicas `Running`, `/health` verified reachable.

**Preventive Action:**
- CI/CD pipelines should build and push (or `kind load`) an image *before* updating the manifest that references it — never update the tag speculatively.
- A deploy pipeline should gate on rollout success (`kubectl rollout status`) and auto-rollback on failure, rather than leaving a broken ReplicaSet stuck indefinitely.
- Worth noting for on-call triage: an `ImagePullBackOff` on a *new* rollout with old pods still healthy is a "stuck deploy," not necessarily a live incident — impact assessment should check `kubectl get pods` for what's still `Running`, not just alert on the failing pod's state.
