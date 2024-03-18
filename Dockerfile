FROM python:3.10.12

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /homepage

# Copy the current directory contents into the container at /homepage
COPY . .

# Copy your SSL certificates (comment out for production)
#COPY certificate.crt .
#COPY certificate.key .

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000 for gunicorn
EXPOSE 8000

# Use gunicorn to run the application with SSL certificates (production version is listed at top, dev version is below)
CMD gunicorn -b 0.0.0.0:$PORT homepage_project_settings.wsgi:application

#CMD gunicorn -b 0.0.0.0:8000 --certfile=certificate.crt --keyfile=certificate.key --timeout 120 --log-level debug --access-logfile - --error-logfile - homepage_project_settings.wsgi:application
