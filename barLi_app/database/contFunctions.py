from functools import wraps
from flask import render_template, flash
from flask_login import current_user
from werkzeug.exceptions import abort


def admin_required(function):
    # Comprobamos si el usuario es administrador
    @wraps(function)
    def decorated_function(*args, **kwargs):
        is_admin = getattr(current_user, 'admin', False)
        if not is_admin:
            abort(403)
        return function(*args, **kwargs)

    return decorated_function


def check_password(password_1, password_2):
    # Comprobamos si las contraseñas pasan el filtro
    if password_1 is None or password_2 is None:
        return False
    if password_1 != password_2:
        flash('Las contraseñas no coinciden.', category='error')
        return False
    if password_1 == "" or len(password_1) < 9:
        flash('La contraseña debe tener más de 8 caracteres.', category='error')
        return False
    return True


def check_user(user):
    # Comprobamos si el usuario es válido
    if user is None:
        return False
    if user.user_email is None or user.user_password is None or user.user_fullname is None or \
            user.user_telephone is None or user.user_admin is None or user.user_birth is None or \
            user.user_district is None:
        flash('Por favor, rellena todos los campos.', category='error')
        return False
    if user.email == "" or len(user.email) < 5:
        flash('El correo debe tener más de 4 letras.', category='error')
        return False
    if user.user_fullname == "" or len(user.user_fullname) < 2:
        flash('El nombre debe tener más de 1 letra.', category='error')
        return False
    if user.user_telephone == "" or len(user.user_telephone) < 9 or len(user.user_telephone) > 9:
        flash('El número de teléfono debe tener 9 numeros.', category='error')
        return False
    return True


def check_bar(bar):
    # Comprobamos si el usuario es válido
    if bar is None:
        return False
    if bar.bar_email is None or bar.bar_password is None or bar.bar_fullname is None or \
            bar.bar_district is None or bar.bar_address is None:
        flash('Por favor, rellena todos los campos.', category='error')
        return False
    if bar.bar_email == "" or len(bar.bar_email) < 5:
        flash('El correo debe tener más de 4 letras.', category='error')
        return False
    if bar.bar_fullname == "" or len(bar.bar_fullname) < 2:
        flash('El nombre debe tener más de 1 letra.', category='error')
        return False
    return True


def check_add(add):
    # Comprobamos si el anunciante es válido
    if add is None:
        return False
    if add.add_email is None or add.add_password is None or add.add_fullname is None or \
            add.add_quantity is None or add.add_address is None:
        flash('Por favor, rellena todos los campos.', category='error')
        return False
    if add.add_email == "" or len(add.add_email) < 4:
        flash('El correo debe tener más de 3 caracteres.', category='error')
        return False
    if add.add_fullname == "" or len(add.add_fullname) < 2:
        flash('El nombre debe tener más de 1 letra.', category='error')
        return False
    return True
