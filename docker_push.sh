# read .env file
export $(grep -v '^#' .env | xargs -0)

docker tag $APP_NAME kuznetsov1024/$APP_NAME
docker push kuznetsov1024/$APP_NAME