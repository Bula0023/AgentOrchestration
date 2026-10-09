Dev compose commands: docker compose -f docker-compose.dev.yml up --build 
 kubectl apply -f postgres-service.yml 
  kubectl apply -f postgres-deployment.yml     
  kubectl apply -f backend-deployment.yml
kubectl apply -f backend-service.yml
kubectl apply -f frontend-deployment.yml
kubectl apply -f frontend-service.yml
kubectl apply -f redis-deployment.yml
kubectl apply -f redis-service.yml

kubectl apply -f chroma-deployment.yml
kubectl apply -f chroma-service.yml

kubectl apply -f postgres-pvc.yml
kubectl apply -f postgres-statefulset.yml
kubectl apply -f postgres-service.yml
kubectl logs agent-backend-756766fd7c-hkz56 --previous