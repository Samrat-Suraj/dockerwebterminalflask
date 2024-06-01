# Use the official Ubuntu image as a base
FROM kalilinux/kali-rolling

# Update package lists and install necessary packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the entire current directory into the container at /app
COPY . /app

# Install pyxtermjs
RUN pip3 install -r requirements.txt --break-system-packages

# Run the pyxtermjs command when the container starts
CMD ["python3", "main.py"]
