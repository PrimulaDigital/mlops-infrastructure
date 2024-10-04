# Use a specific version of Python as the base image
FROM python:3.9

# Set the working directory
WORKDIR /opt/ml

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the training and inference scripts
COPY train.py .

# Specify the command to run your training script
ENTRYPOINT ["python", "/opt/ml/train.py"]
