About this project
------------------
This project is a containerized version of [Flask Catalog](https://github.com/nivanko/flask-catalog), other project
written for Udacity Full Stack Nanodegree.  
Application can be run on any existing Kubernetes cluster, but provided CI/CD configuration uses AWS for this purpose.

Prerequisites
-------------
Existing [AWS](https://aws.amazon.com/) account with permissions to run EKS cluster.  
Existing [CircleCI](https://circleci.com/) account for correct testing and deployment.

Usage
-----
For the CI/CD pipeline to work correctly, the following environment variables must be set:  
- AWS_ACCESS_KEY_ID
- AWS_CLUSTER_NAME (name for EKS cluster, any string)
- AWS_DEFAULT_REGION
- AWS_SECRET_ACCESS_KEY
- AWS_SSH_KEY (existing AWS key pair)
- DOCKER_HUB_PASSWORD
- DOCKER_HUB_USERNAME