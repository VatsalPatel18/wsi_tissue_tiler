# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /app
WORKDIR /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' myuser
USER myuser

# Copy only the necessary files
COPY --chown=myuser:myuser requirements.txt slide_processor_parallel.py extract_one_wsi.py extract_multiple_wsi.py /app/

# Switch to root to install dependencies
USER root
RUN apt-get update && \
    apt-get install -y build-essential openslide-tools && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

# Switch back to the non-root user
USER myuser

# Set the entrypoint to your script
ENTRYPOINT ["python", "extract_multiple_wsi.py"]
# Alternatively, set CMD to run your script, but this can be overridden by command line arguments
# CMD ["python", "extract_multiple_wsi.py"]
