# Kubernetes Networking Configuration for Cauldron

This directory contains Kubernetes networking configurations for the Cauldron platform, including CNI (Container Network Interface) setup and network policies.

## CNI Configuration

Cauldron uses [Calico](https://www.tigera.io/project-calico/) as the CNI provider. Calico provides a full networking stack with support for network policies, BGP routing, and advanced security features.

### Files

- `calico-operator.yaml`: Deploys the Calico operator that manages the Calico components
- `calico-installation.yaml`: Configures Calico networking settings

### Key Features Enabled

- VXLAN Cross-Subnet encapsulation
- BPF dataplane for improved performance
- Prometheus metrics
- Wireguard encryption for pod-to-pod traffic
- Resource requests and limits for Calico components

## Network Policies

Cauldron follows a zero-trust networking model where all traffic is denied by default and only explicitly allowed traffic can flow between services.

### Default Deny Policy

`default-deny.yaml` implements a default deny policy for all pods in the cauldron namespace.

### Service-Specific Policies

Each service has its own network policy file:

- `aethercore-policy.yaml`: Controls traffic to/from the AetherCore service
- `manifold-ui-policy.yaml`: Controls traffic to/from the Manifold UI
- `postgres-policy.yaml`: Controls traffic to/from PostgreSQL
- `prometheus-policy.yaml`: Controls traffic to/from Prometheus monitoring
- `qdrant-policy.yaml`: Controls traffic to/from the Qdrant vector database
- `rabbitmq-policy.yaml`: Controls traffic to/from RabbitMQ
- `traefik-policy.yaml`: Controls traffic to/from the Traefik ingress controller

### Template

`template-policy.yaml` provides a starting point for creating network policies for new services.

## Applying the Configuration

1. First, apply the Calico CNI configuration:
   ```
   kubectl apply -f cni/calico-operator.yaml
   kubectl wait --for=condition=available --timeout=60s deployment/tigera-operator -n tigera-operator
   kubectl apply -f cni/calico-installation.yaml
   ```

2. Wait for Calico to be ready:
   ```
   kubectl -n calico-system wait --for=condition=available --timeout=90s deployment/calico-kube-controllers
   ```

3. Apply the network policies:
   ```
   kubectl apply -f network-policies/default-deny.yaml
   kubectl apply -f network-policies/
   ```

## Tips for Network Policy Management

1. **Testing**: Before applying a new policy, you can validate it with:
   ```
   kubectl apply -f your-policy.yaml --dry-run=client
   ```

2. **Troubleshooting Connectivity**:
   - Check if policies are applied: `kubectl get networkpolicies -n cauldron`
   - Debug traffic: `kubectl exec -it <pod-name> -- wget -O- <service-url>` to test connectivity
   - Use Calico debug tools: `calicoctl get networkpolicy`

3. **Viewing Effective Policies**:
   ```
   kubectl get networkpolicies -n cauldron
   ```

4. **Adding New Services**:
   - Copy `template-policy.yaml` and modify it for your new service
   - Define both ingress and egress rules as needed
   - Always include DNS resolution egress rules