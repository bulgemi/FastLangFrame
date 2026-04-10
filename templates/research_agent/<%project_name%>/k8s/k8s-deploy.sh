#!/bin/bash
K8S_NAME="<%k8s_name%>"
echo "Deploying ${K8S_NAME} to Kubernetes..."
kubectl apply -f k8s/deployment.yaml
