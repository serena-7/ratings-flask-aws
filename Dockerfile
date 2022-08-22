# Set base image (host OS)
FROM python:3.10-alpine

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy files into workdir (this will ignore files in dockerignore)
COPY . .

# Install any dependencies gcc musl-dev
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps build-base postgresql-dev
RUN pip install -r requirements.txt
RUN apk --purge del .build-deps

# Specify the command to run on container start
CMD [ "python", "./server.py" ]