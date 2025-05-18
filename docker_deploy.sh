# read .env file
ENV_FILE=.env_prod
export $(grep -v '^#' $ENV_FILE | xargs -0)

deploy_command="cd ~/$APP_NAME && docker pull kuznetsov1024/$APP_NAME:latest && ./docker_run.sh"

./docker_build.sh && \
    echo "" && \
    ./docker_push.sh && \
    echo "INFO: docker image pushed succesfully!" && echo "" && \
    ssh -i $DEPLOY_SSH_KEY_FILE $DEPLOY_HOST_USER@$DEPLOY_HOST "mkdir -p ~/$APP_NAME/data" && \
    ssh -i $DEPLOY_SSH_KEY_FILE $DEPLOY_HOST_USER@$DEPLOY_HOST "mkdir -p ~/$APP_NAME/received_audio" && \
    ssh -i $DEPLOY_SSH_KEY_FILE $DEPLOY_HOST_USER@$DEPLOY_HOST "mkdir -p ~/$APP_NAME/transcribed_text" && \
    scp -i $DEPLOY_SSH_KEY_FILE $ENV_FILE $DEPLOY_HOST_USER@$DEPLOY_HOST:~/$APP_NAME/.env && \
    scp -i $DEPLOY_SSH_KEY_FILE docker_run.sh $DEPLOY_HOST_USER@$DEPLOY_HOST:~/$APP_NAME/docker_run.sh && \
    ssh -i $DEPLOY_SSH_KEY_FILE $DEPLOY_HOST_USER@$DEPLOY_HOST $deploy_command
