#!/bin/bash
NAME="russian-ira-ads"
PROJECT=$(gcloud config get-value project)
IMAGE="gcr.io/$PROJECT/$NAME"

gcloud builds submit --tag $IMAGE
gcloud run deploy --allow-unauthenticated --platform=managed --image $IMAGE $NAME
