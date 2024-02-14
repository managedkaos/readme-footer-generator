# Use an official Python runtime as a parent image
FROM python:alpine3.16


# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the script into the container at /usr/src/app
COPY . .

# Run the script when the container launches
ENTRYPOINT ["python", "/usr/src/app/script.py"]

