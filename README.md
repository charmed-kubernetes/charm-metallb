# MetalLB charm

This charm enables the MetalLB load balancer on Charmed Kubernetes.

## How to test

Clone this repo:

```bash
git clone https://github.com/charmed-kubernetes/charm-metallb.git
cd charm-metallb
git submodule init
git submodule update
```

Deploy Charmed Kubernetes:

```bash
juju deploy cs:charmed-kubernetes
```

Add k8s to a Juju controller:

```bash
juju scp kubernetes-master/0:config ~/.kube/config
juju add-k8s myk8scloud --controller <controller-name>
```

Create a k8s model:

```bash
juju add-model myk8smodel myk8scloud
```

Deploy metalLB:

```bash
# TBD: Deploy the production version from charm store

# Deploy a local version, useful for development
juju deploy . \
  --resource controller-image=metallb/controller:v0.8.2 \
  --resource speaker-image=metallb/speaker:v0.8.2
```
