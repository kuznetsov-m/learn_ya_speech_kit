# read .env file
export $(grep -v '^#' .env | xargs -0)

# docker build --no-cache -t $APP_NAME:latest .
docker build -t $APP_NAME:latest .