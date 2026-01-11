# Remetra

Autoimmune symptom tracking and ML correlation platform

## Overview

Remetra helps autoimmune disease patients track symptoms, food, and activities to identify patterns and prevent flare-ups through Data analysis.

## Development

### Quick Start

Build Images:
```bash
just setup
```

Start all services with Docker:
```bash
just dev
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to view the API documentation.

### Common Commands

| Command            | Description                   |
|--------------------|-------------------------------|
| `just setup`       | Build images |
| `just dev`         | Start services with hot reload |
| `just test`        | Run all tests                 |
| `just lint`        | Check code quality            |
| `just format`      | Auto-fix formatting issues    |
| `just docker-down` | Stop all services             |

Run `just --list` to see all available commands.

## Project Structure
```
remetra/
├── backend/              # FastAPI backend
├── mobile/               # Mobile app
├── tests/                # Test suite
├── docs/                 # Documentation
└── .github/workflows/    # CI/CD
```

## Tech Stack

- **Backend**: FastAPI, Python
- **Database**: TBD
- **Mobile**: TBD
- **Infrastructure**: Docker

## Team

Built by Generate Product Development Studio at Northeastern University

## Contributing

See [README-DEV.md](./README-DEV.md) for development setup and guidelines.