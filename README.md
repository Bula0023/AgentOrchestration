Dev compose commands: docker compose -f docker-compose.dev.yml up --build 
 kubectl apply -f postgres-service.yml 
  kubectl apply -f postgres-deployment.yml     
  kubectl apply -f backend-deployment.yml
kubectl apply -f backend-service.yml
kubectl apply -f frontend-deployment.yml
kubectl apply -f frontend-service.yml
