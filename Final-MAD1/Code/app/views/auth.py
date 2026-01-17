from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  
from app.models import User  
from app.forms import RegistrationForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'Admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'Sponsor':
            return redirect(url_for('sponsor.dashboard'))
        elif current_user.role == 'Influencer':
            return redirect(url_for('influencer.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data,
                    password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'sponsor':
            return redirect(url_for('sponsor.dashboard'))
        elif current_user.role == 'influencer':
            return redirect(url_for('influencer.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')

            # Check if there was a 'next' argument in the query string, which Flask-Login uses
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Redirect based on role after login
            if user.role == 'Admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'Sponsor':
                return redirect(url_for('sponsor.dashboard'))
            elif user.role == 'Influencer':
                return redirect(url_for('influencer.dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/test')
def test():
    return render_template('test.html')
