from flask import jsonify, request, Blueprint, flash, redirect, url_for, session, make_response
from flask_login import login_required, current_user
from barLi_app.utils.db import db
from barLi_app.database.models import User, Bar, Advertiser, Table, Book, City, District
from barLi_app.database.contFunctions import admin_required, check_password, check_user, check_bar, check_add

# check_supplier, check_manga, check_address, array_merge


controller = Blueprint('controller', __name__)


# Crear usuario
@login_required
@admin_required
@controller.route('/api/user', methods=['POST'])
def create_user():
    # Aquí recogemos del formulario del front los valores y hacemos las comprobaciones

    user_fullname = request.json('user_fullname')

    user_password = request.json('user_password')

    user_password_repeat = request.json('user_password_repeat')

    user_email = request.json('user_email')

    user_telephone = request.json('user_telephone')

    user_admin = request.json('user_admin')

    user_birth = request.json('user_birth')

    user_district = request.json('user_district')

    # Aquí creamos una variable Usuario a través del email recogido
    user = User.query.filter_by(user_email=user_email).first()

    # Comprobamos si la contraseña es mayor de 8 carácteres y coincide con la repeat,sino es así lo mostramos
    if not check_password(user_password, user_password_repeat):
        error_msg = {'error': 'La contraseña no es válida'}
        return make_response(jsonify(error_msg), 400)
    else:
        # Creamos el objeto User si hemos pasado los filtros anteriores
        new_user = User(user_fullname=user_fullname, user_password=user_password, user_email=user_email,
                        user_telephone=user_telephone,
                        user_admin=user_admin, user_birth=user_birth, user_district=user_district)

    # Checkeamos la variable usuario creada previamente
    # Primero tratamos el caso de que ya exista,
    # despues de que los datos no sean compatibles y por ultimo el caso correcto
    if user:
        flash('Ya existe un usuario con este correo.', category='error')
    elif not check_user(new_user):
        error_msg = {'error': 'El usuario ingresado no cumple los requisitos'}
        return make_response(jsonify(error_msg), 400)
    else:
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Usuario creado correctamente.', category='success')
        except Exception as error:
            flash('Error al crear el usuario.', category='error')
            print(error)
            error_msg = {'error': 'El usuario ingresado no cumple los requisitos'}
            return make_response(jsonify(error_msg), 500)
        return new_user


# Obtener usuario
@login_required
@admin_required
@controller.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    # Obtenemos el usuario por su primary key
    user = User.query.filter_by(id=user_id).first()
    # Si encuentra el usuario lo devuelve si no devuelve un error
    if user:
        return user
    else:
        return jsonify({"error": "Usuario no encontrado"}), 500


# Obtener usuarios
@login_required
@admin_required
@controller.route('/api/user', methods=['GET'])
def get_users():
    # Obtener todos los usuarios de la base de datos
    users = User.query.order_by(User.user_id.desc()).all()
    # Devuelve la totalidad de los usuarios,si no hubiera ninguno devuelve un error
    if users:
        return jsonify(users), 200
    else:
        return jsonify({"error": "No hay usuarios en la base de datos"}), 404


# Modificar el usuario
@login_required
@admin_required
@controller.route('/api/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    # Obtener el usuario el cual queramos modificar
    user = User.query.filter_by(id=user_id).first()

    # Si lo obtiene, recogemos los valores del front
    if user:
        user_fullname = request.json('user_fullname')

        user_password = request.json('user_password')

        user_password_repeat = request.json('user_password_repeat')

        user_email = request.json('user_email')

        user_telephone = request.json('user_telephone')

        user_admin = request.json('user_admin')

        user_birth = request.json('user_birth')

        user_district = request.json('user_district')

        # Comprobamos si la contraseña es mayor de 8 carácteres y coincide con la repeat,sino es así lo mostramos
        if not check_password(user_password, user_password_repeat):
            error_msg = {'error': 'La contraseña no es válida'}
            return make_response(jsonify(error_msg), 400)
        else:
            # creamos el usuario que sobreescribira los datos del anterior
            mod_user = User(user_fullname=user_fullname, user_password=user_password, user_email=user_email,
                            user_telephone=user_telephone,
                            user_admin=user_admin, user_birth=user_birth, user_district=user_district)
        # Si los datos introducidos pasan el filtro, se sobreescribira el usuario
        if not check_user(mod_user):
            error_msg = {'error': 'Los datos introducidos no son válidos'}
            return make_response(jsonify(error_msg), 400)
        else:
            try:
                user.user_fullname = user.user_fullname
                user.user_email = user_email
                user.user_password = user.user_password
                user.user_telephone = user_telephone
                user.user_admin = user_admin
                user.user_birth = user_birth
                user.user_district = user_district

                db.session.commit()
                flash('Usuario modificado.', category='success')

                return user
            # Tratamos el error en la modificacion
            except Exception as error:
                flash('Error al modificar el usuario.', category='error')
                print(error)
                error_msg = {'error': 'El usuario no se ha podido modificar'}
                return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'El usuario no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Borrar el usuario
@login_required
@admin_required
@controller.route('/api/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Buscamos el usuario el cual queremos borrar de la base de datos
    user = User.query.filter_by(id=user_id).first()

    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            flash('Usuario eliminado correctamente.', category='success')

            return jsonify({"message": "El usuario ha sido borrado"}), 200
        except Exception as error:
            flash('Error al eliminar el usuario.', category='error')
            print(error)

            error_msg = {'error': 'El usuario no ha sido borrado'}
            return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'El usuario no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Creamos un bar
@login_required
@admin_required
@controller.route('/api/bar', methods=['POST'])
def create_bar():
    # Aquí recogemos del formulario del front los valores y hacemos las comprobaciones

    bar_fullname = request.json('bar_fullname')

    bar_password = request.json('bar_password')

    bar_password_repeat = request.json('bar_password_repeat')

    bar_email = request.json('bar_email')

    bar_address = request.json('bar_address')

    bar_district = request.json('bar_district')

    # Aquí creamos una variable Bar a través del email recogido
    bar = Bar.query.filter_by(bar_email=bar_email).first()

    # Comprobamos si la contraseña es mayor de 8 carácteres y coincide con la repeat,sino es así lo mostramos
    if not check_password(bar_password, bar_password_repeat):
        error_msg = {'error': 'La contraseña no es válida'}
        return make_response(jsonify(error_msg), 400)
    else:
        # Creamos el objeto Bar si hemos pasado los filtros anteriores
        new_bar = Bar(bar_fullname=bar_fullname, bar_password=bar_password, bar_email=bar_email, bar_address=bar_address
                      , bar_district=bar_district)

    # Checkeamos la variable bar creada previamente
    # Primero tratamos el caso de que ya exista, despues de que los datos no sean compatibles
    # y por ultimo el caso correcto
    if bar:
        flash('Ya existe un bar con este correo electrónico.', category='error')
    elif not check_bar(new_bar):
        error_msg = {'error': 'El usuario ingresado no cumple los requisitos'}
        return make_response(jsonify(error_msg), 400)
    else:
        try:
            db.session.add(new_bar)
            db.session.commit()
            flash('Bar creado correctamente.', category='success')
        except Exception as error:
            flash('Error al crear el bar.', category='error')
            print(error)
            error_msg = {'error': 'El bar ingresado no cumple los requisitos'}
            return make_response(jsonify(error_msg), 500)
        return new_bar


# Obtener un bar
@login_required
@admin_required
@controller.route('/api/bar/<supplier_id>', methods=['GET'])
def get_bar(bar_id):

    bar = Bar.query.filter_by(id=bar_id).first()

    if bar:
        return bar
    else:
        return jsonify({"error": "Supplier not found"}), 404


# Obtener todos los bares
@login_required
@admin_required
@controller.route('/api/bar', methods=['GET'])
def get_bars():
    suppliers = Bar.query.order_by(Bar.name.desc()).all()

    if suppliers:
        return jsonify(suppliers), 200
    else:
        return jsonify({"error": "No suppliers found"}), 404


# Modificar un bar
@login_required
@admin_required
@controller.route('/api/bar/<bar_id>', methods=['PUT'])
def update_bar(bar_id):
    # Obtener el bar el cual queramos modificar
    bar = Bar.query.filter_by(id=bar_id).first()

    # Si lo obtiene, recogemos los valores del front
    if bar:
        bar_fullname = request.json('bar_fullname')

        bar_password = request.json('bar_password')

        bar_password_repeat = request.json('bar_password_repeat')

        bar_email = request.json('bar_email')

        bar_address = request.json('bar_address')

        bar_district = request.json('bar_district')

        # Comprobamos si la contraseña es mayor de 8 carácteres y coincide con la repeat,sino es así lo mostramos
        if not check_password(bar_password, bar_password_repeat):
            error_msg = {'error': 'La contraseña no es válida'}
            return make_response(jsonify(error_msg), 400)
        else:
            # creamos el bar que sobreescribira los datos del anterior
            mod_bar = Bar(bar_fullname=bar_fullname, bar_password=bar_password, bar_email=bar_email,
                          bar_address=bar_address, bar_district=bar_district)
        # Si los datos introducidos pasan el filtro, se sobreescribira el bar
        if not check_bar(mod_bar):
            error_msg = {'error': 'Los datos introducidos no son válidos'}
            return make_response(jsonify(error_msg), 400)
        else:
            try:
                bar.bar_fullname = bar.bar_fullname
                bar.bar_address = bar.bar_addres
                bar.bar_email = bar.bar_email
                bar.bar_password = bar.bar_password
                bar.bar_district = bar.bar_district

                db.session.commit()
                flash('Bar modificado.', category='success')

                return bar
            # Tratamos el error en la modificacion
            except Exception as error:
                flash('Error al modificar el bar.', category='error')
                print(error)
                error_msg = {'error': 'El bar no se ha podido modificado'}
                return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'El bar no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Borrar el bar
@login_required
@admin_required
@controller.route('/api/bar/<bar_id>', methods=['DELETE'])
def delete_bar(bar_id):
    # Buscamos el bar el cual queremos borrar de la base de datos
    bar = Bar.query.filter_by(id=bar_id).first()

    if bar:
        try:
            db.session.delete(bar)
            db.session.commit()
            flash('Bar eliminado correctamente.', category='success')

            return jsonify({"message": "El bar ha sido borrado"}), 200
        except Exception as error:
            flash('Error al eliminar el bar.', category='error')
            print(error)

            error_msg = {'error': 'El bar no ha sido borrado'}
            return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'El bar no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Creamos una anunciante
@login_required
@admin_required
@controller.route('/api/advertiser', methods=['POST'])
def create_advertiser():
    # Aquí recogemos del formulario del front los valores y hacemos las comprobaciones

    add_fullname = request.json('add_fullname')

    add_quantity = request.json('add_quantity')

    add_img = request.json('add_img')

    add_email = request.json('add_email')

    add_password = request.json('add_password')

    add_password_repeat = request.json('add_password_repeat')

    add_district = request.json('add_district')

    # Aquí creamos una variable Advertiser a través del nombre recogido
    add = Advertiser.query.filter_by(add_fullname=add_fullname).first()

    # Comprobamos si la contraseña es mayor de 8 carácteres y coincide con la repeat,sino es así lo mostramos
    if not check_password(add_password, add_password_repeat):
        error_msg = {'error': 'La contraseña no es válida'}
        return make_response(jsonify(error_msg), 400)
    else:
        # Creamos un objeto Advertiser si hemos pasado los filtros anteriores
        new_add = Advertiser(add_fullname=add_fullname, add_password=add_password, add_email=add_email,
                             add_quantity=add_quantity, add_img=add_img, add_district=add_district)

    # Checkeamos la variable Advertiser creada previamente
    # Primero tratamos el caso de que ya exista,
    # despues de que los datos no sean compatibles y por ultimo el caso correcto
    if add:
        flash('Ya existe un Anunciante con ete nombre.', category='error')
    elif not check_add(new_add):
        error_msg = {'error': 'El anunciante ingresado no cumple los requisitos'}
        return make_response(jsonify(error_msg), 400)
    else:
        try:
            db.session.add(new_add)
            db.session.commit()
            flash('Anunciante creado correctamente.', category='success')
        except Exception as error:
            flash('Error al crear el Anunciante.', category='error')
            print(error)
            error_msg = {'error': 'El anunciante ingresado no cumple los requisitos'}
            return make_response(jsonify(error_msg), 500)
        return new_add


# Obtener anunciante
@login_required
@admin_required
@controller.route('/api/advertiser/<add_fullname>', methods=['GET'])
def get_add(add_fullname):
    # Obtenemos el advertiser por su primary key
    add = User.query.filter_by(fullname=add_fullname).first()
    # Si encuentra el usuario lo devuelve si no devuelve un error
    if add:
        return add
    else:
        return jsonify({"error": "Anunciante no encontrado"}), 500


# Obtener usuarios
@login_required
@admin_required
@controller.route('/api/advertiser', methods=['GET'])
def get_adds():
    # Obtener todos los anunciantes de la base de datos
    adds = Advertiser.query.order_by(Advertiser.add_fullname.desc()).all()
    # Devuelve la totalidad de los usuarios,si no hubiera ninguno devuelve un error
    if adds:
        return jsonify(adds), 200
    else:
        return jsonify({"error": "No hay anunciantes en la base de datos"}), 404


# Modificar un anunciante
@login_required
@admin_required
@controller.route('/api/advertiser/<add_fullname>', methods=['PUT'])
def update_add(add_fullname):
    # Obtener el anunciante el cual queramos modificar
    add = Advertiser.query.filter_by(fullname=add_fullname).first()

    # Si lo obtiene, recogemos los valores del front
    if add:
        add_fullname = request.json('add_fullname')

        add_password = request.json('add_password')

        add_password_repeat = request.json('add_password_repeat')

        add_email = request.json('add_email')

        add_img = request.json('add_img')

        add_quantity = request.json('add_quantity')

        add_district = request.json('add_district')

        # Comprobamos si la contraseña es mayor de 8 carácteres y coincide con la repeat,sino es así lo mostramos
        if not check_password(add_password, add_password_repeat):
            error_msg = {'error': 'La contraseña no es válida'}
            return make_response(jsonify(error_msg), 400)
        else:
            # creamos el avertiser que sobreescribira los datos del anterior
            mod_add = Advertiser(add_fullname=add_fullname, add_password=add_password, add_email=add_email,
                                 add_quantity=add_quantity, add_district=add_district, add_img=add_img)
        # Si los datos introducidos pasan el filtro, se sobreescribira el bar
        if not check_add(mod_add):
            error_msg = {'error': 'Los datos introducidos no son válidos'}
            return make_response(jsonify(error_msg), 400)
        else:
            try:
                add.add_fullname = add.add_fullname
                add.add_password = add.add_password
                add.add_email = add.add_email
                add.add_quantity = add.add_quantity
                add.add_district = add.add_district

                db.session.commit()
                flash('Anunciante modificado.', category='success')

                return add
            # Tratamos el error en la modificacion
            except Exception as error:
                flash('Error al modificar el Anunciante.', category='error')
                print(error)
                error_msg = {'error': 'El Anunciante no se ha podido modificado'}
                return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'El Anunciante no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Borrar el Anunciante
@login_required
@admin_required
@controller.route('/api/advertiser/<add_fullname>', methods=['DELETE'])
def delete_add(add_fullname):
    # Buscamos el Anunciante el cual queremos borrar de la base de datos
    add = Advertiser.query.filter_by(fullname=add_fullname).first()

    if add:
        try:
            db.session.delete(add)
            db.session.commit()
            flash('Anunciante eliminado correctamente.', category='success')

            return jsonify({"message": "El Anunciante ha sido borrado"}), 200
        except Exception as error:
            flash('Error al eliminar el Anunciante.', category='error')
            print(error)
            error_msg = {'error': 'El Anunciante no ha sido borrado'}
            return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'El Anunciante no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Creamos una mesa
@login_required
@admin_required
@controller.route('/api/table', methods=['POST'])
def create_table():
    # Aquí recogemos del formulario del front los valores y hacemos las comprobaciones

    table_seat_num = request.json('table_seat_num')

    table_bar = request.json('table_bar')

    table_inside = request.json('table_inside')

    table_state = request.json('table_state')

    # Creamos el objeto Mesa si hemos pasado los filtros anteriores
    new_table = Table(table_seat_num=table_seat_num, table_bar=table_bar, table_inside=table_inside,
                      table_state=table_state)

    try:
        db.session.add(new_table)
        db.session.commit()
        flash('Mesa creada correctamente.', category='success')
    except Exception as error:
        flash('Error al crear la mesa.', category='error')
        print(error)
        error_msg = {'error': 'La mesa ingresada no cumple los requisitos'}
        return make_response(jsonify(error_msg), 500)
    return new_table


# Obtener una mesa
@login_required
@admin_required
@controller.route('/api/table/<table_id>', methods=['GET'])
def get_table(table_id):

    table = Table.query.filter_by(id=table_id).first()

    if table:
        return table
    else:
        return jsonify({"error": "Table not found"}), 404


# Obtener todoas las mesas
@login_required
@admin_required
@controller.route('/api/table', methods=['GET'])
def get_tables():
    tables = Table.query.order_by(Table.id.desc()).all()

    if tables:
        return jsonify(tables), 200
    else:
        return jsonify({"error": "No tables found"}), 404


# Modificar una mesa
@login_required
@admin_required
@controller.route('/api/table/<table_id>', methods=['PUT'])
def update_table(table_id):
    # Obtener el bar el cual queramos modificar
    table = Table.query.filter_by(id=table_id).first()

    # Si lo obtiene, recogemos los valores del front
    if table:
        table_seat_num = request.json('table_seat_num')

        table_bar = request.json('table_bar')

        table_inside = request.json('table_inside')

        table_state = request.json('table_state')

        # creamos la mesa que sobreescribira los datos del anterior
        mod_table = Table(table_seat_num=table_seat_num, table_bar=table_bar, table_inside=table_inside,
                          table_state=table_state)
        # Si los datos introducidos pasan el filtro, se sobreescribira el bar
        try:
            table.table_seat_num = table.table_seat_num
            table.table_bar = table.table_bar
            table.table_inside = table.table_inside
            table.table_state = table.table_state
            db.session.commit()
            flash('Mesa modificada.', category='success')
            return table
            # Tratamos el error en la modificacion
        except Exception as error:
            flash('Error al modificar la mesa.', category='error')
            print(error)
            error_msg = {'error': 'La mesa no se ha podido modificado'}
            return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'La mesa no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Borrar la mesa
@login_required
@admin_required
@controller.route('/api/table/<table_id>', methods=['DELETE'])
def delete_table(table_id):
    # Buscamos la mesa la cual queremos borrar de la base de datos
    table = Table.query.filter_by(id=table_id).first()

    if table:
        try:
            db.session.delete(table)
            db.session.commit()
            flash('Mesa eliminada correctamente.', category='success')

            return jsonify({"message": "La mesa ha sido borrado"}), 200
        except Exception as error:
            flash('Error al eliminar la mesa.', category='error')
            print(error)
            error_msg = {'error': 'La mesa no ha sido borrada'}
            return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'La mesa no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Creamos una reserva
@login_required
@admin_required
@controller.route('/api/book', methods=['POST'])
def create_book():
    # Aquí recogemos del formulario del front los valores y hacemos las comprobaciones

    book_user = request.json('book_user')

    book_table = request.json('book_table')

    book_bar = request.json('book_bar')

    book_expiration = request.json('book_expiration')

    book_completed = request.json('book_completed')

    # Creamos el objeto Reserva si hemos pasado los filtros anteriores
    new_book = Book(book_user=book_user, book_table=book_table, book_bar=book_bar, book_expiration=book_expiration,
                    book_completed=book_completed)

    try:
        db.session.add(new_book)
        db.session.commit()
        flash('Reserva creada correctamente.', category='success')
    except Exception as error:
        flash('Error al crear la reserva.', category='error')
        print(error)
        error_msg = {'error': 'La reserva ingresada no cumple los requisitos'}
        return make_response(jsonify(error_msg), 500)
    return new_book


# Obtener todos las mesas
@login_required
@admin_required
@controller.route('/api/book', methods=['GET'])
def get_books():
    books = Book.query.order_by(Book.id.desc()).all()

    if books:
        return jsonify(books), 200
    else:
        return jsonify({"error": "No books found"}), 404


# Modificar una reserva
@login_required
@admin_required
@controller.route('/api/book/<book_id>', methods=['PUT'])
def update_book(book_id):
    # Obtener el bar el cual queramos modificar
    book = Book.query.filter_by(id=book_id).first()

    # Si lo obtiene, recogemos los valores del front
    if book:
        book_user = request.json('book_user')

        book_table = request.json('book_table')

        book_bar = request.json('book_bar')

        book_expiration = request.json('book_expiration')

        book_completed = request.json('book_completed')

        # creamos la mesa que sobreescribira los datos del anterior
        mod_book = Book(book_user=book_user, book_table=book_table, book_bar=book_bar,
                        book_expiration=book_expiration, book_completed=book_completed)
        # Si los datos introducidos pasan el filtro, se sobreescribira el bar
        try:
            book.book_user = book.book_user
            book.book_table = book.book_table
            book.book_bar = book.book_bar
            book.book_expiration = book.book_expiration
            book.book_completed = book.book_completed
            db.session.commit()
            flash('Reserva modificada.', category='success')
            return book
            # Tratamos el error en la modificacion
        except Exception as error:
            flash('Error al modificar la reserva.', category='error')
            print(error)
            error_msg = {'error': 'La reserva no se ha podido modificado'}
            return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'La reserva no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Borrar la reserva
@login_required
@admin_required
@controller.route('/api/book/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    # Buscamos la mesa la cual queremos borrar de la base de datos
    book = Book.query.filter_by(id=book_id).first()

    if book:
        try:
            db.session.delete(book)
            db.session.commit()
            flash('Reserva eliminada correctamente.', category='success')

            return jsonify({"message": "La reserva ha sido borrado"}), 200
        except Exception as error:
            flash('Error al eliminar la reserva.', category='error')
            print(error)
            error_msg = {'error': 'La reserva no ha sido borrada'}
            return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'La reserva no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)


# Creamos una ciudad
@login_required
@admin_required
@controller.route('/api/city', methods=['POST'])
def create_city():
    # Aquí recogemos del formulario del front los valores y hacemos las comprobaciones

    city_fullname = request.json('city_name')

    # Creamos el objeto Reserva si hemos pasado los filtros anteriores
    new_city = City(city_fullname=city_fullname)

    try:
        db.session.add(new_city)
        db.session.commit()
        flash('Ciudad creada correctamente.', category='success')
    except Exception as error:
        flash('Error al crear la Ciudad.', category='error')
        print(error)
        error_msg = {'error': 'La Ciudad ingresada no cumple los requisitos'}
        return make_response(jsonify(error_msg), 500)
    return new_city


# Obtener todas las ciudades
@login_required
@admin_required
@controller.route('/api/city', methods=['GET'])
def get_cities():
    cities = City.query.order_by(Book.id.desc()).all()

    if cities:
        return jsonify(cities), 200
    else:
        return jsonify({"error": "No cities found"}), 404


# Creamos un barrio
@login_required
@admin_required
@controller.route('/api/district', methods=['POST'])
def create_district():
    # Aquí recogemos del formulario del front los valores y hacemos las comprobaciones

    district_fullname = request.json('district_fullname')

    district_city = request.json('district_city')

    # Creamos el objeto Barrio si hemos pasado los filtros anteriores
    new_district = District(district_fullname=district_fullname, district_city=district_city)

    try:
        db.session.add(new_district)
        db.session.commit()
        flash('Barrio creado correctamente.', category='success')
    except Exception as error:
        flash('Error al crear el barrio.', category='error')
        print(error)
        error_msg = {'error': 'El barrio ingresado no cumple los requisitos'}
        return make_response(jsonify(error_msg), 500)
    return new_district


# Obtener un barrio
@login_required
@admin_required
@controller.route('/api/district/<district_id>', methods=['GET'])
def get_district(district_id):

    district = District.query.filter_by(id=district_id).first()

    if district:
        return district
    else:
        return jsonify({"error": "District not found"}), 404


# Obtener todos los barrios
@login_required
@admin_required
@controller.route('/api/district', methods=['GET'])
def get_books():
    districts = District.query.order_by(District.id.desc()).all()

    if districts:
        return jsonify(districts), 200
    else:
        return jsonify({"error": "No Districts found"}), 404


# Borrar el barrio
@login_required
@admin_required
@controller.route('/api/district/<district>', methods=['DELETE'])
def delete_district(district_id):
    # Buscamos la mesa la cual queremos borrar de la base de datos
    district = District.query.filter_by(id=district_id).first()

    if district:
        try:
            db.session.delete(district)
            db.session.commit()
            flash('Barrio eliminado correctamente.', category='success')

            return jsonify({"message": "El barrio ha sido borrado"}), 200
        except Exception as error:
            flash('Error al eliminar El barrio.', category='error')
            print(error)
            error_msg = {'error': 'El barrio no ha sido borrada'}
            return make_response(jsonify(error_msg), 500)
    else:
        error_msg = {'error': 'El barrio no ha sido encontrado'}
        return make_response(jsonify(error_msg), 500)
