# Use a Node.js base image
FROM node:18

# Install Python & Pip
RUN apt-get update && apt-get install -y python3 python3-pip && \
    ln -s /usr/bin/python3 /usr/bin/python  # Ensure python command works

# Set working directory
WORKDIR /app

# Copy files
COPY . .

# Install Node.js dependencies
RUN npm install

# Install Python dependencies
RUN pip3 install --no-cache-dir -r chatbot-backend/requirements.txt

# Start both Node.js and Python server
CMD npx concurrently "node chatbot-backend/server.js" "python3 chatbot-backend/rag_backend.py"
