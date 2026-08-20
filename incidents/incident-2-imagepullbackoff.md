# Incident 2: ImagePullBackOff

**Incident:** A new pod got stuck at `0/1` after I updated the Deployment to point at `incident-lab-app:v3`.

**Impact:** Honestly, less bad than it looked at first. The two existing v2 pods stayed `Running` the whole time - the rollout just never finished, it didn't take anything down. That's the rolling update default doing its job: it won't kill old pods until new ones are actually ready.

**Symptoms:**
`kubectl get pods` showed the new pod sitting at `0/1`, status `ErrImagePull`, which after a bit turned into `ImagePullBackOff`. Restart count stayed at 0 the whole time, which is a difference from incident 1 - there's no container running yet to restart.

**Investigation:**
My first instinct was to check the logs, same as last time:

```
kubectl logs <pod>
```

That didn't work - "no container found" or similar. Makes sense once I thought about it: if the image can't even be pulled, there's no container, so there's nothing to log. That absence is itself a clue - if `kubectl logs` gives you nothing, stop thinking about the app code and look at the image/scheduling side instead.

`kubectl describe pod` had the real answer in the Events section:

```
Failed to pull image "incident-lab-app:v3": failed to resolve reference
"docker.io/library/incident-lab-app:v3": pull access denied, repository
does not exist or may require authorization
```

**Root Cause:**
`v3` was never actually built or loaded into the kind cluster - I bumped the tag in the manifest without building/loading the image first. Since this image only exists locally (not on Docker Hub), every pull attempt failed the same way.

**Resolution:**
Reverted the image tag back to `v2`, which was already loaded. Reapplied, rollout finished, bad pod got cleaned up, `/health` came back.

**Preventive Action:**
Build (or `kind load`) has to happen before the manifest ever references the new tag - not after, not "at the same time." I'd also want rollout status checked automatically as part of any deploy step (`kubectl rollout status`) so a stuck rollout like this gets flagged instead of just sitting there quietly. One thing worth remembering for on-call triage specifically: check what's still `Running` before assuming a failing pod means an outage - in this case it didn't.
