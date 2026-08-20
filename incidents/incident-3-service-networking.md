# Incident 3: Service Networking Failure

**Incident:** App became unreachable through the Service - connection refused on every request.

**Impact:** Full outage from a client's point of view, even though both pods were completely healthy.

This one was a good reminder that "the pods are fine" and "the app is reachable" are not the same statement.

**Symptoms:**
`kubectl get pods` looked totally normal - both `1/1 Running`, 0 restarts. But trying to hit the Service through `kubectl port-forward` just got connection refused immediately, not a timeout.

**Investigation:**
Since the pods themselves looked fine, I checked `kubectl get pods --show-labels` first, just to rule that out. Pods had `app=incident-lab-app`, as expected.

Then `kubectl describe svc incident-lab-app`:

```
Selector: app=incident-lab-app-frontend
Endpoints:
```

There it was - the selector said `incident-lab-app-frontend`, not `incident-lab-app`. And `Endpoints` was blank. A Service doesn't know about pods directly; it just continuously matches its selector against pod labels and keeps a live list of matching pod IPs (the Endpoints). Zero matches means zero endpoints, and zero endpoints means the Service has genuinely nothing to send traffic to - it's not that it's misrouting, it's that there's no route at all.

`kubectl get endpoints incident-lab-app` confirmed it directly: `<none>`.

**Root Cause:**
Selector/label mismatch between the Service and the Deployment's pod template. Simple typo-class bug, but it fully breaks routing regardless of how healthy the pods are.

**Resolution:**
Fixed the selector to match the actual pod label (`app: incident-lab-app`) and reapplied. `kubectl get endpoints` immediately picked up both pod IPs on port 5000, and the app was reachable again.

**Preventive Action:**
The selector and the pod template labels should really come from one shared value instead of being typed out twice in two different files - that's exactly how this kind of drift happens. Also making a mental note: `kubectl get endpoints` should be one of the first things I check whenever "pods are healthy but the service isn't reachable" comes up, since it isolates a networking/selector problem from an app problem in a single command.
