from flask import render_template, redirect, request, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
import traceback
import sys
from . import auth
from .. import db
from ..models.user import User
from .forms import LoginForm, RegistrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    print(">>> Login function called", file=sys.stderr)
    if current_user.is_authenticated:
        print(">>> User already authenticated, redirecting to index", file=sys.stderr)
        return redirect(url_for('main.index'))

    form = LoginForm()
    print(f">>> Login request method: {request.method}", file=sys.stderr)

    if form.validate_on_submit():
        print(f">>> Form validated, email: {form.email.data}", file=sys.stderr)

        user = User.query.filter_by(email=form.email.data).first()
        print(f">>> User found: {user}", file=sys.stderr)

        if user is not None:
            print(f">>> User exists, checking password", file=sys.stderr)
            password_correct = user.verify_password(form.password.data)
            print(f">>> Password correct: {password_correct}", file=sys.stderr)
            print(f">>> Password hash: {user.password_hash}", file=sys.stderr)

            if password_correct:
                login_user(user, form.remember_me.data)
                print(f">>> User logged in successfully", file=sys.stderr)
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('main.index')
                return redirect(next)

        print(">>> Invalid email or password", file=sys.stderr)
        flash('Неверный email или пароль')
    elif request.method == 'POST':
        print(f">>> Form validation failed. Errors: {form.errors}", file=sys.stderr)

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    print(">>> Register function called", file=sys.stderr)
    if current_user.is_authenticated:
        print(">>> User already authenticated, redirecting to index", file=sys.stderr)
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    print(f">>> Register request method: {request.method}", file=sys.stderr)

    if form.validate_on_submit():
        print(">>> Form validated successfully", file=sys.stderr)
        try:
            print(f">>> Creating user with email: {form.email.data}", file=sys.stderr)
            print(f">>> First name: {form.first_name.data}", file=sys.stderr)
            print(f">>> Last name: {form.last_name.data}", file=sys.stderr)

            user = User(
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.password = form.password.data
            print(f">>> Password hash generated: {user.password_hash}", file=sys.stderr)

            print(">>> Adding user to session", file=sys.stderr)
            db.session.add(user)

            print(">>> Committing session", file=sys.stderr)
            db.session.commit()

            print(">>> User created successfully with ID: {user.id}", file=sys.stderr)
            flash('Регистрация успешно завершена! Теперь вы можете войти.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            print(f">>> Error creating user: {str(e)}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            flash('Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.')
    elif request.method == 'POST':
        print(f">>> Form validation failed. Errors: {form.errors}", file=sys.stderr)

    return render_template('auth/register.html', form=form)
