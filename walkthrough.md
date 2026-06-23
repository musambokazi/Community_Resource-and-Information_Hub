# Walkthrough: Running the Community Resource Hub Locally

Here is a summary of the steps taken to get the application running natively on Windows and Linux/macOS environments for local development.

## 1. Environment Configuration (`.env`)

The application expects a production-like environment by default (PostgreSQL, Redis). To run it locally without installing these external services, modify the `.env` file to use local development fallbacks:

- **Enable Development Mode:** Change `FLASK_ENV` from `production` to `development`. This disables the strict requirement for a `FLASK_SECRET_KEY` and allows the app to run using fallback insecure keys for local testing.
- **Switch to SQLite:** Comment out the PostgreSQL `DATABASE_URL` and replace it with `DATABASE_URL=sqlite:///community.db`. This tells SQLAlchemy to create a local `.db` file instead of trying to connect to a PostgreSQL instance.
- **Bypass Redis:** Comment out `REDIS_URL=redis://localhost:6379` and change it to `REDIS_URL=memory://`. This configures Flask-Limiter to use system memory for rate limiting, resolving any `ConnectionRefusedError` related to Redis.

## 2. Database Migrations

With the environment pointing to a fresh SQLite database, initialize it and create the tables.

### Windows (PowerShell)

```powershell
# Remove any existing migration history to start fresh
Remove-Item -Recurse -Force backend\migrations -ErrorAction SilentlyContinue

cd backend

# Initialize the migrations directory
..\.venv\Scripts\flask --app run:app db init

# Generate the initial migration script based on models
..\.venv\Scripts\flask --app run:app db migrate -m "init"

# Apply the migration to create the SQLite database and tables
..\.venv\Scripts\flask --app run:app db upgrade
```

### Linux / macOS (Bash)

```bash
# Remove any existing migration history to start fresh
rm -rf backend/migrations

cd backend

# Initialize the migrations directory
../.venv/bin/flask --app run:app db init

# Generate the initial migration script based on models
../.venv/bin/flask --app run:app db migrate -m "init"

# Apply the migration to create the SQLite database and tables
../.venv/bin/flask --app run:app db upgrade
```

## 3. Starting the Server

Finally, start the Flask development server:

### Windows (PowerShell)

```powershell
# Run the application using the virtual environment's python executable
.\.venv\Scripts\python.exe backend\run.py
```

### Linux / macOS (Bash)

```bash
# Run the application using the virtual environment's python executable
./.venv/bin/python backend/run.py
```

The application will be accessible at **http://127.0.0.1:5000**.
