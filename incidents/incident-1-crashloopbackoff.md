# Incident 1: CrashLoopBackOff

**Incident:** After rolling out v2 of the app, both pods went into `CrashLoopBackOff` and never recovered.

**Impact:** Complete outage. Neither `/` nor `/health` was reachable through the Service.

**Symptoms:**
`kubectl get pods` showed restart counts climbing every few seconds - 1, then 2, then 3 - with status flipping between `Error` and `CrashLoopBackOff`.
The old v1 pods were being terminated as part of the rollout, so there was no fallback once the new ones started failing.

**Investigation:**

First thing I checked was `kubectl get pods`, just to see how bad it was. Restarts were climbing fast, which told me the container was starting and then dying almost immediately, not hanging or timing out.

From there I ran `kubectl describe pod` on one of the failing pods. Two things jumped out - `Exit Code: 1` (so this wasn't an OOM kill, which shows as 137) and the `Environment` section only listed `APP_MESSAGE`. No `REQUIRED_CONFIG` anywhere, even though I could see in the app code that it should be there. The `Events` section at the bottom also had a `BackOff` warning, which is literally the thing generating the `CrashLoopBackOff` status.

That was a strong enough hint, but I didn't want to guess, so I pulled the actual logs:

```
kubectl logs <pod>
```

```
Traceback (most recent call last):
  File "/app/app.py", line 9, in <module>
    REQUIRED_CONFIG = os.environ["REQUIRED_CONFIG"]
KeyError: 'REQUIRED_CONFIG'
```

That confirmed it.

**Root Cause:**
v2 of the app added a hard requirement on a `REQUIRED_CONFIG` environment variable - no default, so `os.environ["REQUIRED_CONFIG"]` throws if it's missing. The Deployment manifest was never updated to actually set it when I bumped the image tag. Since this line runs at import time, the crash happens before Flask even boots.

**Resolution:**
Added `REQUIRED_CONFIG` to the Deployment's `env:` block and reapplied. Rollout went through cleanly, both pods came up `Running` with `RESTARTS: 0`, and `/health` responded again.

**Preventive Action:**
The actual mistake here wasn't the missing env var, it was shipping a code change that required new config without updating the deployment in the same step. In a real pipeline I'd want this caught by CI before it ever reaches a cluster - something that fails the build if the app declares a required env var the manifest doesn't set. I'd also rather see this fail with a clear log line like `missing required config: REQUIRED_CONFIG` than a raw Python traceback, since that's a lot faster to read at 2am.
