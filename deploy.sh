#!/bin/bash
set -e

IMAGE="rberry364/euchre-api"
CONTAINER="euchre-api"

echo "Building Docker image..."
docker build -t "$IMAGE" .

echo "Pushing to Docker Hub..."
docker push "$IMAGE"

echo "Done! Image pushed to $IMAGE"
echo ""
echo "To deploy on your Oracle VM, run:"
echo "  sudo docker pull $IMAGE"
echo "  sudo docker stop $CONTAINER 2>/dev/null; sudo docker rm $CONTAINER 2>/dev/null"
echo "  sudo docker run -d --restart always -p 8080:8080 --name $CONTAINER $IMAGE"
