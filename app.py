from flask import Flask
from views import my_blueprint

# Create the Flask application instance
app = Flask(__name__)

# Configure the Flask app
app.config['SECRET_KEY'] = 'your_secret_key'

# Register blueprints
app.register_blueprint(my_blueprint)

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)

