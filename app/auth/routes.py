from . import auth
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            print("User found:", user.email)
            if user.check_password(form.password.data):
                print("Password correct")
                login_user(user)
                flash('Logged in successfully.', 'success')

                # Redirect based on user role
                if user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user.role == 'supplier':
                    return redirect(url_for('supplier.dashboard'))
                else:
                    return redirect(url_for('auth.login'))  # Fallback in case of undefined role
            else:
                print("Password incorrect")
        else:
            print("User not found")
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegistrationForm()
        print("Form loaded successfully.")
        
        if form.validate_on_submit():
            print("Form validated successfully.")
            
            # Log form data for debugging purposes
            print(f"Form data: email={form.email.data}, company_name={form.company_name.data}, address={form.address.data}, phone_number={form.phone_number.data}, category={form.category.data}")
            
            # Set the role to 'supplier' by default
            role = 'supplier'  # Default role
            if hasattr(form, 'role') and form.role.data:  # If the form has a role field, use it
                role = form.role.data
            
            # Create the new user with the default or provided role
            new_user = User(
                email=form.email.data,
                company_name=form.company_name.data,
                address=form.address.data,
                phone_number=form.phone_number.data,
                category=form.category.data,
                role=role  # Set role to 'supplier' by default
            )
            
            # Set the hashed password
            new_user.set_password(form.password.data)
            print("Password hashed and set.")
            
            # Add the user to the database
            db.session.add(new_user)
            db.session.commit()
            print("New user committed to the database.")
            
            flash('Registration successful.', 'success')
            return redirect(url_for('auth.login'))
        else:
            print("Form validation failed.")
            print(form.errors)  # Print out form validation errors for debugging
            
    except Exception as e:
        # Catch any exceptions and print them to the console
        print(f"An error occurred during registration: {str(e)}")

    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
