#!/bin/bash
PROJECT_NAME="research_agent"
IMAGE_NAME="${PROJECT_NAME}:latest"
echo "Building Docker image: ${IMAGE_NAME}..."
docker build -t ${IMAGE_NAME} -f docker/Dockerfile ../../..
