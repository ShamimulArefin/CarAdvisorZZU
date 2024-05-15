# Import the 'app' object from the 'CarAdvisor.app' module
# This assumes that there is a Flask application instance named 'app' in the 'CarAdvisor.app' module
from CarAdvisor.app import app

# Entry point of the application when this script is executed
if __name__ == '__main__':
    # Run the Flask application in debug mode
    # Debug mode enables features like automatic code reloading and detailed error messages
    app.run(debug=True)
