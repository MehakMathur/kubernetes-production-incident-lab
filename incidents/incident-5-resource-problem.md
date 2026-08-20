 # Incident 5: Resource Problem (OOMKilled)

This one was interesting because I intentionally wanted to see what Kubernetes would do if I gave the application less memory than it actually needed.

Before changing the Deployment, I checked the current usage with:

`kubectl top pods`

Both pods were using around 21Mi of memory. I then set the memory limit to 16Mi, knowing it was lower than the current usage, and deployed the change.

Pretty quickly, the pods started restarting.

When I checked them with `kubectl get pods`, I could see `OOMKilled` and the restart count kept increasing.

I used `kubectl describe pod <pod-name>` to get more information and found:

`Reason: OOMKilled`  
`Exit Code: 137`

At this point the issue was pretty clear. I had told Kubernetes that the container could use a maximum of 16Mi of memory, while the Flask app itself was already using around 21Mi.

So every time the container started and crossed that limit, it was killed and Kubernetes tried to start it again.

What surprised me here was that this actually caused the application to become unavailable for a short time. In some of the earlier incidents, the old healthy pods stayed around while the new deployment was failing. Here, the new pods were able to start briefly before being killed, and eventually I ended up with no healthy pods.

To fix it, I changed the resources to:

`requests: 64Mi`  
`limits: 128Mi`

After redeploying, both pods stayed running. I checked `kubectl top pods` again and they were back around 21–22Mi.

The main thing I took away from this was that resource limits shouldn't just be numbers added to a YAML file because they look reasonable. I should first understand how much memory the application normally uses and then leave enough room for it to handle changes in usage.

I also now know that if I see `OOMKilled`, memory is one of the first places I should look. Exit code `137` tells me the process received a SIGKILL, and together with Kubernetes reporting `OOMKilled`, that's a strong sign that the container exceeded its memory limit.

This was also the first incident where I used `kubectl top`, so it helped me understand the difference between looking at what Kubernetes *configured* for a pod and looking at what the pod is *actually consuming*.


