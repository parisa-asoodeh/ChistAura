# ChistAura

![Python](https://img.shields.io/badge/Python-3%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6%2B-darkgreen?logo=django)
![Backend](https://img.shields.io/badge/Project-Backend-success)
![Status](https://img.shields.io/badge/Status-Active_Development-orange)
![GitHub license](https://img.shields.io/github/license/parisa-asoodeh/ChistAura)

---

A modular Django backend for managing game tournaments, teams, matches, and player scoring and rankings.

This project is a backend-focused platform designed to manage multiplayer game competitions through a scalable and maintainable architecture. It supports tournament management, team organization, match tracking, player scoring, and ranking systems while providing a flexible foundation for adding new game types and advanced features in the future.

## Features

- User authentication and profile management
- Team creation and membership management
- Tournament management and lifecycle control
- Match management and result tracking
- Automatic player and team score calculation
- Team and player leaderboards
- Extensible support for multiple game types
- Modular service-layer architecture
- Game session management
- Extensible project architecture
- Foundation for AI-powered analysis and predictions

## Architecture Highlights

- Modular Django application structure with separated apps for accounts, teams, games, and competitions.
- Service Layer pattern to keep business logic independent from views and forms.
- Extensible game type system for supporting different game mechanics and scoring strategies.
- Automatic ranking and scoring services with clear separation of responsibilities.
- Designed for scalability and long-term feature expansion.

## Tech Stack

- **Backend:** Django 6, Python 3
- **Database:** SQLite (development)
- **Architecture:** Service Layer, Modular App Structure
- **Authentication:** Django Authentication System
- **Version Control:** Git & GitHub

## Project Structure

```
game-competition-platform/
├── competition/
│   ├── accounts/
│   ├── competitions/
│   ├── games/
│   ├── pages/
│   ├── teams/
│   ├── templates/
│   ├── competition/
│   └── manage.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/parisa-asoodeh/ChistAura.git
cd game-competition-platform
```

### 2. Create and activate a virtual environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Navigate to the Django project

```bash
cd competition
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver
```

Then open:

```
http://127.0.0.1:8000/
```

## Roadmap

Planned improvements include:

- [ ] REST API with Django REST Framework
- [ ] PostgreSQL support
- [ ] Docker configuration
- [ ] CI/CD with GitHub Actions
- [ ] Comprehensive unit and integration tests
- [ ] Tournament statistics dashboard
- [ ] Advanced AI-powered match analysis
- [ ] Match scheduling improvements
- [ ] Performance optimization

## Design Principles

This project is built around the following software design principles:

- **Modularity:** Independent Django apps with clearly defined responsibilities.
- **Separation of Concerns:** Business logic is separated from views and forms through dedicated service classes.
- **Extensibility:** New game types, scoring rules, and competition features can be added with minimal changes to the existing codebase.
- **Maintainability:** Clear project organization and reusable services simplify future development.
- **Scalability:** The architecture is designed to support future growth without major structural changes.

## Current Status

This project is actively under development. New features, architectural improvements, and additional game types are planned as part of its long-term roadmap.

## Contributing

Contributions are welcome. If you have suggestions for improvements or find a bug, feel free to open an issue or submit a pull request.

## Author

**Parisa Asoodeh**

Backend Developer | Python & Django

## Project Goals

This project is being developed to:

- Explore backend architecture and software design principles.
- Build a scalable Django application following best practices.
- Serve as a long-term portfolio and learning project.