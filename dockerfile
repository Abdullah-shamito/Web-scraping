FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libglib2.0-0 libxext6 libsm6 libxrender1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 

# Install Chrome
RUN apt-get update && \
    apt-get install -y wget && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install

# Set work directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Command to run on container start
CMD ["python", "my.py"]
