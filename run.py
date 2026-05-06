from app import create_app
import os

# Load .env variables before creating app
if os.path.exists('.env'):
    with open('.env') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
