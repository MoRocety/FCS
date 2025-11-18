from flask import Flask
from views import my_blueprint
import os
from pathlib import Path

# Load environment variables from .env file if it exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    print(f"Loading environment from: {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                # Split on first = only
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"  Set: {key.strip()}")
else:
    print("No .env file found, using system environment variables")

# Create the Flask application instance
app = Flask(__name__)

# Configure the Flask app
app.config['SECRET_KEY'] = 'your_secret_key'

# Register blueprints
app.register_blueprint(my_blueprint)

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
