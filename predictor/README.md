# Ad-Category Prediction Module

This directory contains the ad category classification api to give categories
to new articles. Application runs on kubernetes cluster on GCE (Google Compute Engine)
for scalability.

## Create Kubernetes Cluster
+ `kubernetes/cluster/kube-up.sh`

## Instructions to Run on Kubernetes
+ `kubectl apply -f deployment.yaml`
+ `kubectl expose deployment ad-category-classifier-deployment --type=LoadBalancer --name=classifier-api`


## Delete Deployments
+ `kubectl delete deployment ad-category-classifier-deployment`
+ `kubectl delete service classifier-api`

## Tear Down Cluster
+ `kubernetes/cluster/kube-down.sh`
