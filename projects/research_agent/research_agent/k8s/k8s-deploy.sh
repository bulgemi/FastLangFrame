#!/bin/bash
K8S_NAME="research-agent"
echo "Deploying ${K8S_NAME} to Kubernetes..."
kubectl apply -f k8s/deployment.yaml
