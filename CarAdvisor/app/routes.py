# Import necessary modules and functions from Flask
from flask import Flask, Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
import sqlite3
import hashlib

# Import custom functionalities from the 'utils' module
from CarAdvisor.utils.carRecommendation import recommended_cars
from CarAdvisor.utils.pricePrediction import price_prediction

# Create a Blueprint to organize routes and views
main_bp = Blueprint('main', __name__, static_folder='static', template_folder='templates')

# Function to create the Flask application instance
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = '8sdf8932hjksdf!@#$%^&*()_+'

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Define a User class for Flask-Login
    class User(UserMixin):
        def __init__(self, user_id, username, is_admin = False):
            self.id = user_id
            self.username = username
            self.is_admin = is_admin

    # Database connection function
    def get_db_connection():
        conn = sqlite3.connect('mainDB.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    # User loader function required by Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE userid = ?", (user_id,))
        user_data = cursor.fetchone()
        conn.close()
        if user_data:
            return User(user_data['userid'], user_data['username'], user_data['is_admin'])
        return None
    
    # Decorator to restrict access to admin routes
    def admin_required(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_admin:
                return render_template('unauthorized.html')
            return view(*args, **kwargs)
        return wrapped_view
    
    # admin route
    @main_bp.route('/dashboard')
    @login_required
    @admin_required
    def admin_dashboard():
        users = get_user_list()
        return render_template('admin_dashboard.html', users = users)
    
    # user deletion
    @main_bp.route('/admin/delete-user/<int:user_id>', methods=['POST'])
    @login_required
    @admin_required
    def delete_user(user_id):
        # Delete the user from the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE userid = ?", (user_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('main.admin_dashboard'))
    
    # get user list
    def get_user_list():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        conn.close()
        return users
    
    # user registration
    @main_bp.route('/register', methods=['GET', 'POST'])
    def user_register():
        if request.method == 'POST':
            fullname = request.form['fullname']
            email = request.form['email']
            username = request.form['username'].lower()
            password = hashlib.sha256(request.form['password'].encode()).hexdigest()

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (email, name, username, password) VALUES (?, ?, ?, ?)", (email, fullname, username, password))
                conn.commit()
                conn.close()
                return render_template('user_register.html', success_message='Account Created Successfully!')
            except sqlite3.IntegrityError:
                conn.close()
                return render_template('user_register.html', error_message='Username or email already exists!')

        return render_template('user_register.html')
    
    # user login
    @main_bp.route('/login', methods=['GET', 'POST'])
    def user_login():
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = hashlib.sha256(request.form['password'].encode()).hexdigest()

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                user_obj = User(user['userid'], user['username'], user['is_admin'])
                login_user(user_obj)

                if user['is_admin']==1:
                    return redirect(url_for('main.admin_dashboard'))
                return redirect(url_for('main.home'))
            else:
                return render_template('user_login.html', error_message='Invalid username or password')

        return render_template('user_login.html')
    
    # Logout
    @main_bp.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('main.home'))


    # Home Page
    @main_bp.route('/')
    def home():
        return render_template('index.html')
    
    # Car recommendation
    @main_bp.route('/recommend', methods=['GET', 'POST'])
    @login_required
    def recommend_cars():
        error_message = None
        if request.method == 'POST':
            features = [request.form.get(feature) for feature in ['made', 'color_group', 'type_group', 'price_range', 'transmission']]
            features[1] = features[1].lower()
            features[4] = features[4].lower()
            features[3] = tuple(map(int, features[3].split('-')))
            try:
                cars = recommended_cars(tuple(features))
            except Exception as e:
                error_message = "Invalid input!"
            if error_message:
                return render_template('recommend.html', error_message = error_message)
            else:
                return render_template('recommend.html',cars = cars, features = features)
        return render_template('recommend.html')
    
    # Car price prediction
    @main_bp.route('/predict', methods=['GET', 'POST'])
    @login_required
    def predict_price():
        error_message = None
        if request.method == 'POST':
            features = [request.form.get(feature) for feature in ['year', 'odometer', 'cylinders', 'manufacturer', 'model', 'fuel', 'title_status', 'transmission', 'condition', 'drive', 'type']]
            try:
                predicted_price = price_prediction(features)
            except Exception as e:
                error_message = f"Error: {e}"
            if error_message:
                return render_template('predict.html', error_message = error_message)
            else:
                return render_template('predict.html', predicted_price = predicted_price)
        return render_template('predict.html')
    
    # User feedback for car recommendation
    @main_bp.route('/feedback', methods = ['POST'])
    @login_required
    def feedback_rating():
        if request.method == 'POST':
            rating = int(request.form['inlineRadioOptions'])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO rec_ratings (ratings) VALUES (?)", (rating,))
            conn.commit()
            cur.close()
        return render_template('recommend.html', rating = rating)
    
    # count feedback rating
    @main_bp.route('/rating-count')
    @login_required
    def rating_count():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT ratings FROM rec_ratings")
        ratings = cur.fetchall()
        ratings_count = {}
        for rating in ratings:
            rating = rating[0]
            if rating in ratings_count:
                ratings_count[rating] += 1
            else:
                ratings_count[rating] = 1
        return jsonify(ratings_count)
        
    # show privacy policy page
    @main_bp.route('/privacy-policy')
    def privacy():
        return render_template('privacy_policy.html')

    # show terms and conditions page
    @main_bp.route('/terms-and-conditions')
    def terms():
        return render_template('terms_conditions.html')
    
    # Return the Flask app instance
    return app