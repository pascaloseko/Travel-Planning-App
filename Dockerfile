FROM python:3.8

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory
WORKDIR /app

# Copy only the requirements file, to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire application
COPY app /app/app

# Copy libuplinkc.so into the Python package directory
COPY libuplinkc.so /usr/local/lib/python3.8/site-packages/uplink_python/

# Expose the port
EXPOSE 8050

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8050"]
