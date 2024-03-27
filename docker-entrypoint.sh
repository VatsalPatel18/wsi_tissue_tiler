#!/bin/sh

# Adjust permissions of the mounted volume to ensure myuser can write to it
chown -R myuser:myuser /app/outputs

# Execute the main command
exec "$@"
