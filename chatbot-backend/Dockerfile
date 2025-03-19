# Use a base image with both Node.js and Python installed
FROM ubuntu:22.04

# Install Node.js, npm, Python3, and Pip
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    python3 \
    python3-pip \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Node.js dependencies
RUN npm install

# Install Python dependencies
RUN pip3 install --no-cache-dir -r chatbot-backend/requirements.txt

# Ensure Python3 is properly linked
RUN ln -s /usr/bin/python3 /usr/bin/python

# Start both Node.js and Python server
CMD npx concurrently "node chatbot-backend/server.js" "python3 chatbot-backend/rag_backend.py"
