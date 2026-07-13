from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Courier
from config import Config
import os
import random
import smtplib

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Ensure database tables and upload folders are created
with app.app_context():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Email Helper
def send_verification_email(to_email, code):
    try:
        server = smtplib.SMTP(app.config.get('MAIL_SERVER'), app.config.get('MAIL_PORT'))
        server.starttls()
        server.login(app.config.get('MAIL_USERNAME'), app.config.get('MAIL_PASSWORD'))
        
        subject = "Courier Management System - Password Reset Code"
        body = f"Your 6-digit verification code is: {code}"
        message = f"Subject: {subject}\n\n{body}"
        
        server.sendmail(app.config.get('MAIL_USERNAME'), to_email, message)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False



# Home
@app.route('/')
def index():
    return render_template('index.html')


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Check if email already exists
        existing_user = User.query.filter_by(email=request.form['email']).first()
        if existing_user:
            flash("Email address already registered!", "danger")
            return redirect(url_for('register'))
            
        user = User(
            name=request.form['name'], 
            email=request.form['email'], 
            password=request.form['password']
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash("Logged in successfully!", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials!", "danger")
        return redirect(url_for('login'))
    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))


# Forgot Password
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Generate 6-digit random code
            code = str(random.randint(100000, 999999))
            session['reset_code'] = code
            session['reset_email'] = email
            
            # Attempt to send email
            success = send_verification_email(email, code)
            if success:
                flash("A 6-digit verification code has been sent to your email.", "success")
            else:
                flash("Failed to send verification email. Developer simulation mode enabled.", "info")
            return redirect(url_for('verify_code'))
        else:
            flash("Email address not found!", "danger")
            return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')


# Verify Code
@app.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    if not session.get('reset_email') or not session.get('reset_code'):
        flash("Please start the password reset process first.", "danger")
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        code = request.form['code']
        if code == session.get('reset_code'):
            session['reset_verified'] = True
            flash("Code verified! Please set your new password.", "success")
            return redirect(url_for('reset_password'))
        flash("Invalid verification code! Please try again.", "danger")
        return redirect(url_for('verify_code'))
    return render_template('verify_code.html')


# Reset Password
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('reset_verified') or not session.get('reset_email'):
        flash("Please verify your reset code first.", "danger")
        return redirect(url_for('forgot_password'))
        
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('reset_password'))
            
        user = User.query.filter_by(email=session.get('reset_email')).first()
        if user:
            user.password = password
            db.session.commit()
            
            # Clean up session keys
            session.pop('reset_code', None)
            session.pop('reset_email', None)
            session.pop('reset_verified', None)
            
            flash("Your password has been reset successfully! Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("User not found.", "danger")
            return redirect(url_for('forgot_password'))
            
    return render_template('reset_password.html')


# Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        flash("Please log in to access the dashboard.", "danger")
        return redirect(url_for('login'))
        
    search_query = request.args.get('search', '')
    if search_query:
        couriers = Courier.query.filter(
            (Courier.sender.like(f"%{search_query}%")) | 
            (Courier.receiver.like(f"%{search_query}%"))
        ).all()
    else:
        couriers = Courier.query.all()
    return render_template('dashboard.html', couriers=couriers)


# Add Courier
@app.route('/add-courier', methods=['GET', 'POST'])
def add_courier():
    if not session.get('user_id'):
        flash("Please log in to add a courier.", "danger")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
        courier = Courier(
            sender=request.form['sender'],
            receiver=request.form['receiver'],
            parcel_type=request.form['parcel_type'],
            weight=float(request.form['weight']),
            charges=float(request.form['charges']),
            address=request.form['address'],
            address_2=request.form.get('address_2', ''),
            status=request.form.get('status', 'Pending'),
            image=filename
        )
        db.session.add(courier)
        db.session.commit()
        flash("Courier added successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('courier.html', courier=None)


# Edit Courier
@app.route('/edit-courier/<int:id>', methods=['GET', 'POST'])
def edit_courier(id):
    if not session.get('user_id'):
        flash("Please log in to edit a courier.", "danger")
        return redirect(url_for('login'))
        
    courier = Courier.query.get_or_404(id)
    if request.method == 'POST':
        courier.sender = request.form['sender']
        courier.receiver = request.form['receiver']
        courier.parcel_type = request.form['parcel_type']
        courier.weight = float(request.form['weight'])
        courier.charges = float(request.form['charges'])
        courier.address = request.form['address']
        courier.address_2 = request.form.get('address_2', '')
        courier.status = request.form['status']
        
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                courier.image = filename
                
        db.session.commit()
        flash("Courier updated successfully!", "success")
        return redirect(url_for('dashboard'))
    return render_template('courier.html', courier=courier)


# Delete Courier
@app.route('/delete-courier/<int:id>')
def delete_courier(id):
    if not session.get('user_id'):
        flash("Please log in to delete a courier.", "danger")
        return redirect(url_for('login'))
        
    courier = Courier.query.get_or_404(id)
    db.session.delete(courier)
    db.session.commit()
    flash("Courier deleted successfully!", "danger")
    return redirect(url_for('dashboard'))


# Tracking Search
@app.route('/track')
def track_search():
    tracking_id = request.args.get('id')
    courier = None
    if tracking_id:
        try:
            courier = db.session.get(Courier, int(tracking_id))
        except ValueError:
            pass
    return render_template('tracking.html', courier=courier, tracking_id=tracking_id)


# Tracking Details
@app.route('/track-details/<int:id>')
def track_details(id):
    return redirect(url_for('track_search', id=id))


if __name__ == '__main__':
    app.run(debug=True)
