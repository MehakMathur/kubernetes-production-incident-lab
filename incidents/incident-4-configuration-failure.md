# Incident 4: Configuration Failure (ConfigMap Key Mismatch)

**Incident:** New pod stuck in `CreateContainerConfigError` after I moved `APP_MESSAGE` from a hardcoded value into a ConfigMap and then (deliberately) typo'd the key reference.

**Impact:** No real outage - same as incident 2, the old pods kept running since the new one never came up. The deploy was just stuck.

**Symptoms:**
New pod sat at `0/1`, went `ContainerCreating` then `CreateContainerConfigError`. Old pods untouched.

**Investigation:**
`kubectl describe pod` again had the answer, and it's worth noting this fails at a different point than incident 2 - the image had already pulled fine (`already present on machine`), but the container still couldn't be created:

```
Error: couldn't find key APP_MSG in ConfigMap default/incident-lab-config
```

I'd referenced the key as `APP_MSG` in the Deployment's `configMapKeyRef`, but the actual key in the ConfigMap was `APP_MESSAGE`. Small typo, same failure class as incident 3 in spirit - two files that are supposed to agree on a name, and don't.

**Root Cause:**
Key name mismatch between the ConfigMap (`APP_MESSAGE`) and the Deployment's reference to it (`APP_MSG`).

**Resolution:**
Fixed the key name in the Deployment, reapplied. Bad pod terminated on its own, and the response confirmed the ConfigMap value was actually being read (`"Hello from a ConfigMap!"`).

**Preventive Action:**
Generating the ConfigMap and its references from a single source (Kustomize's `configMapGenerator`, for example) instead of hand-typing the key name in two places would remove this failure mode entirely. Also good to just know as a pattern: `CreateContainerConfigError` almost always means "go check ConfigMap/Secret references," not "go read the app code" - the app never got the chance to run at all here.
