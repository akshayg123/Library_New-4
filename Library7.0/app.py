from flask import Flask, jsonify, render_template, request, redirect, send_from_directory, url_for ,session, flash,request
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import os
from datetime import date, datetime
from sqlalchemy import create_engine
import pandas as pd
import stripe
import logging


app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)
stripe.api_version = '2020-08-27'  #  latest version available
stripe.api_key = "sk_test_51ORdqUSJDUJBJy6Sgj4QxeU1u5CCmqI7RB2Sdd0JMdLq9bmF14Ax7RM2gNqDU70YVKCkxkZcxFCVt3RP676XcB8d00sFLMVWBq"
app.secret_key = 'library'  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'akshayg2003'
app.config['MYSQL_DB'] = 'new_library2'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'akshaygirish1@gmail.com'  # Enter your email here
app.config['MAIL_PASSWORD'] = 'viey kqsg czkg wskv'  # Enter your password here
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads/'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


mysql = MySQL(app)
mail = Mail(app)

with app.app_context():
    cur = mysql.connection.cursor()
    #cur.execute("DROP TABLE IF EXISTS book_issue_table")
    #cur.execute("DROP TABLE IF EXISTS students")
    #cur.execute("DROP TABLE IF EXISTS books")
    
    cur.execute('''
         CREATE TABLE IF NOT EXISTS students (
             student_id INT PRIMARY KEY,
             student_name VARCHAR(100)
         )
     ''')

    cur.execute('''
         CREATE TABLE IF NOT EXISTS books (
             book_id VARCHAR(20) PRIMARY KEY,
             book_name VARCHAR(255),
             author VARCHAR(100),
             genre VARCHAR(100),
             image_url_l VARCHAR(255)
         )
     ''')

    cur.execute('''
         CREATE TABLE IF NOT EXISTS book_issue_table (
             student_id INT,
             book_id VARCHAR(20),
             date_of_issue DATE,
             return_date DATE,
             PRIMARY KEY (student_id, book_id),
             FOREIGN KEY (student_id) REFERENCES students(student_id),
             FOREIGN KEY (book_id) REFERENCES books(book_id)
         )
     ''')
    
    cur.execute('''
     CREATE TABLE IF NOT EXISTS rack (
         student_id INT,
         book_id VARCHAR(20),
         PRIMARY KEY (student_id, book_id),
         FOREIGN KEY (student_id) REFERENCES students(student_id),
         FOREIGN KEY (book_id) REFERENCES books(book_id)
     )
 ''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS fine_table (
        student_id INT,
        book_id VARCHAR(20),
        fine_amount INT,
        PRIMARY KEY (student_id, book_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (book_id) REFERENCES books(book_id)
    )
''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS registration_requests (
        name VARCHAR(100),
        email VARCHAR(100) PRIMARY KEY
    )
''')
    

    cur.execute('''
    CREATE TABLE IF NOT EXISTS ratings_table (
        student_id INT,
        book_id VARCHAR(20),
        rating INT,
        PRIMARY KEY (student_id, book_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (book_id) REFERENCES books(book_id)
    )
''')

    
    #cur.execute("ALTER TABLE books MODIFY book_id VARCHAR(50)")
    #mysql.connection.commit()



    #cur.execute("DELETE FROM books")
    cur.execute("SELECT COUNT(*) FROM books")
    count = cur.fetchone()[0]
    if count == 0:
        # If 'books' table is empty, insert data
        data = pd.read_csv(r'C:\Users\HP\Desktop\books_with_genre - books_with_genre.csv')
        data = data[['ISBN', 'Book-Title', 'Book-Author', 'genre', 'Image-URL-L']]
        data.columns = ['book_id', 'book_name', 'author', 'genre', 'image_url_l']
        data = data.drop_duplicates(subset='book_id', keep='first')
        engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                               .format(user="root",
                                       pw="akshayg2003",
                                       db="new_library2"))
        data.to_sql('books', con = engine, if_exists = 'append',index=False)

    cur.close()



@app.route('/')
def login():
    return render_template('login.html')



@app.route('/main_menu')
def main_menu():
    return render_template('main_menu.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO registration_requests(name, email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')



@app.route('/view_requests')
def view_requests():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM registration_requests")
    if result_value > 0:
        requests = cur.fetchall()
        return render_template('view_requests.html', requests=requests)
    return 'No requests found'



@app.route('/accept_request/<email>')
def accept_request(email):
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT name FROM registration_requests WHERE email = %s", [email])
    if result_value > 0:
        name = cur.fetchone()[0]
        # Redirect to create_account.html
        return redirect(url_for('create_account', name=name, email=email))
    else:
        return 'Email not found'


@app.route('/create_account/<name>/<email>', methods=['GET', 'POST'])
def create_account(name, email):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Here you can add the code to create the account in your database
        msg = Message('Account Created', sender='akshaygirish1@gmail.com', recipients=[email])
        msg.body = 'Dear ' + name + ',\n\nYour account has been created with the following details:\n\nUsername: ' + username + '\nPassword: ' + password
        mail.send(msg)
        return redirect(url_for('main_menu'))
    return render_template('create_account.html', name=name, email=email)




@app.route('/reject_request/<email>')
def reject_request(email):
    msg = Message('Registration Rejected', sender='akshaygirish1@gmail.com', recipients=[email])
    msg.body = 'We are sorry to say that Biblotech has reviewed your request and DECLINES your registration for more info contact the admin of Biblotech.'
    mail.send(msg)
    return 'Email sent'


@app.route('/student_login', methods=['POST'])
def student_login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students WHERE student_name = %s AND student_id = %s", (username, password))
    student = cur.fetchone()
    cur.close()

    if student is not None:
        session['student_id'] = student[0]
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error'}), 401

    

@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')


@app.route('/student_search', methods=['GET', 'POST'])
def student_search():
    if request.method == 'POST':
        book_name = request.form['book_name']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books WHERE book_name LIKE %s", ('%' + book_name + '%',))
        books = cur.fetchall()
        cur.close()
        return render_template('student_search_results.html', books=books)
    return render_template('student_search.html')


@app.route('/add_to_rack/<book_id>', methods=['POST'])
def add_to_rack(book_id):
    student_id = session['student_id']  # assuming you have stored the student_id in session
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO rack (student_id, book_id) VALUES (%s, %s)", (student_id, book_id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('student_search'))


@app.route('/view_virtual_rack', methods=['GET'])
def view_virtual_rack():
    student_id = session['student_id']  # assuming you have stored the student_id in session
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books WHERE book_id IN (SELECT book_id FROM rack WHERE student_id = %s)", (student_id,))
    books = cur.fetchall()
    cur.close()
    return render_template('view_virtual_rack.html', books=books)


@app.route('/remove_from_rack/<book_id>', methods=['POST'])
def remove_from_rack(book_id):
    student_id = session['student_id']  # assuming you have stored the student_id in session
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM rack WHERE student_id = %s AND book_id = %s", (student_id, book_id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('view_virtual_rack'))




@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_name = request.form['student_name']
        student_id = request.form['student_id']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students(student_name, student_id) VALUES (%s, %s)", (student_name, student_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('main_menu'))
    return render_template('add_student.html')




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']



@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        book_name = request.form['book_name']
        book_id = request.form['book_id']
        author = request.form['author']
        genre = request.form['genre']
        
        # Get the name of the uploaded file
        file = request.files['image']
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            # Move the file from the temporal folder to the upload
            # folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Store the url to the file
            image_url_l = url_for('uploaded_file', filename=filename)
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books(book_name, book_id, author, genre, image_url_l) VALUES (%s, %s, %s, %s, %s)", (book_name, book_id, author, genre, image_url_l))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('main_menu'))
    return render_template('add_book.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/borrow_book', methods=['GET', 'POST'])
def borrow_book():
    if request.method == 'POST':
        student_id = session.get('student_id')
        book_id = request.form['book_id']
        date_of_issue = date.today()
        session['student_id'] = student_id
        session['book_id'] = book_id
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO book_issue_table(student_id, book_id, date_of_issue) VALUES (%s, %s, %s)", (student_id, book_id, date_of_issue))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('student_dashboard'))
    return render_template('borrow_book.html')




@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    # Retrieve student_id and book_id from session
    student_id = session.get('student_id')
    book_id = session.get('book_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT date_of_issue FROM book_issue_table WHERE student_id = %s AND book_id = %s", (student_id, book_id))
    date_of_issue = cur.fetchone()[0]  
    if request.method == 'POST':
        return_date = request.form['return_date']
        cur.execute("UPDATE book_issue_table SET return_date = %s WHERE student_id = %s AND book_id = %s", (return_date, student_id, book_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('main_menu'))
    return render_template('issue_book.html', student_id=student_id, book_id=book_id, date_of_issue=date_of_issue)


@app.route('/issued_books', methods=['GET'])
def issued_books():
    student_id = session.get('student_id')  # Get the student_id from the session
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM book_issue_table WHERE student_id = %s", [student_id])
    books = cur.fetchall()  # Fetch all the books issued for the student
    cur.close()
    if books:
        return render_template('issued_books.html', books=books)  # Render the HTML page
    else:
        return "No books found for the given student ID"





@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        delete_id = request.form['delete_id']
        cur = mysql.connection.cursor()
        # Delete from book_issue_table
        result_value = cur.execute("DELETE FROM book_issue_table WHERE student_id = %s OR book_id = %s", [delete_id, delete_id])
        if result_value > 0:
            mysql.connection.commit()
            message = 'Record deleted from book_issue_table. '
        else:
            message = 'No record found in book_issue_table. '
        # Delete from rack
        result_value = cur.execute("DELETE FROM rack WHERE student_id = %s", [delete_id])
        if result_value > 0:
            mysql.connection.commit()
            message += 'Record deleted from rack. '
        else:
            message += 'No record found in rack. '
        # Delete from students
        result_value = cur.execute("DELETE FROM students WHERE student_id = %s", [delete_id])
        if result_value > 0:
            mysql.connection.commit()
            message += 'Student deleted. '
        else:
            message += 'Student not found. '
        # Delete from books
        result_value = cur.execute("DELETE FROM books WHERE book_id = %s", [delete_id])
        if result_value > 0:
            mysql.connection.commit()
            message += 'Book deleted. '
        else:
            message += 'Book not found. '
        return message
    return render_template('delete.html')


@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':
        student_name = request.form['student_name']
        student_id = request.form['student_id']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET student_name = %s WHERE student_id = %s", (student_name, student_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('main_menu'))
    return render_template('update_student.html')


@app.route('/update_book', methods=['GET', 'POST'])
def update_book():
    if request.method == 'POST':
        book_name = request.form['book_name']
        book_id = request.form['book_id']
        author = request.form['author']
        genre = request.form['genre']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET book_name = %s, author = %s, genre = %s WHERE book_id = %s", (book_name, author, genre, book_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('main_menu'))
    return render_template('update_book.html')


@app.route('/fine_calculator', methods=['GET', 'POST'])
def fine_calculator():
    if request.method == 'POST':
        student_id = request.form['student_id']
        book_id = request.form['book_id']  # Get the book_id from the form data
        current_date = datetime.strptime(request.form['current_date'], '%Y-%m-%d').date()
        cur = mysql.connection.cursor()
        result_value = cur.execute("SELECT * FROM book_issue_table WHERE student_id = %s AND book_id = %s", [student_id, book_id])  # Include book_id in the query
        if result_value > 0:
            record = cur.fetchone()
            book_return_date = record[3]
            if current_date > book_return_date:
                delta = current_date - book_return_date
                fine = delta.days * 50
                cur.execute("INSERT INTO fine_table(student_id, book_id, fine_amount) VALUES (%s, %s, %s)", (student_id, book_id, fine))  # Insert the fine into the fine_table
                mysql.connection.commit()
                return render_template('fine_results.html', fine=fine, student_id=student_id, book_id=book_id)
            else:
                return render_template('fine_results.html', fine=0, student_id=student_id, book_id=book_id)
        else:
            return 'Student not found'
    return render_template('fine_calculator.html')


@app.route('/display_fines')
def display_fines():
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM fine_table")
    if result_value > 0:
        fine_details = cur.fetchall()
        return render_template('display_fines.html', fine_details=fine_details)
    return 'No fines found'


@app.route('/fines')
def fines():
    return render_template('fines.html')



@app.route('/fetch_fines/<int:student_id>', methods=['GET'])
def fetch_fines(student_id):
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT fine_table.student_id, students.student_name, fine_table.book_id, books.book_name, fine_table.fine_amount
        FROM fine_table
        INNER JOIN students ON fine_table.student_id = students.student_id
        INNER JOIN books ON fine_table.book_id = books.book_id
        WHERE fine_table.student_id = %s
    ''', [student_id])
    fines = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.close()
    return jsonify(fines)


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = request.get_json()
    amount = data['amount']
    customer_details = data.get('customer_details', {})

    # Set currency based on customer's country
    currency = 'inr' if customer_details.get('country', '').lower() == 'india' else 'usd'

    # Set billing address collection based on currency and country
    billing_address_collection = 'auto'
    if currency != 'inr' and customer_details.get('country', '').lower() == 'india':
        billing_address_collection = 'required'

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'Fine',
                    },
                    'unit_amount': int(float(amount) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:5000/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:5000/cancel',
            customer_email=customer_details.get('email', ''),
            billing_address_collection=billing_address_collection,
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify(error=str(e)), 403


@app.route('/success', methods=['GET'])
def success():
    return "Payment successful!"

    

    


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_name = request.form['search_name']
        cur = mysql.connection.cursor()
        result_value = cur.execute("SELECT * FROM students WHERE student_name = %s", [search_name])
        if result_value > 0:
            students = cur.fetchall()
            return render_template('search_results.html', students=students)
        else:
            result_value = cur.execute("SELECT * FROM books WHERE book_name = %s", [search_name])
            if result_value > 0:
                books = cur.fetchall()
                #print(books)
                return render_template('search_results.html', books=books)
            else:
                return 'Not found'
    return render_template('search.html')


@app.route('/display_students')
def display_students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    return render_template('display_students.html', students=data)



@app.route('/display_books')
def display_books():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM books")
    data = cur.fetchall()
    cur.close()
    return render_template('display_books.html', books=data)



@app.route('/display_books_issued')
def display_books_issued():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM book_issue_table")
    data = cur.fetchall()
    cur.close()
    return render_template('display_books_issued.html', books_issued=data)




@app.route('/book_ratings', methods=['GET', 'POST'])
def book_ratings():
    if request.method == 'POST':
        student_id = session.get('student_id')
        book_name = request.form.get('book_name')
        rating = request.form.get('rating')
        cur = mysql.connection.cursor()
        cur.execute("SELECT book_id FROM books WHERE book_name = %s", [book_name])
        book_id = cur.fetchone()
        if book_id is not None:
            cur.execute("INSERT INTO ratings_table (student_id, book_id, rating) VALUES (%s, %s, %s)", (student_id, book_id, rating))
            mysql.connection.commit()
            cur.close()
            return "Rating submitted successfully"
        else:
            return "Book not found"
    else:
        cur = mysql.connection.cursor()
        cur.execute("SELECT book_name FROM books")
        book_names = [row[0] for row in cur.fetchall()]
        cur.close()
        return render_template('book_ratings.html', book_names=book_names)
    

@app.route('/book_recommendations', methods=['GET', 'POST'])
def book_recommendations():
    student_id = session.get('student_id')
    if request.method == 'POST':
        search = request.form.get('search')

        cur = mysql.connection.cursor()

        # Fetch books based on genre or author
        cur.execute("SELECT * FROM books WHERE genre = %s OR author = %s", [search, search])
        books = cur.fetchall()

        # Exclude books that the student has already issued
        cur.execute("SELECT book_id FROM book_issue_table WHERE student_id = %s", [student_id])
        issued_books = cur.fetchall()
        issued_book_ids = [book[0] for book in issued_books]
        books = [book for book in books if book[0] not in issued_book_ids]

        # Prepare a list to hold books with ratings and a list to hold books without ratings
        books_with_ratings = []
        books_without_ratings = []

        # Check if there are sufficient ratings for the books
        for book in books:
            cur.execute("SELECT COUNT(rating), AVG(rating) FROM ratings_table WHERE book_id = %s GROUP BY book_id", [book[0]])
            result = cur.fetchone()
            if result is not None:
                num_ratings, avg_rating = result
                if num_ratings >= 1:  # Change this number based on what you consider "sufficient"
                    # Add the book and its average rating to the list of books with ratings
                    books_with_ratings.append((book, avg_rating))
                else:
                    # Add the book to the list of books without ratings
                    books_without_ratings.append(book)
            else:
                # Add the book to the list of books without ratings
                books_without_ratings.append(book)

        # Sort books by average rating in descending order
        books_with_ratings.sort(key=lambda x: x[1], reverse=True)

        # Combine the lists of books with and without ratings
        books = [book for book, rating in books_with_ratings] + books_without_ratings

        cur.close()

        return render_template('book_recommendations.html', books=books)

    return render_template('book_recommendations.html')




@app.route('/display_ratings')
def display_ratings():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM ratings_table")
    ratings_data = cur.fetchall()
    cur.close()
    return render_template('display_ratings.html', ratings_data=ratings_data)





if __name__ == '__main__':
    app.run(debug=True)