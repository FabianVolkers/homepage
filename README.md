# Portfolio Page <!-- omit in TOC -->

## Contents <!-- omit in TOC -->
- [Description](#description)
- [Technologies](#technologies)
- [Deployment](#deployment)
- [Run the App](#run-the-app)
  - [Run with docker](#run-with-docker)
  - [Run directly on host machine](#run-directly-on-host-machine)


## Description
This is the source code for my personal portfolio page, live at [fabianvolkers.com](https://fabianvolkers.com). It features an overview of the projects I've worked on as well as detail views for each project. Additionally, it features a selection of my photographs. There is a contact form for enquiries.

## Technologies
This portfolio page is built with Python and Django. Django was chosen for it's powerful and secure ORM, easy DB migrations and the built in admin page for managing the database.

## Deployment
The app is running live at [fabianvolkers.com](https://fabianvolkers.com). The Django app is running as a service inside a Docker Swarm. On top of that, we handle load balancing and proxying with a Traefik instance inside the Swarm.

## Run the App
The easiest way to run the app is to clone this repository and start a docker container with the included Dockerfile. Alternatively you can clone the repo and use Django's manage.py runserver command.

### Run with docker
```bash
# Clone the repository
git clone https://github.com/FabianVolkers/portfolio.git
cd portfolio
# Build the docker image
docker build --tag portfolio:latest
# Run the docker image
docker run --publish 8000:8000 --detach --name portfolio portfolio:latest
```

### Run directly on host machine
```bash
# Clone the repository
git clone https://github.com/FabianVolkers/portfolio.git
cd portfolio

# Create and activate the virtual environment, install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy the example.env file into a .env file. Don't forget to replace the values with your own.
cp example.env .env

# Change into the project directory, initialise the database and run the server
cd homepage
python manage.py makemigrations portfolio
python manage.py migrate
python manage.py runserver
```