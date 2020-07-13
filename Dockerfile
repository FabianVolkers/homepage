# Use the official Python image from the Docker Hub
FROM python:3.7.7

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
    && apt-get install -y netcat

# Create an app user in the app group. 
RUN useradd --user-group --create-home --no-log-init --shell /bin/bash app

ENV APP_HOME=/home/app/web

# Change the workdir.
WORKDIR $APP_HOME

COPY requirements.txt $APP_HOME
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# For media serving in dev mode, remove in production
#RUN pip install Pillow

RUN mkdir -p $APP_HOME/static
RUN mkdir -p $APP_HOME/media
# Copy the rest of the code. 
COPY ./homepage $APP_HOME

RUN chown -R app:app $APP_HOME

#COPY ./homepage/portfolio/static /var/www/media/static

USER app:app

ENTRYPOINT ["/home/app/web/entrypoint.sh"]