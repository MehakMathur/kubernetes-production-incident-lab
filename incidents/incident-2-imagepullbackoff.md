# Incident 2: ImagePullBackOff

For this incident, I changed the image version in my Kubernetes Deployment from `v2` to `v3`.

After applying the change, I ran:

`kubectl get pods`

and noticed that the new pod was stuck at `0/1`. At first it showed `ErrImagePull`, and after some time it changed to `ImagePullBackOff`.

One thing I noticed was that my old v2 pods were still running, so the application was actually still available. Kubernetes was trying to start the new version before removing the existing working pods.

## Troubleshooting

My first thought was to check the logs:

`kubectl logs <pod-name>`

But there weren't really any logs to check.

This helped me understand something important — the container never actually started. Kubernetes couldn't get the Docker image in the first place, so there was no running container generating application logs.

I then checked:

`kubectl describe pod <pod-name>`

The Events section showed that Kubernetes was failing to pull:

`incident-lab-app:v3`

That's when I realized what I had done. I updated the Deployment to use `v3`, but I had never actually built that image or loaded it into my kind cluster.

## Fix

I changed the image back to `incident-lab-app:v2`, which was already available in the cluster, and applied the Deployment again.

After that, the rollout completed successfully and the pods were running normally.

## What I learned

The main thing I understood from this incident is the difference between `CrashLoopBackOff` and `ImagePullBackOff`.

With `CrashLoopBackOff`, the container is able to start, but something causes it to crash and Kubernetes keeps restarting it.

With `ImagePullBackOff`, Kubernetes can't even get the image needed to create the container, so the container never starts.

I also learned not to jump straight to application logs every time something goes wrong. The pod status and the Events section from `kubectl describe` can tell me which stage is actually failing.

And before updating a Deployment with a new image tag, I need to make sure that image actually exists and is available to the cluster.
