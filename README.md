# Kubernetes Production Incident Lab

I built this project to get hands-on experience with Kubernetes troubleshooting and understand how real production issues are investigated.

The project uses a simple Flask application running on a local Kubernetes cluster. Instead of only deploying the application, I intentionally create different problems and work through how to find and fix them.

Some of the issues I’ll be working with include:
- CrashLoopBackOff
- ImagePullBackOff
- Kubernetes Service/networking issues
- Configuration errors
- CPU and memory issues

For each issue, I’ll document what went wrong, the commands I used while troubleshooting, what caused the problem, and how I fixed it.

## Project Structure

- `app/` - Flask application
- `kubernetes/` - Kubernetes deployment and service files
- `incidents/` - notes and RCA for each issue
- `scripts/` - helper scripts used during the project

## Tools

Docker, Kubernetes (kind), kubectl, Python, and Flask.

Everything runs locally, so the project doesn't require any cloud resources.
