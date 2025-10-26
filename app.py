from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import yaml, os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
import re
from functools import wraps

app = Flask(__name__)
Bootstrap(app)
CKEditor(app)


db = yaml.full_load(open('db_pub.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
#TODO: - Это к хуям удалить
app.config['MYSQL_CUSTOM_OPTIONS'] = {
    'ssl': {
        'ca': f"{db['ssl']}",
    }
}
#----
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)
mysql = MySQL(app)

# методы помощники
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'login' not in session:
            flash('Сначала войдите в систему')
            return redirect('/logcus')
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'login' not in session or session.get('id_role') not in roles:
                flash('У вас нет прав для доступа к этой странице')
                return redirect('/')
            return f(*args, **kwargs)
        return decorated_function
    return decorator



# главная страница
@app.route('/')
def index():

    message = session.pop('message', None)

    return render_template('index.html', message=message)


#регистрация пользователя
@app.route('/regcus', methods=['GET', 'POST'])
def regcus():
    if request.method == 'POST':
        user_details = request.form

        # Проверка на пустые поля
        if not user_details['firstname_client'] or not user_details['lastname_client'] or not user_details['phone_client'] or not user_details['password_client']:
            message = 'Пожалуйста, заполните все обязательные поля'
            return render_template('regcus.html', user_details=user_details, message=message)
        
        phone_client = user_details['phone_client']
        # Валидация телефона
        if not validate_phone(phone_client):
            message = 'Номер телефона должен быть в формате +7XXXXXXXXXX'
            return render_template('regcus.html', user_details=user_details, message=message)
        
        # Преобразование номера для БД
        phone_for_db = convert_phone_for_db(phone_client)

        # Проверка уникальности phone_client
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM roofing_materials.`users` WHERE phone = %s", (phone_for_db,))
        existing_user = cursor.fetchone()

        if existing_user:
            message = 'Этот телефон уже зарегистрирован. Пожалуйста, используйте другой'
            return render_template('regcus.html', user_details=user_details, message=message)
        

        # Проверка на соответствие паролей
        if user_details['password_client'] != user_details['confirmpassword']:
            message = 'Пароли не совпадают. Попробуйте снова'
            return render_template('regcus.html', user_details=user_details, message=message)

        # Проверка на соответствие условиям пароля
        password_client = user_details['password_client']
        if not validate_password(password_client):
            message = 'Пароль должен содержать минимум 8 символов и заглавную букву'
            return render_template('regcus.html', user_details=user_details, message=message)

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO roofing_materials.`users`(firstname, lastname, phone, password) VALUES (%s, %s, %s, %s)",
                       (
                           user_details['firstname_client'],
                           user_details['lastname_client'],
                           phone_for_db,
                           generate_password_hash(password_client)
                        )
                        )
        mysql.connection.commit()
        cursor.close()
        # flash('Регистрация пройдена успешно', 'success')
        session['message'] = "Регистрация пройдена успешно"
        return redirect('/logcus')

    return render_template('regcus.html', user_details={}, message=None)

def validate_password(password_client):
    # Проверка на минимальную длину
    if len(password_client) < 8:
        return False
    # Проверка на наличие цифры
    if not re.search(r"[0-9]", password_client):
        return False
    # Проверка на наличие заглавной буквы
    if not re.search(r"[A-Z]", password_client):
        return False
    return True

def validate_phone(phone):

    pattern = r'^\+\d{11}$' #Проверяет номер телефона в формате '+7XXXXXXXXXX', где X - цифра.
    return bool(re.match(pattern, phone))

def convert_phone_for_db(phone):
    # Убираем все символы кроме цифр
    clean_phone = re.sub(r'\D', '', phone)  # оставляем только цифры
        
    return clean_phone


#вход пользователя
@app.route('/logcus', methods=['GET', 'POST'])
def logcus():

    message = session.pop('message', None)

    if request.method == 'POST':
        user_details = request.form
        
        # Проверяем, что номер в правильном формате +7xxx
        if not re.match(r'^\+7\d{10}$', user_details['phone_client']):
            session['message'] = 'Номер телефона должен быть в формате +7xxxxxxxxxx'
            return render_template('logcus.html', message=session['message'])
        
        # Запрещаем номера, начинающиеся с 8
        if user_details['phone_client'].startswith('8'):
            session['message'] = 'Номер телефона должен начинаться с +7, а не с 8'
            return render_template('logcus.html', message=session['message'])
        
        phone_client = convert_phone_for_db(user_details['phone_client'])
        cursor = mysql.connection.cursor()
        result_value = cursor.execute("SELECT * FROM roofing_materials.`users` WHERE phone = %s", ([phone_client]))
        if result_value > 0:
            client = cursor.fetchone()
            if check_password_hash(client['password'], user_details['password_client']):
                session['login'] = True
                session['id_role'] = client['id_role']
                session['firstname'] = client['firstname']
                session['lastname'] = client['lastname']
                session['id_user'] = client['id_user']
                session['message'] = 'Добро пожаловать, ' + session['firstname'] + '!'
            else:
                cursor.close()
                session['message'] = 'Неверный пароль, попробуйте снова'
                return render_template('logcus.html', message=message)
        else:
            cursor.close()
            session['message'] = 'Неверный логин, попробуйте снова'
            return render_template('logcus.html', message=message)
        cursor.close()        

        return redirect('/products')
    return render_template('logcus.html', message=message)




#регистрация администратора
@app.route('/regemp', methods=['GET', 'POST'])
@login_required
@role_required([1])
def regemp():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM roles")
    roles = cursor.fetchall()
    
    if request.method == 'POST':
        emp_details = request.form
        selected_role_id = request.form.get('name_role')

        # Проверка на пустые поля
        if not emp_details['firstname_worker'] or not emp_details['lastname_worker'] or not emp_details['login_worker'] or not emp_details['password_worker'] or not emp_details['name_role']:
            message = 'Пожалуйста, заполните все обязательные поля'
            return render_template('regemp.html', emp_details=emp_details, roles=roles, message=message)

        # Проверка уникальности login_worker
        cursor.execute("SELECT * FROM roofing_materials.`users` WHERE login = %s", (emp_details['login_worker'],))
        existing_user = cursor.fetchone()

        if existing_user:
            message = 'Этот логин уже зарегистрирован. Пожалуйста, используйте другой логин'
            return render_template('regemp.html', emp_details=emp_details, roles=roles, message=message)

        # Проверка на соответствие паролей
        if emp_details['password_worker'] != emp_details['confirmpassword']:
            message = 'Пароли не совпадают. Попробуйте снова'
            return render_template('regemp.html', emp_details=emp_details, roles=roles, message=message)

        # Проверка на соответствие условиям пароля
        password_worker = emp_details['password_worker']
        if not validate_password(password_worker):
            message = 'Пароль должен содержать минимум 8 символов и заглавную букву'
            return render_template('regemp.html', emp_details=emp_details, roles=roles, message=message)

        # Получаем id_role по названию роли
        # cursor.execute("SELECT id_role FROM roles WHERE name_role = %s", (emp_details['name_role'],))
        # role = cursor.fetchone()

        if not selected_role_id:
            flash("Роль не найдена. Пожалуйста, проверьте название роли.", "error")
        else:
            # Здесь добавьте логику для обработки выбранной роли
            # Например, проверьте, существует ли роль в базе данных
            cursor.execute("SELECT * FROM roles WHERE id_role = %s", (selected_role_id,))
            role = cursor.fetchone()
            if not role:
                flash("Роль не найдена. Пожалуйста, проверьте название роли.", "error")

        id_role = role['id_role']

        cursor.execute("INSERT INTO roofing_materials.`users`(firstname, lastname, login, password, id_role) VALUES (%s, %s, %s, %s, %s)",
                       (emp_details['firstname_worker'], emp_details['lastname_worker'], emp_details['login_worker'], generate_password_hash(password_worker), id_role))
        mysql.connection.commit()
        cursor.close()
        # flash('Регистрация пройдена успешно', 'success')
        session['message'] = "Регистрация пройдена успешно"
        return redirect('/')

    return render_template('regemp.html', emp_details={}, roles=roles, message=None)


def validate_password(password_worker):
    # Проверка на минимальную длину
    if len(password_worker) < 8:
        return False
    # Проверка на наличие цифры
    if not re.search(r"[0-9]", password_worker):
        return False
    # Проверка на наличие заглавной буквы
    if not re.search(r"[A-Z]", password_worker):
        return False
    return True


#вход администратора
@app.route('/logemp', methods=['GET', 'POST'])
def logemp():

    message = session.pop('message', None)

    if request.method == 'POST':
        emp_details = request.form
        login_worker = emp_details['login_worker']
        cursor = mysql.connection.cursor()
        result_value = cursor.execute("SELECT * FROM roofing_materials.`users` WHERE login = %s", ([login_worker]))
        if result_value > 0:
            worker = cursor.fetchone()
            if check_password_hash(worker['password'], emp_details['password_worker']):
                session['login'] = True
                session['id_role'] = worker['id_role']
                session['firstname'] = worker['firstname']
                session['lastname'] = worker['lastname']
                session['message'] = 'Добро пожаловать, ' + session['firstname'] + '!'
            else:
                cursor.close()
                session['message'] = 'Неверный пароль, попробуйте снова'
                return render_template('logemp.html', message=message)
        else:
            cursor.close()
            session['message'] = 'Неверный логин, попробуйте снова'
            return render_template('logemp.html', message=message)
        cursor.close()        

        return redirect('/products')
    return render_template('logemp.html', message=message)


#выход
@app.route('/logout/')
def logout():
    session.clear()
    session['message'] = 'Вы успешно вышли'
    return redirect('/')



# страница продуктов - теперь перенаправляет на поиск
@app.route('/products')
def products():
    return redirect('/search')


# карточка продукта
@app.route('/sel_prod<int:id>')
def sel_prod(id):
    message = session.pop('message', None)
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT id_materials, name_materials, thickness, place, count, price, name_type_of_roofing_material, name_color, name_coverage, name_brand FROM materials JOIN type_of_roofing_material ON materials.id_type_of_roofing_material = type_of_roofing_material.id_type_of_roofing_material JOIN color ON materials.id_color = color.id_color JOIN coverage ON materials.id_coverage = coverage.id_coverage JOIN brand ON materials.id_brand = brand.id_brand WHERE id_materials = {}".format(id))
    if result_value > 0:
        materials = cursor.fetchone()
        return render_template('sel_prod.html', materials=materials, message=message)
    return 'Продукт не найден'




# начало редактирования продуктов, редактирования и добавления характеристик
@app.route('/edit_product<int:id>', methods=['GET', 'POST'])
@login_required
@role_required([1, 2])
def edit_product(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':

        action = request.form.get('action')

        if action == 'delete':
            # Удаление продукта
            cursor.execute("DELETE FROM materials WHERE id_materials = %s", (id,))
            mysql.connection.commit()
            cursor.close()
            flash('_______________ Продукт успешно удален', 'success')
            return redirect('/products')

        # Получение данных из формы
        name_materials = request.form['name_materials']
        thickness = request.form['thickness']
        place = request.form['place']
        count = request.form['count']
        price = request.form['price']
        id_type_of_roofing_material = request.form['id_type_of_roofing_material']
        id_color = request.form['id_color']
        id_coverage = request.form['id_coverage']
        id_brand = request.form['id_brand']


        # Проверка на пустые значения
        if not name_materials or not thickness or not place or not count or not price:
            flash('_______________ Пожалуйста, заполните все поля', 'danger')
            return redirect(request.url)  # Возвращаем на ту же страницу
        

        # Проверка уникальности name_product
        cursor.execute("SELECT COUNT(*) FROM materials WHERE name_materials = %s AND id_materials != %s", (name_materials, id))
        cont = cursor.fetchone()['COUNT(*)']

        if cont > 0:
            flash('_______________ Продукт с таким названием уже существует', 'danger')
            return redirect(request.url)
        
        # Проверка, что являются float, а count является int
        try:
            thickness = float(thickness)
            place = float(place)
            price = float(price)
            count = int(count)
        except ValueError:
            flash('_______________ Цена, объем и количество должны быть числовыми значениями', 'danger')
            return redirect(request.url)
        
         # Проверка, что price не отрицательный
        if thickness < 0 or place < 0 or price < 0 or count < 0:
            flash('_______________ Числовые значения не могут быть отрицательными', 'danger')
            return redirect(request.url)


        # обновление продукта
        result_value = cursor.execute("UPDATE materials JOIN type_of_roofing_material ON materials.id_type_of_roofing_material = type_of_roofing_material.id_type_of_roofing_material JOIN color ON materials.id_color = color.id_color JOIN coverage ON materials.id_coverage = coverage.id_coverage JOIN brand ON materials.id_brand = brand.id_brand SET name_materials = %s, thickness = %s, place = %s, count = %s, price = %s, materials.id_type_of_roofing_material = %s, materials.id_color = %s, materials.id_coverage = %s, materials.id_brand = %s WHERE id_materials = %s", (name_materials, thickness, place, count, price, id_type_of_roofing_material, id_color, id_coverage, id_brand, id))

        mysql.connection.commit()
        cursor.close()
        flash('_______________ Изменения успешно внесены', 'success')
        return redirect('/sel_prod{}'.format(id))
    
    
    cursor = mysql.connection.cursor()
    result_value = cursor.execute("SELECT * FROM materials JOIN type_of_roofing_material ON materials.id_type_of_roofing_material = type_of_roofing_material.id_type_of_roofing_material JOIN color ON materials.id_color = color.id_color JOIN coverage ON materials.id_coverage = coverage.id_coverage JOIN brand ON materials.id_brand = brand.id_brand WHERE id_materials = {}".format(id))
    if result_value > 0:
        materials = cursor.fetchone()
        material_form = {}
        material_form['name_materials'] = materials['name_materials']
        material_form['thickness'] = materials['thickness']
        material_form['place'] = materials['place']
        material_form['count'] = materials['count']
        material_form['price'] = materials['price']
        material_form['id_type_of_roofing_material'] = materials['id_type_of_roofing_material']
        material_form['id_color'] = materials['id_color']
        material_form['id_coverage'] = materials['id_coverage']
        material_form['id_brand'] = materials['id_brand']

        cursor.execute("SELECT * FROM type_of_roofing_material")
        type_of_roofing_material = cursor.fetchall()

        cursor.execute("SELECT * FROM color")
        color = cursor.fetchall()

        cursor.execute("SELECT * FROM coverage")
        coverage = cursor.fetchall()

        cursor.execute("SELECT * FROM brand")
        brand = cursor.fetchall()


        return render_template('edit_product.html', material_form=material_form, type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)

    return render_template('edit_product.html', id_materials=id)
# конец редактирования продуктов, редактирования и добавления характеристик




# начало добавления продуктов, редактирования и добавления характеристик
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
@role_required([1, 2])
def add_product():
    cursor = mysql.connection.cursor()


    cursor.execute("SELECT * FROM type_of_roofing_material")
    type_of_roofing_material = cursor.fetchall()

    cursor.execute("SELECT * FROM color")
    color = cursor.fetchall()

    cursor.execute("SELECT * FROM coverage")
    coverage = cursor.fetchall()

    cursor.execute("SELECT * FROM brand")
    brand = cursor.fetchall()

    if request.method == 'POST':
        
        addproduct = request.form

        name_materials = addproduct['name_materials']
        thickness = addproduct['thickness']
        place = addproduct['place']
        count = addproduct['count']
        price = addproduct['price']

        id_type_of_roofing_material = addproduct.get('id_type_of_roofing_material', '')
        id_color = addproduct.get('id_color', '')
        id_coverage = addproduct.get('id_coverage', '')
        id_brand = addproduct.get('id_brand', '')


        # Валидация
        if not name_materials or not thickness or not place or not count or not price:
            flash("_______________ Все поля должны быть заполнены", 'danger')
            return render_template('add_product.html', type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)


        # Проверка уникальности name_materials
        cursor.execute("SELECT * FROM materials WHERE name_materials = %s", (name_materials,))
        if cursor.fetchone():
            flash("_______________ Продукт с таким названием уже существует", 'danger')
            return render_template('add_product.html', type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)

        # Проверка, что price и volume являются float
        try:
            thickness = float(thickness)
            place = float(place)
            price = float(price)
            count = int(count)
        except ValueError:
            flash("_______________ Цена и объем должны быть числовыми значениями", 'danger')
            return render_template('add_product.html', type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)
        

        # Проверка на отрицательную толщину
        if float(thickness) < 0:
            flash("_______________ Толщина не может быть отрицательной", 'danger')
            return render_template('add_product.html', type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)

        # Проверка на отрицательную цену
        if float(price) < 0:
            flash("_______________ Цена не может быть отрицательной", 'danger')
            return render_template('add_product.html', type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)

        # Проверка на отрицательный размер
        if float(place) < 0:
            flash("_______________ Размер не может быть отрицательным", 'danger')
            return render_template('add_product.html', type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)

        # Проверка на отрицательное количество
        if int(count) < 0:
            flash("_______________ Количество не может быть отрицательным", 'danger')
            return render_template('add_product.html', type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)

    
        cursor.execute("INSERT INTO materials (name_materials, thickness, place, count, price, id_type_of_roofing_material, id_color, id_coverage, id_brand) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (name_materials, thickness, place, count, price, id_type_of_roofing_material, id_color, id_coverage, id_brand))
        
        mysql.connection.commit()
        cursor.close()

        flash("_______________ Продукт успешно добавлен", 'success')

        return redirect("/products")
    
    return render_template('add_product.html', type_of_roofing_material=type_of_roofing_material, color=color, coverage=coverage, brand=brand)

# конец добавления продуктов, редактирования и добавления характеристик





@app.route('/edit_type_of_roofing_material/', methods=['GET', 'POST'])
@login_required
@role_required([1, 2])
def edit_type_of_roofing_material():
    cursor = mysql.connection.cursor()
    message = None
    # НЕ РАБОТАЕТ ПРОВЕРКА УНИКАЛЬНОСТИ

    if request.method == 'POST':
        addproduct = request.form
        delete_id = addproduct.get('delete_id')

        if delete_id:
            cursor.execute("DELETE FROM type_of_roofing_material WHERE id_type_of_roofing_material = %s", (delete_id,))
            mysql.connection.commit()
            message = "Материал успешно удалён"

        else:
            for key in addproduct.keys():
                if key.startswith('material_'):
                    id_type_of_roofing_material = key.split('_')[1]
                    name_type_of_roofing_material = addproduct[key]
                    cursor.execute("UPDATE type_of_roofing_material SET name_type_of_roofing_material = %s WHERE id_type_of_roofing_material = %s", (name_type_of_roofing_material, id_type_of_roofing_material))

            new_material = addproduct.get('new_material', '').strip()
            if new_material: 
                cursor.execute("INSERT INTO type_of_roofing_material (name_type_of_roofing_material) VALUES (%s)", (new_material,))

            message = "Материалы успешно обновлены"

        mysql.connection.commit()

    # Загрузка данных таблицы после всех операций
    cursor.execute("SELECT * FROM type_of_roofing_material")
    type_of_roofing_material = cursor.fetchall()
    cursor.close()

    return render_template('edit_type_of_roofing_material.html', type_of_roofing_material=type_of_roofing_material, message=message)




@app.route('/edit_color/', methods=['GET', 'POST'])
@login_required
@role_required([1, 2])
def edit_color():
    cursor = mysql.connection.cursor()
    message = None  # Переменная для сообщения
    # НЕ РАБОТАЕТ ПРОВЕРКА УНИКАЛЬНОСТИ

    if request.method == 'POST':
        addproduct = request.form

        # Проверяем, есть ли запрос на удаление
        delete_id = addproduct.get('delete_id')
        if delete_id:
            # Удаляем запись с указанным ID
            cursor.execute("DELETE FROM color WHERE id_color = %s", (delete_id,))
            mysql.connection.commit()
            message = "Материал успешно удалён"
        else:
            # Обновление существующих материалов
            for key in addproduct.keys():
                if key.startswith('material_'):
                    id_color = key.split('_')[1]  # Извлекаем ID из ключа
                    name_color = addproduct[key]
                    cursor.execute("UPDATE color SET name_color = %s WHERE id_color = %s", (name_color, id_color))

            # Добавление нового материала
            new_material = addproduct.get('new_material', '').strip()
            if new_material:
                cursor.execute("INSERT INTO color (name_color) VALUES (%s)", (new_material,))

            message = "Материалы успешно обновлены"

        mysql.connection.commit()

    # Загрузка данных таблицы после всех операций
    cursor.execute("SELECT * FROM color")
    color = cursor.fetchall()
    cursor.close()  # Закрываем курсор только после всех операций
    return render_template('edit_color.html', color=color, message=message)




@app.route('/edit_coverage/', methods=['GET', 'POST'])
@login_required
@role_required([1, 2])
def edit_coverage():
    cursor = mysql.connection.cursor()
    message = None  # Переменная для сообщения
    # НЕ РАБОТАЕТ ПРОВЕРКА УНИКАЛЬНОСТИ

    if request.method == 'POST':
        addproduct = request.form

        # Проверяем, есть ли запрос на удаление
        delete_id = addproduct.get('delete_id')
        if delete_id:
            # Удаляем запись с указанным ID
            cursor.execute("DELETE FROM coverage WHERE id_coverage = %s", (delete_id,))
            mysql.connection.commit()
            message = "Материал успешно удалён"
        else:
            # Обновление существующих материалов
            for key in addproduct.keys():
                if key.startswith('material_'):
                    id_coverage = key.split('_')[1]  # Извлекаем ID из ключа
                    name_coverage = addproduct[key]
                    cursor.execute("UPDATE coverage SET name_coverage = %s WHERE id_coverage = %s", (name_coverage, id_coverage))

            # Добавление нового материала
            new_material = addproduct.get('new_material', '').strip()
            if new_material:
                cursor.execute("INSERT INTO coverage (name_coverage) VALUES (%s)", (new_material,))

            message = "Материалы успешно обновлены"

        mysql.connection.commit()

    # Загрузка данных таблицы после всех операций
    cursor.execute("SELECT * FROM coverage")
    coverage = cursor.fetchall()
    cursor.close()  # Закрываем курсор только после всех операций
    return render_template('edit_coverage.html', coverage=coverage, message=message)



@app.route('/edit_brand/', methods=['GET', 'POST'])
@login_required
@role_required([1, 2])
def edit_brand():
    cursor = mysql.connection.cursor()
    message = None  # Переменная для сообщения
    # НЕ РАБОТАЕТ ПРОВЕРКА УНИКАЛЬНОСТИ

    if request.method == 'POST':
        addproduct = request.form

        # Проверяем, есть ли запрос на удаление
        delete_id = addproduct.get('delete_id')
        if delete_id:
            # Удаляем запись с указанным ID
            cursor.execute("DELETE FROM brand WHERE id_brand = %s", (delete_id,))
            mysql.connection.commit()
            message = "Материал успешно удалён"
        else:
            # Обновление существующих материалов
            for key in addproduct.keys():
                if key.startswith('material_'):
                    id_brand = key.split('_')[1]  # Извлекаем ID из ключа
                    name_brand = addproduct[key]
                    cursor.execute("UPDATE brand SET name_brand = %s WHERE id_brand = %s", (name_brand, id_brand))

            # Добавление нового материала
            new_material = addproduct.get('new_material', '').strip()
            if new_material:
                cursor.execute("INSERT INTO brand (name_brand) VALUES (%s)", (new_material,))

            message = "Материалы успешно обновлены"

        mysql.connection.commit()

    # Загрузка данных таблицы после всех операций
    cursor.execute("SELECT * FROM brand")
    brand = cursor.fetchall()
    cursor.close()  # Закрываем курсор только после всех операций
    return render_template('edit_brand.html', brand=brand, message=message)



@app.route('/search', methods=['GET', 'POST'])
def search():
    cursor = mysql.connection.cursor()

    # Загружаем данные для фильтров
    cursor.execute("SELECT * FROM type_of_roofing_material")
    types = cursor.fetchall()
    cursor.execute("SELECT * FROM color")
    colors = cursor.fetchall()
    cursor.execute("SELECT * FROM coverage")
    coverages = cursor.fetchall()
    cursor.execute("SELECT * FROM brand")
    brands = cursor.fetchall()

    #Диапазоны
    thickness_ranges = {
        "0-0.5": {"start": 0.0, "end": 0.5, "label": "0 - 0.5 мм"},
        "0.5-0.8": {"start": 0.5, "end": 0.8, "label": "0.5 - 0.8 мм"}, 
        "0.8+": {"start": 0.8, "end": None, "label": "0.8 мм и более"}, 
    }

    price_ranges = {
        "0-1000": {"start": 0, "end": 1000, "label": "до 1000 руб"},
        "1000-1200": {"start": 1000, "end": 1200, "label": "1000 - 1200 руб"},
        "1200-1500": {"start": 1200, "end": 1500, "label": "1200 - 1500 руб"},
        "1500+": {"start": 1500, "end": None, "label": "1500 руб и выше"},
    }

    size_ranges = {
        "0-1": {"start": 0, "end": 1, "label": "до 1 м²"},
        "1-5": {"start": 1, "end": 5, "label": "1 - 5 м²"},
        "5+": {"start": 5, "end": None, "label": "5 м² и более"},
    }

    form_data = request.form if request.method == 'POST' else {}

    # Базовый SQL
    sql = """
        SELECT id_materials, name_materials, material_photo, thickness, place, count, price, 
               name_type_of_roofing_material, name_color, name_coverage, name_brand
        FROM materials
        JOIN type_of_roofing_material ON materials.id_type_of_roofing_material = type_of_roofing_material.id_type_of_roofing_material
        JOIN color ON materials.id_color = color.id_color
        JOIN coverage ON materials.id_coverage = coverage.id_coverage
        JOIN brand ON materials.id_brand = brand.id_brand
        WHERE 1=1
    """
    params = []

    

    if request.method == 'POST':
        # Получаем установленные фильтры
        query = request.form.get('query', '').strip()
        type_filter = request.form.get('type_filter', '')
        color_filter = request.form.get('color_filter', '')
        coverage_filter = request.form.get('coverage_filter', '')
        brand_filter = request.form.get('brand_filter', '')
        thickness_filter = request.form.get('thickness_filter', '')
        price_filter = request.form.get('price_filter', '')
        size_filter = request.form.get('size_filter', '')

       # --- Текстовый поиск ---
        if query:
            like_query = f"%{query}%"
            sql += (
                f" AND (name_materials LIKE '{like_query}' "
                f"OR name_type_of_roofing_material LIKE '{like_query}' "
                f"OR name_color LIKE '{like_query}' "
                f"OR name_coverage LIKE '{like_query}' "
                f"OR name_brand LIKE '{like_query}')"
            )

        # --- Простые фильтры ---
        if type_filter:
            sql += f" AND materials.id_type_of_roofing_material = {type_filter}"

        if color_filter:
            sql += f" AND materials.id_color = {color_filter}"

        if coverage_filter:
            sql += f" AND materials.id_coverage = {coverage_filter}"

        if brand_filter:
            sql += f" AND materials.id_brand = {brand_filter}"

        # --- Фильтр по толщине ---
        if thickness_filter:
            r = thickness_ranges[thickness_filter]
            if r["end"] is not None:
                sql += f" AND materials.thickness BETWEEN {r['start']} AND {r['end']}"
            else:
                sql += f" AND materials.thickness >= {r['start']}"

        # --- Фильтр по цене ---
        if price_filter:
            r = price_ranges[price_filter]
            if r["end"] is not None:
                sql += f" AND materials.price BETWEEN {r['start']} AND {r['end']}"
            else:
                sql += f" AND materials.price >= {r['start']}"

        # --- Фильтр по размеру ---
        if size_filter:
            r = size_ranges[size_filter]
            if r["end"] is not None:
                sql += f" AND materials.place BETWEEN {r['start']} AND {r['end']}"
            else:
                sql += f" AND materials.place >= {r['start']}"
    

    sql += " ORDER BY name_materials"
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()

    user_role = session.get('id_role')
    if user_role in [1, 2]:
        return render_template('results.html',
                            results=results,
                            types=types,
                            colors=colors,
                            coverages=coverages,
                            brands=brands,
                            thickness_ranges=thickness_ranges,
                            price_ranges=price_ranges,
                            size_ranges=size_ranges,
                            form_data=form_data)
    else:
        return render_template('results_customer.html',
                            results=results,
                            types=types,
                            colors=colors,
                            coverages=coverages,
                            brands=brands,
                            thickness_ranges=thickness_ranges,
                            price_ranges=price_ranges,
                            size_ranges=size_ranges,
                            form_data=form_data)


@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    if 'login' not in session:
        return redirect('/logcus')

    cursor = mysql.connection.cursor()

    # Получаем все статусы
    cursor.execute("SELECT * FROM order_status")
    statuses = cursor.fetchall()

    search_query = ''
    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()

    user_role = session.get('id_role')

    if user_role in [1, 2]:  # администратор или модератор
        sql = """
            SELECT o.id_order, o.order_date, o.id_status, os.name_status,
                   c.firstname, c.lastname,
                   m.name_materials, oi.quantity, oi.price
            FROM orders o
            JOIN `users` c ON o.id_user = c.id_user
            JOIN order_items oi ON o.id_order = oi.id_order
            JOIN materials m ON oi.id_materials = m.id_materials
            JOIN order_status os ON o.id_status = os.id_status
            WHERE 1=1
        """
        params = []

        if search_query:
            sql += " AND (o.id_order LIKE %s OR c.firstname LIKE %s OR c.lastname LIKE %s)"
            like_query = f"%{search_query}%"
            params.extend([like_query, like_query, like_query])

        sql += " ORDER BY o.order_date DESC"
        cursor.execute(sql, params)
        orders = cursor.fetchall()
        cursor.close()
        return render_template('orders/orders_admin.html', orders=orders, statuses=statuses, search_query=search_query)

    else:  # клиент
        cursor.execute("""
            SELECT o.id_order, o.order_date, o.id_status, os.name_status,
                   m.name_materials, oi.quantity, oi.price
            FROM orders o
            JOIN order_items oi ON o.id_order = oi.id_order
            JOIN materials m ON oi.id_materials = m.id_materials
            JOIN order_status os ON o.id_status = os.id_status
            WHERE o.id_user = %s
            ORDER BY o.order_date DESC
        """, (session.get('id_user'),))
        orders = cursor.fetchall()
        cursor.close()
        return render_template('orders/orders_customer.html', orders=orders)

@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
@role_required([1, 2])
def update_order_status(order_id):
    if 'login' not in session or session.get('id_role') not in [1, 2]:
        return redirect('/orders')

    new_status = request.form.get('status')

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE orders SET id_status = %s WHERE id_order = %s", (new_status, order_id))
    mysql.connection.commit()
    cursor.close()
    return redirect('/orders')

@app.route('/order/<int:material_id>', methods=['GET', 'POST'])
@login_required
@role_required([3])
def order(material_id):

    cursor = mysql.connection.cursor()
    # Получаем данные материала
    cursor.execute("SELECT * FROM materials WHERE id_materials=%s", (material_id,))
    material = cursor.fetchone()

    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        price = material['price'] * quantity

        # Создаем заказ
        cursor.execute(
            "INSERT INTO orders (id_user) VALUES (%s)",
            (session['id_user'],)
        )
        order_id = cursor.lastrowid

        # Добавляем товар в заказ
        cursor.execute(
            "INSERT INTO order_items (id_order, id_materials, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, material_id, quantity, price)
        )
        mysql.connection.commit()
        flash('Заказ успешно создан!')
        return redirect(url_for('orders'))

    return render_template('orders/order_form.html', material=material)



if __name__ == '__main__':
    app.run(debug=True, port=5005)