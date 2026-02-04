# Remetra Developer Guide

Welcome! This guide will help you get set up and contributing to Remetra. Don't worry if some concepts are new - we're here to help you learn as we build!

## Quick Note Before You Start

We're throwing a lot of information at you all at once - Docker, APIs, databases, Git workflows, testing, etc. For a lot of you, most of this stuff is probably completely new, both the concepts and the technology itself. 

**It's not expected to stick right away.** Like genuinely, if 10% makes sense at the beginning, that's totally normal. This is a lot, especially if you're coming from a DS background or haven't worked on development projects before.

**Please ask questions ‼️‼️‼️.** I know it's easy to feel like you should just figure it out or that asking makes you seem less capable, but that's really not the case. Everyone learns this stuff by asking questions and running into issues. The only reason I know any of this is through a lot of experience and trial and error - there's no shortcut to that.

**Seriously, bother us with questions.** Slack, meetings, email, whatever - we want to make sure everyone's comfortable, especially at the beginning. By working through problems and asking when you're stuck, you'll gradually build understanding as the semester goes on. That's the whole point.

---

## Table of Contents

- [First-Time Setup](#first-time-setup)
  - [Windows Setup](#windows-setup)
  - [macOS Setup](#macos-setup)
- [Daily Development Workflow](#daily-development-workflow)
- [Project Structure](#project-structure)
- [Common Commands](#common-commands)
- [Understanding the Codebase](#understanding-the-codebase)
- [Adding Dependencies](#adding-dependencies)
- [Git Workflow](#git-workflow)
- [Code Quality](#code-quality)
- [Troubleshooting](#troubleshooting)

---

## First-Time Setup

Choose your operating system below and follow the steps in order.

### Windows Setup

**1. Install Docker Desktop**
- Download: https://www.docker.com/products/docker-desktop
- Run the installer and follow prompts
- Restart your computer when prompted
- Open Docker Desktop - wait for it to fully start (Docker icon in system tray)

**2. Install Git**
- Download: https://git-scm.com/downloads
- Use default settings during installation
- Verify: Open Command Prompt → `git --version`

**3. Install Just (Command Runner)**

Open **PowerShell as Administrator** (right-click PowerShell → "Run as Administrator"):

```powershell
# Install Scoop (package manager)
irm get.scoop.sh | iex

# Install just
scoop install just
```

Verify it worked:
```powershell
just --version
```

You may need to restart PowerShell or your IDE after installation.

**4. Install Python 3.11+**
- Download: https://www.python.org/downloads/
- **Important:** Check "Add Python to PATH" during installation
- Verify: `python --version`

**5. Install UV (Python Package Manager)**

In PowerShell:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart PowerShell, then verify:
```powershell
uv --version
```

**6. Clone Repository and Build**

```powershell
# Clone the repo
git clone git@github.com:GenerateNU/remetra.git
cd remetra

# Set up local Python environment (for IDE autocomplete/linting)
cd backend
uv sync && uv run pre-commit install # setup pre-commit hooks
cd ..

# Build Docker images (takes 3-5 minutes first time)
just setup

# Start development server
just dev
```

Open http://localhost:8000/docs in your browser - you should see the API documentation!

Press `Ctrl+C` in the terminal to stop the server when done.

---

### macOS Setup

**1. Install Homebrew (Package Manager)**

Open Terminal:

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow on-screen instructions. You might need to add Homebrew to your PATH - the installer will show you the exact command.

**2. Install Docker Desktop**
- Download: https://www.docker.com/products/docker-desktop
- Drag to Applications folder
- Open Docker Desktop - wait for it to start completely

**3. Install Development Tools**

```bash
# Install everything in one go
brew install git just python@3.11 uv
```

Restart Terminal, then verify:
```bash
git --version
just --version
python3 --version
uv --version
```

**4. Clone Repository and Build**

```bash
# Clone the repo
git clone git@github.com:GenerateNU/remetra.git
cd remetra

# Set up local Python environment (for IDE autocomplete)
cd backend
uv sync
cd ..

# setup frontend
cd frontend
npm install
cd ..

# Build Docker images (takes 3-5 minutes first time)
just setup

# Start development server (backend)
just dev
```

Open http://localhost:8000/docs - you should see the API documentation!

Press `Ctrl+C` to stop the server.

---

## Sample Development Workflow 😱

Once setup is complete, here's how a workflow for a ticket may look:

```bash
# 1. Make sure you're on main and pull latest changes
git checkout main
git pull origin main

# 2. Create a new branch for your work
git checkout -b feat/your-feature-name

# 3. Start the development server
just dev
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs or /scalar
# Changes auto-reload when you save files!

# 4. Make your code changes in your IDE

# 5. Check code quality (do this often!)
just lint      # Check for issues
just format    # Auto-fix formatting
just test      # Run tests

# 6. Commit your changes
git add .
git commit -m "feat: add symptom tracking endpoint"


# 7. Push to GitHub
git push origin feat/your-feature-name

# 8. Open a Pull Request on GitHub
# Go to the repo on GitHub, click "Compare & pull request", and fill out the PR description template
```
**Note:** We follow [conventional commits](https://www.conventionalcommits.org/) - prefix with `feat:`, `fix:`, `chore:`, `docs:`, etc.
---

## Project Structure

```
remetra/
├── .github/workflows/       # CI/CD (auto-runs tests on every push)
├── backend/                 # FastAPI backend
│   ├── examples/            # Example code
│   │   ├── example_pydantic_models.py    # Request/response models
│   │   ├── example_service_layer.py      # Business logic
│   │   └── example_router.py             # API endpoints
│   ├── tests/               # Test files
│   │   ├── examples/        # Example tests showing patterns
│   │   └── conftest.py      # Shared test fixtures
│   ├── main.py              # App entry point
│   ├── pyproject.toml       # Python dependencies
│   └── pytest.ini           # Test configuration
├── frontend/                # Mobile app (separate dev readme in folder)
├── docs/                    # Documentation
├── docker-compose.yml       # Docker orchestration
├── Dockerfile.backend       # Backend container dockerfile
├── Justfile                 # Development commands
├── README.md                # Project overview
└── README-DEV.md            # This file
```

**Start Here:**
- Read `examples/` files to understand code patterns
- Check `docs/ARCHITECTURE.md` for system design
- Look at `tests/examples/` to see how to write tests

---

## Common Commands

Run these from the project root directory:

| Command | What It Does |
|---------|--------------|
| `just dev` | Start development server with hot reload |
| `just test` | Run all tests |
| `just lint` | Check code for style/quality issues |
| `just format` | Auto-fix formatting problems |
| `just rebuild` | Rebuild Docker images (after adding packages) |
| `just down` | Stop all Docker containers |
| `just shell` | Open terminal inside backend container |
| `just logs` | View backend logs |

Run `just --list` to see all available commands.

---

## Understanding the Codebase

### What is an API?

An API (Application Programming Interface) is how our mobile app communicates with our backend. 
Here's a [link](https://www.youtube.com/watch?v=s7wmiS2mSXY) to a good video

Example: User logs a symptom → App sends request to `POST /symptoms` → Backend saves it to database

### N-Tier Architecture

We organize code into layers to keep things clean and maintainable:

```
┌──────────────┐
│   Router     │  ← Handles HTTP (API endpoints in routers/)
└──────────────┘
       ↓
┌──────────────┐
│   Service    │  ← Business logic (services/)
└──────────────┘
       ↓
┌──────────────┐
│  Repository  │  ← Database operations (repositories/)
└──────────────┘
       ↓
┌──────────────┐
│   Database   │  ← SQL/NOSQL/ETC.
└──────────────┘
```

**Why separate?**
- **Easier to test** - can test business logic without HTTP
- **Easier to change** - swap databases without touching business rules
- **Easier to understand** - each file has one clear responsibility

See `docs/ARCHITECTURE.md` for more details.

### Pydantic Models

Pydantic models define the shape of data and validate it automatically:

```python
class SymptomCreate(BaseModel):
    symptom_type: str          # Required string
    severity: int              # Required integer
    notes: str | None = None   # Optional string
```

When a request comes in, FastAPI automatically:
- Checks the data matches the model
- Returns error if validation fails
- Converts to the right types
- Shows in API docs

Check `examples/example_pydantic_models.py` for detailed examples!

### Docker - Why We Use It

**The Problem:** "It works on my machine" - code works for one person but breaks for others due to different:
- Python versions
- Installed packages
- Operating systems
- Enviroments

**The Solution:** Docker creates identical environments for everyone. When you run `just dev`:
1. Docker starts a Linux container
2. Installs exact Python 3.11
3. Installs exact package versions from `uv.lock`
4. Runs your code

Everyone gets the same environment mitigating possible issues due to different development environments

**Important:** 
- Code runs **inside Docker** (Linux)
- Your local Python is just for IDE support (autocomplete, linting)
- **Always** use `just` commands to run code, not `python main.py`

---

## Adding Dependencies

When you need a new Python package:

```bash
# In the backend/ folder
cd backend
uv add package-name

# Example: uv add pandas
```

This updates both `pyproject.toml` and `uv.lock`. **Commit both files:**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add package-name dependency"
```

Then rebuild Docker to use the new package:
```bash
just rebuild
```

**Important:** Don't edit `pyproject.toml` or `uv.lock` manually - always use `uv add`.

---

## Git Workflow

### Branch Naming

Use descriptive branch names with prefixes:
- `feat/symptom-tracking` - New features
- `fix/login-bug` - Bug fixes
- `chore/update-deps` - Maintenance tasks

### Commit Messages

Keep commits clear and concise:

**Good:**
- `feat: add symptom severity validation`
- `fix: resolve duplicate detection bug`
- `docs: update setup instructions`

**Not ideal:**
- `updated stuff`
- `fixed it`
- `changes`

### Pull Request Process

1. Push your branch to GitHub
2. Open a Pull Request (PR) against `main`
3. CI will automatically run tests and linting
4. Request review from tech leads
5. Address any feedback
6. Once approved and CI passes, we'll merge!

**Branch Protection:** You cannot merge PRs with failing tests or linting issues.

---

## Code Quality

### Linting & Formatting

We use **Ruff** for code quality. It checks:
- Code style (formatting, line length)
- Import organization
- Unused variables
- Common bugs

**Before every commit:**
```bash
just lint      # Check for issues
just format    # Auto-fix what's fixable
```

**CI will block PRs** with linting issues, so fix them locally first!

### Testing

Every feature should have tests. Check `tests/examples/test_example.py` to see how.

**Run tests:**
```bash
just test
```

**Writing tests:**
- Test file names: `test_*.py`
- Test function names: `test_something()`
- Use fixtures for reusable setup (see `conftest.py`)

---

## IDE Setup

### PyCharm

1. Open the `remetra` folder as a project
2. Right-click `backend/` → "Mark Directory as" → "Sources Root"
3. File → Settings → Project → Python Interpreter
4. Add Interpreter → Existing → Select `backend/.venv/bin/python` (or `.venv\Scripts\python.exe` on Windows)
5. Apply and OK

Now you'll get autocomplete and error checking!

### VS Code

1. Open the `remetra` folder
2. Install Python extension
3. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
4. Type "Python: Select Interpreter"
5. Choose the interpreter from `backend/.venv`

VS Code should auto-detect the venv and configure itself.

---

## Troubleshooting

### Docker Issues

**"Docker daemon is not running"**
- Open Docker Desktop and wait for it to start
- You should see the Docker icon in your system tray/menu bar

**"Port 8000 is already in use"**
```bash
# Stop existing containers
just down

# Or change the port in docker-compose.yml
```

**"Container exits immediately"**
```bash
# Check logs for errors
just logs

# Rebuild from scratch
just rebuild
```

### Import Errors in IDE

**Red squiggly lines or "Cannot find module 'examples'"**

If your IDE shows import errors but the code runs fine in Docker (`just dev` works), don't worry too much about it. Your code will work - Docker has everything it needs.

That said, fixing IDE errors makes development way easier (autocomplete, type checking, etc.). To fix:

1. Make sure you ran `uv sync` in the `backend/` folder
2. Configure your IDE to use the Python interpreter from `backend/.venv`:
   - **PyCharm:** File → Settings → Project → Python Interpreter → Add → Existing → Select `backend/.venv`
   - **VS Code:** Command Palette → "Python: Select Interpreter" → Choose from `backend/.venv`
3. **PyCharm only:** Right-click `backend/` → "Mark Directory as" → "Sources Root"
4. Restart your IDE

**Remember:** If Docker works (`just dev`, `just test`), your code is fine. IDE setup is just for convenience.

### UV/Package Issues

**"UV command not found after install"**
- Restart your terminal/IDE
- On Windows: Check that `C:\Users\<you>\bin` is in your PATH

**"Failed to remove directory .venv"**
- Close your IDE completely
- Delete `.venv` folder manually
- Run `uv sync` again

### Test Failures

**"ModuleNotFoundError" in tests**
- Make sure all folders have `__init__.py` files
- Rebuild Docker: `just rebuild`

### Git Issues

**Accidentally committed sensitive data**
1. Don't panic
2. Immediately notify tech leads
3. We'll help remove it from history

**Merge conflicts**
1. Ask for help if this is your first time‼️‼️‼️
2. We will walk you through resolving them

---

## Getting Help

**Stuck/Confused?**

Please reach out to a TL (It's our job to help)!

**Other Resources:**
- Check `docs/` folder for architecture and design decisions
- Look at `examples/` code for patterns
- Review existing code in the repo
- FastAPI docs: https://fastapi.tiangolo.com/
- Python docs: https://docs.python.org/3/

---

## Quick Reference

### Environment Setup Checklist

- [ ] Docker Desktop installed and running
- [ ] Git installed
- [ ] Just installed
- [ ] Python 3.11+ installed
- [ ] UV installed
- [ ] Repository cloned
- [ ] `uv sync` completed in backend/
- [ ] `just setup` completed successfully
- [ ] `just dev` starts server successfully
- [ ] Can access http://localhost:8000/docs

### Before Every Commit

- [ ] `just lint` passes
- [ ] `just format` run
- [ ] `just test` passes
- [ ] Meaningful commit message
- [ ] No sensitive data (passwords, API keys, etc.)

### Opening a PR

- [ ] Branch name is descriptive (feat/fix/chore prefix)
- [ ] Code is tested locally
- [ ] Linting passes
- [ ] Tests pass
- [ ] PR description explains what and why
- [ ] Requested review from tech leads

---

## Example Code

The `backend/examples/` folder contains fully-commented example code showing:
- `example_pydantic_models.py` - How to define request/response models
- `example_service_layer.py` - How to write business logic
- `example_router.py` - How to create API endpoints
- `tests/examples/test_example.py` - How to write tests

They follow all the patterns and best practices we use in this project.

---

## Tech Stack Quick Reference (Will Change over time - tentative)

- **FastAPI** - Python web framework for building APIs
- **Docker** - Containerization (consistent environments)
- **PostgreSQL or MongoDB** - Database (TBD)
- **Pytest** - Testing framework
- **Ruff** - Code linting and formatting
- **UV** - Fast Python package manager
- **Just** - Command runner (like make but simpler)
- **GitHub Actions** - CI/CD automation

---