# read .env file
export $(grep -v '^#' .env | xargs -0)

image_name=kuznetsov1024/${APP_NAME}:latest
container_name=${APP_NAME}_container
mount_source=~/${APP_NAME}/data
mount_target=/data

remove_container() {
  running=$(docker inspect --format="{{ .State.Running }}" $container_name 2> /dev/null)

  if [ $? -eq 0 ]; then
    docker rm --force $container_name
    echo "'$container_name' removed"
  fi
}

remove_container

docker run -d \
  -it \
  --name $container_name \
  --mount type=bind,source=$mount_source,target=$mount_target \
  --mount type=bind,source=$(pwd)/received_audio,target=/app/received_audio \
  --mount type=bind,source=$(pwd)/transcribed_text,target=/app/transcribed_text \
  --env-file .env \
  $image_name