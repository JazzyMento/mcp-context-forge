#!/usr/bin/env bash

# The script will stop if any commands fail, if undefined variables are used or if a command inside a pipeline fails
set -euo pipefail

CLUSTER_NAME="mcp-kind"
RELEASE_NAME="mcp-stack"
CHART_PATH="charts/mcp-stack"
VALUES_FILE="charts/mcp-stack/values-kind-test.yaml"

#Deletes any old Kind cluster called mcp-kind, if the cluster does not exist it will continue
echo "Deleting existing Kind cluster named ${CLUSTER_NAME} if it exists..."
kind delete cluster --name "${CLUSTER_NAME}" || true

#Creates a fresh Kubernetes cluster using Kind
echo "Creating Kind cluster named ${CLUSTER_NAME}..."
kind create cluster --name "${CLUSTER_NAME}"

#Installs the Helm chart into the newly created Kind cluster
echo "Installing Helm chart..."
  helm install "${RELEASE_NAME}" "${CHART_PATH}" \
  -f "${VALUES_FILE}" \
  --timeout 10m

#Helm will NOT finish installing until all pods are ready, the deployment has up to 5 minutes
echo "Waiting for pods to become ready..."
kubectl wait --for=condition=Ready pod \
  --all \
  --timeout=300s

#Runs Helm tests gateway-health-test, db-ready-test chart to prove the gateway health endpoint and Postgres service discovery work
echo "Running Helm tests..."
helm test "${RELEASE_NAME}" --logs

#Deletes the temp Kind cluster after the tests finish
echo "Deleting Kind cluster..."
kind delete cluster --name "${CLUSTER_NAME}"

#If everything in the script work, this message is printed
echo "Kind chart test completed successfully."
