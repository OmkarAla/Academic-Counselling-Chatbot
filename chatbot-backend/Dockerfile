# Use a Node.js base image with Python installed
FROM node:18

# Install Python & Pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Node.js dependencies
RUN npm install

# Install Python dependencies
RUN pip3 install -r chatbot-backend/requirements.txt

# Start both Node.js and Python server
CMD npx concurrently "node chatbot-backend/server.js" "python3 chatbot-backend/rag_backend.py"
