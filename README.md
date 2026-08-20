# ChistAura

![Python](https://img.shields.io/badge/Python-3.14.5-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.0.5-darkgreen?logo=django)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![Status](https://img.shields.io/badge/Status-Active-orange)

A modular Django platform for managing multiplayer game competitions, tournaments, teams, matches, rankings, and interactive games.

---

## Table of Contents

- About
- Features
- Architecture
- AI Features
- Automated Scheduling
- Security
- Testing
- Technology Stack
- Installation
- Running Tests
- Roadmap
- Author

---

## About

ChistAura is a Django-based competition platform designed to manage multiplayer tournaments and different types of games.

Version 2 is a major evolution of the original project, introducing a Swiss System tournament engine, a fully implemented interactive Quiz game, AI-powered analysis and predictions, improved security, and automated tournament scheduling.

The architecture is designed to keep the tournament system independent from individual game implementations, making it easier to add new games in the future.

---

## Features

- Swiss System tournament management
- Progressive round-based tournament execution
- Team and player management
- Interactive Quiz game
- Match and game session management
- Tournament, team, and player rankings
- Time-based scoring and tie-breaking
- AI-powered match and tournament analysis
- Match winner prediction
- Tournament champion prediction
- Automated match reports
- Best player analysis
- Scheduled round execution
- Security and state validation
- Extensive automated testing
- Extensible game architecture

---

## Architecture

The core competition flow is based on:

    Tournament
        |
        +-- Round
        |     |
        |     +-- Round Questions
        |     +-- Pairings / Bye
        |     +-- Matches
        |            |
        |            +-- Game Sessions
        |
        +-- Final Ranking
                |
                +-- Champion

The project follows a modular Django architecture with a dedicated Service Layer.

Main applications:

    accounts/
    competitions/
    games/
    teams/
    pages/
    templates/

Business logic is separated into dedicated services for tournaments, rounds, pairing, matches, games, scoring, ranking, and AI analysis.

---

## AI Features

ChistAura includes an AI analysis layer for teams, matches, and tournaments.

Current capabilities include:

- Performance analysis
- Team power ranking
- Match winner prediction
- Tournament champion prediction
- Best player analysis
- Automated match reports
- Performance explanations

The analysis system considers multiple performance factors, including average performance, consistency, momentum, match difficulty, team balance, and star-player dependency.

---

## Automated Scheduling

The project includes a Django Management Command for automatically starting scheduled rounds.

    python manage.py start_scheduled_rounds

The scheduling mechanism has been tested successfully with Windows Task Scheduler and is designed to be ready for integration with an appropriate scheduler in a production environment.

---

## Security

Version 2 includes additional security and state validation around gameplay and tournament execution.

The system validates:

- Round state
- Game access
- Game submission
- Match and session state
- Gameplay data transmission

Critical gameplay operations also use atomic database transactions where required.

---

## Testing

The project has an extensive automated test suite covering:

- Tournament lifecycle
- Swiss pairing
- Round execution
- Match management
- Quiz gameplay
- Game sessions
- Scoring
- Ranking
- Scheduling
- AI analysis and predictions
- Security-related workflows

Run the complete test suite with:

    python manage.py test

---

## Technology Stack

- Python 3.14.5
- Django 6.0.5
- SQLite (development)
- Django Templates
- JavaScript
- Django Test Framework
- Django Management Commands
- Windows Task Scheduler
- Git & GitHub

---

## Installation

### 1. Clone the repository

    git clone https://github.com/parisa-asoodeh/ChistAura.git
    cd ChistAura

### 2. Create a virtual environment

Windows:

    python -m venv venv
    venv\Scripts\activate

Linux / macOS:

    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies

    python -m pip install -r requirements.txt

### 4. Run migrations

    cd competition
    python manage.py migrate

### 5. Start the development server

    python manage.py runserver

Then open:

    http://127.0.0.1:8000/

---

## Running Tests

Run the complete automated test suite:

    python manage.py test

---

## Roadmap

- [ ] Additional fully implemented game types
- [ ] REST API
- [ ] PostgreSQL production configuration
- [ ] Docker support
- [ ] CI/CD
- [ ] Advanced tournament statistics
- [ ] Production deployment

---

## Author

Parisa Asoodeh

Backend Developer | Python & Django

---

## Project Goals

ChistAura is being developed as a long-term backend engineering project focused on:

- Scalable competition architecture
- Reusable tournament infrastructure
- Extensible game systems
- AI-assisted analysis
- Secure and reliable gameplay
- Clean service-oriented design
- Strong automated testing