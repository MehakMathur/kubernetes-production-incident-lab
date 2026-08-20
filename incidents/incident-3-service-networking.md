# Incident 3: Service Networking Failure

For this incident, my pods were running normally, but I couldn't access the application through the Kubernetes Service.

When I checked:

`kubectl get pods`

both pods showed `1/1 Running` with 0 restarts.

At first this was a little confusing because everything looked healthy, but the application was still unreachable.

## Troubleshooting

Since the pods were running, I first checked their labels:

`kubectl get pods --show-labels`

The pods had:

`app=incident-lab-app`

Then I checked the Service:

`kubectl describe svc incident-lab-app`

I noticed that the Service was looking for:

`app=incident-lab-app-frontend`

But my pods were labeled:

`app=incident-lab-app`

So the Service wasn't actually finding any pods to send traffic to.

I also noticed that the `Endpoints` section was empty.

To confirm this, I ran:

`kubectl get endpoints incident-lab-app`

and it showed `<none>`.

This helped me understand how a Kubernetes Service actually finds pods. The Service doesn't automatically know which pods belong to it. It uses its **selector** to find pods with matching **labels**.

In my case:

Service was looking for:

`app=incident-lab-app-frontend`

Pods had:

`app=incident-lab-app`

Since they didn't match, the Service had no endpoints and therefore nowhere to send the incoming traffic.

## Fix

I changed the Service selector to:

`app: incident-lab-app`

and applied the configuration again.

After that, I checked the endpoints and could see the IP addresses of both pods.

I tried accessing the application again and it worked.

## What I learned

The biggest thing I learned here is that a pod being `Running` doesn't automatically mean the application is reachable.

The pods can be completely healthy while the Service configuration is broken.

I also understood the relationship between:

**Pod Labels → Service Selector → Endpoints → Traffic reaches Pods**

If the Service selector doesn't match the pod labels, Kubernetes won't add those pods as endpoints and the Service has nowhere to send traffic.

So if I see healthy pods but the application still isn't reachable, one of the first things I would check now is:

`kubectl get endpoints <service-name>`

If there are no endpoints, I would check whether the Service selector matches the pod labels.
