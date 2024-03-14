FROM python:3.10.12

# Set environment variables
ENV PYTHONUNBUFFERED 1
# ENV other variables as needed

# Set the working directory in the container
WORKDIR /homepage

# Copy the current directory contents into the container at /homepage
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000 for gunicorn
EXPOSE 8000

# Use gunicorn to run the application
CMD gunicorn -b 0.0.0.0:$PORT homepage_project_settings.wsgi:application

