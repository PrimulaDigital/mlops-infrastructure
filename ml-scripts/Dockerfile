# Use a specific version of Python as the base image
FROM python:3.9

# Set the working directory
WORKDIR /opt/ml

# Copy requirements.txt
COPY requirements.txt /opt/ml/

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the training and inference scripts
COPY train.py /opt/ml/
COPY inference.py /opt/ml/

# Specify the command to run your training script
ENTRYPOINT ["python", "/opt/ml/train.py"]
