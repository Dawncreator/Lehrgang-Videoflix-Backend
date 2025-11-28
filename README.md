Videoflix Backend

A complete backend API for the Videoflix project.
Provides user authentication, secure JWT HttpOnly cookies, email activation, password reset, video listing, and full HLS streaming support.
The entire backend runs inside Docker for full reproducibility including automatic HLS conversion and thumbnail generation via ffmpeg and Django-RQ worker.

Table of Contents

Overview

Technologies Used

Features

Requirements

Project Structure

Installation

Environment Setup

Running the Project

Docker Commands

Database Migrations

Running Tests

HLS Directory Structure

API Endpoints

Authentication Flow

Superuser Creation

Troubleshooting

Overview

The Videoflix backend provides:

user registration with email activation

login with HttpOnly cookies

refresh token flow

secure logout with token blacklist

password reset system

video listing

automatic HLS conversion via ffmpeg (480p, 720p, 1080p)

automatic thumbnail generation and URL assignment

Redis + Django-RQ worker for background tasks

Docker-based reproducible environment

PEP8-compliant codebase

Technologies Used

Python 3.12

Django 5.2

Django REST Framework

PostgreSQL

Redis

Django-RQ

ffmpeg (video conversion)

JWT (manual cookie-based implementation)

Docker & Docker Compose

WhiteNoise

Features
Authentication

Email registration

Activation link

Login with HttpOnly cookies

Access/refresh token flow

Password reset

Logout with refresh token blacklist

Video System

Video list endpoint

HLS manifest + segment serving

Automatic ffmpeg conversion

Automatic thumbnail extraction (1-second frame)

Background processing using RQ worker

Compatible with existing frontend expectations

Requirements
Windows

Docker Desktop

WSL2

Ubuntu

VS Code

macOS

Docker Desktop

VS Code

Project Structure
core/
    settings.py
    urls.py

auth_app/
    api/...

video_app/
    api/...
    tasks.py     <-- ffmpeg HLS + thumbnails
    signals.py   <-- triggers worker jobs
    models.py

media/
    videos/
    hls/
    thumbnails/

docker-compose.yml
backend.Dockerfile
requirements.txt
.env.example

Installation
git clone <your repository>
cd <project>

Environment Setup
cp .env.example .env


Fill environment variables:

SECRET_KEY=your-secret-key

DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=videoflix_pass
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

Running the Project
1. Start Docker Desktop
2. Start all services
docker compose up --build


Backend:

http://localhost:8000


Admin panel:

http://localhost:8000/admin/

3. Stop services
docker compose down

Docker Commands

Build + run:

docker compose up --build


Stop:

docker compose down


Backend logs:

docker compose logs -f web


Worker logs:

docker compose logs -f worker


Enter backend container:

docker compose exec web bash

Database Migrations
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

Running Tests
docker compose exec web pytest

HLS Directory Structure
media/
    hls/
        <id>/
            480p/
                index.m3u8
                0000.ts
            720p/
            1080p/
    thumbnails/
        <id>.jpg
    videos/
        uploaded_file.mp4


(Video conversion and thumbnail extraction are executed automatically by the RQ worker.)

API Endpoints
Authentication
POST /api/register/
GET  /api/activate/<uid>/<token>/
POST /api/login/
POST /api/logout/
POST /api/token/refresh/
POST /api/password_reset/
POST /api/password_confirm/<uid>/<token>/

Video
GET /api/video/


HLS files are not under /api — they are served directly from /media:

/media/hls/<id>/<resolution>/index.m3u8
/media/hls/<id>/<resolution>/<segment>.ts


Thumbnails:

/media/thumbnails/<id>.jpg

Authentication Flow

User registers

Backend sends activation email

User activates account

Login sets HttpOnly cookies

Access token expires

Refresh token is used to obtain a new one

Logout blacklists the refresh token

Superuser Creation
docker compose exec web python manage.py createsuperuser

Troubleshooting
Terminal freezes on Windows
wsl --shutdown

Worker did not generate HLS files
docker compose logs -f worker


Check for ffmpeg errors inside the container.

Thumbnails missing in Admin

ensure worker is running

ensure /app/media/thumbnails/ is writable

check worker logs

Player loads forever

ensure path: /media/hls/<id>/<resolution>/index.m3u8

ensure resolution folders exist (480p/720p/1080p)
