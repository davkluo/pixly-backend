# Pixly Backend
RESTful API backend for photo sharing and gallery app with EXIF data extraction.

The accompanying frontend can be found [here](https://github.com/davkluo/pixly-frontend).

## Table of Contents

- [Motivation](#motivation)
- [Tech Stack](#tech-stack)
- [Setup](#setup)
- [Running the App](#running-the-app)
- [Project Structure](#project-structure)
- [API](#api)
- [Future Improvements](#future-improvements)

## Motivation

- Create a full-stack application where images could be uploaded and viewed
- Extract and display EXIF data from images
- Make simple edits to images prior to uploading
- Utilize Amazon S3 to store files

## Tech Stack

Built with Flask and PostgreSQL

## Setup

### Clone the repo

```bash
git clone git@github.com:davkluo/pixly-backend.git
cd pixly-backend
```

### Set environment variables

```bash
cp .env.example .env
# open .env and modify the secret key environment variable
```

You will need to create an AWS bucket with public folder locations /pixly/images/originals and /pixly/images/thumbnails

### Create virtual env

```bash
python3 -m venv venv
```

### Activate virtual env

```bash
source venv/bin/activate
```

### Install python packages

```bash
pip install -r requirements.txt
```

### Create database in psql

```bash
psql
CREATE DATABASE pixly;
```

## Running the App

```bash
flask run -p 5000
```

## Project Structure
```
\                                 # Root folder
 |--app.py                        # main routes scripts
 |--image_processing.py           # image processing helper functions
 |--models.py                     # database models and methods
 |--pixly_aws.py                  # methods for uploading to aws
 |--readme.md                     # project readme
 |--requirements.txt              # dependencies
 |--service.py                    # route servicing functions
```
## API
List of available routes:
**Images routes**:\
`GET /api/images` - get all images as json data (optional filtering)\
`GET /api/images/:id` - get json data for image by id\
`POST /api/images` - post/upload new photo\
`PATCH /api/images/:id` - patch to increment image view count by id

## Future Improvements
- Write tests
- Add image tagging feature
- Add image filtering options for more EXIF categories
