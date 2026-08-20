# Incident 5: Resource Problem (OOMKilled)

**Incident:** Both pods stuck in a kill loop after I added resource limits to the Deployment for the first time.

**Impact:** This was the only one of the five that turned into a genuine full outage. Both old pods got rotated out even though the new ones never stabilized - I didn't expect that at first, since incidents 2 and 4 both left the old pods alone. The difference is that these pods did briefly report `Running` before getting killed, which was apparently enough for the rollout to treat them as "started" and move on to retiring the old ones.

**Symptoms:**
`kubectl get pods` showed `OOMKilled` directly as the status, restarts climbing, and - unlike the earlier incidents - zero healthy pods at one point.

**Investigation:**
Before I even added the limits, I ran `kubectl top pods` out of curiosity (this needed metrics-server installed first, since kind doesn't ship it by default - that itself is worth remembering, `kubectl top` silently does nothing without it). Actual usage was sitting around 21Mi per pod.

I set the memory limit to 16Mi. In hindsight, obviously too low given what I'd just measured, but I wanted to see what actually happens rather than just read about it.

`kubectl describe pod` confirmed exactly what I expected:

```
State:       Terminated
  Reason:    OOMKilled
  Exit Code: 137
```

137 is 128 + 9 (SIGKILL) - the kernel's OOM killer, not the app failing on its own. Different animal entirely from incident 1's `Exit Code: 1`.

**Root Cause:**
Memory limit (16Mi) set lower than the app's actual measured usage (~21Mi), guaranteeing an OOM kill on every single startup.

**Resolution:**
Bumped it to `requests: 64Mi` / `limits: 128Mi`, based on the number I'd actually measured plus real headroom. Reapplied - both pods came up clean, `kubectl top pods` showed ~21-22Mi again, comfortably under the new limit this time.

**Preventive Action:**
Don't set memory limits from a guess - measure first with `kubectl top` (or under actual load) and leave real headroom above it, then revisit any time the app or its dependencies change. And as a triage shortcut: `OOMKilled` + exit code `137` should point straight at `resources.limits.memory`, not at the code - it's a completely different category of bug from a crash.
