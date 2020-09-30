# Python image to use.
FROM python:3.8-slim

# Set the working directory to /app
ENV APP_HOME /app
WORKDIR $APP_HOME

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

RUN python manage.py collectstatic --noinput

ENV PORT 8080

ENV DEBUG 0

# Setting this ensures print statements and log messages
# promptly appear in Cloud Logging.
#ENV PYTHONUNBUFFERED TRUE


# Run app.py when the container launches
#ENTRYPOINT ["python", "app.py"]

#EXPOSE 8090

CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 config.wsgi:application --log-config config/gunicorn_logging.conf