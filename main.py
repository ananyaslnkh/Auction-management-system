'''
CAR AUCTION MANAGEMENT SYSTEM
'''

from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
from mysql.connector import Error
from flask_mail import Mail, Message
import random
import string
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from PIL import Image
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import re

# here app is an instance of flask application, name variable is special python variable that represents the name of current module
# secret key is used for secretly signing session cookies and other cryptographic functions within flask

app = Flask(__name__)
app.secret_key = 'secret'


# smtp = simple mail transfer protocol
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'exampleprojectcs@gmail.c' 
app.config['MAIL_PASSWORD'] = 'rfbw euew poor smdf'
app.config['MAIL_DEFAULT_SENDER'] = 'exampleproject@gmail.com'

mail = Mail(app)


def create_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def send_verification_email(email, verification_code):
    msg = Message('Email Verification', recipients=[email])
    msg.body = f'Your verification code is: {verification_code}'
    mail.send(msg)


def create_server_connection():
    host_name = 'localhost'
    user_name = 'root'
    user_password = 'rooppt123'
    db_name = 'ams'
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        if connection.is_connected():
            print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection


# verhoeff algorithm for aadhar verification
mult = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5], [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7], [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3], [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]]
perm = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4], [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7], [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]]


def validate_aadhar_number(aadhar_number):
    aadhar_number = aadhar_number.replace(' ', '')
    try:
        i = len(aadhar_number)
        j = 0
        x = 0

        while i > 0:
            i -= 1
            x = mult[x][perm[(j % 8)][int(aadhar_number[i])]]
            j += 1
        return x == 0
    except ValueError:
        return False
    except IndexError:
        return False


# A GET message is send, and the server returns data.
# POST Used to send HTML form data to the server. The data received by the POST method is not cached by the server.

# Routes
@app.route('/')
def signup_redirect():
    return redirect('/signup')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        password_hash = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']
        address = request.form['address']
        phone_number = request.form['phone_number']
        aadhar_number = request.form['aadhar_number']
        user_type = request.form['user_type']

        # Check if username already exists
        connection = create_server_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM User WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                error_message = f"Error: User with username '{username}' already exists."
                return render_template('sign.html', error=error_message)

            # Check if email already exists
            cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
            existing_email = cursor.fetchone()
            if existing_email:
                error_message = f"Error: User with email '{email}' already exists."
                return render_template('sign.html', error=error_message)

            # Check if Aadhar number already exists

            cursor.execute("SELECT * FROM User WHERE aadhar_number = %s", (aadhar_number,))
            existing_aadhar = cursor.fetchone()
            if existing_aadhar:
                error_message = "Error: Account with this Aadhar number already exists."
                return render_template('sign.html', error=error_message)
            
            # Validate Aadhar number
            if not validate_aadhar_number(aadhar_number):
                error_message = "Error: Invalid Aadhar number."
                return render_template('sign.html', error=error_message)

            # Validate password using regex
            if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$", password_hash):

                error_message = "Error: Password must contain at least 8 characters, including uppercase, lowercase, numbers, and special characters."
                return render_template('sign.html', error=error_message)


            # Generate verification code and send email
            verification_code = create_verification_code()
            session['verification_code'] = verification_code
            send_verification_email(email, verification_code)

            # Store user details in session for verification
            session['signup_details'] = {
                'username': username,
                'password_hash': password_hash,
                'email': email,
                'full_name': full_name,
                'address': address,
                'phone_number': phone_number,
                'aadhar_number': aadhar_number,
                'user_type': user_type
            }

            return redirect('/verify')

        except mysql.connector.Error as err:
            error_message = str(err)
        finally:
            cursor.close()
            connection.close()

    return render_template('sign.html', error=error_message)



@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        user_verification_code = request.form['verification_code']
        verification_code = session.get('verification_code')

        if user_verification_code == verification_code:
            signup_details = session.get('signup_details')
            if signup_details:
                connection = create_server_connection()
                cursor = connection.cursor()
                try:
                    sql = """INSERT INTO User (username, password_hash, email, full_name, address, phone_number, aadhar_number, user_type, is_verified) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(sql, (
                        signup_details['username'], signup_details['password_hash'], signup_details['email'],
                        signup_details['full_name'], signup_details['address'], signup_details['phone_number'],
                        signup_details['aadhar_number'], signup_details['user_type'], 1))
                    connection.commit()

                    success_message = "Verification successful. User added to the database."
                    session.pop('signup_details')  
                    return render_template('verify.html', success=success_message) 

                except mysql.connector.Error as err:
                    return str(err)
                finally:
                    cursor.close()
                    connection.close()
        else:
            return render_template('verify.html', error='Incorrect verification code. Please try again.')

    return render_template('verify.html')



# Check if user is buyer/seller and redirect to respective dashboard
@app.route('/dashboard')
def dashboard_route():
    if 'logged_in' in session and session['logged_in']:
        user_type = session.get('user_type')
        if user_type == 'seller':
            return redirect(url_for('seller_dashboard_route'))
        else:
            return redirect(url_for('buyer_dashboard_route')) 
    else:
        return redirect(url_for('login_route'))



# Displays cars on user dashboard and search bar functionality
@app.route('/buyer_dashboard', methods=['GET', 'POST'])
def buyer_dashboard_route():
    if 'logged_in' in session and session['logged_in']:
        connection = create_server_connection()
        cursor = connection.cursor()
        try:
            if request.method == 'POST':
                search_query = request.form['search_query']
                cursor.execute("SELECT car_id, make, model, starting_bid_price, side_image_path FROM Car WHERE make LIKE %s OR model LIKE %s", (f'%{search_query}%', f'%{search_query}%'))
            else:
                cursor.execute("SELECT car_id, make, model, starting_bid_price, side_image_path FROM Car")
            
            
            cars_data = cursor.fetchall()
            cars = []
            for car in cars_data:
                car_dict = {
                    'car_id': car[0],
                    'make': car[1],
                    'model': car[2],
                    'starting_bid_price': car[3],
                    'side_image_path': car[4],
                }
                cars.append(car_dict)

            if not cars:  
                error_message = 'Car not found.'
                return render_template('dashboard.html', error_message=error_message)
            else:
                return render_template('dashboard.html', cars=cars)
            
        except Exception as e:
            error_message = str(e)
            return render_template('dashboard.html', error_message=error_message)
        finally:
            cursor.close()
            connection.close()
    else:
        return redirect(url_for('login_route'))




@app.route('/seller_dashboard')
def seller_dashboard_route():
    if 'logged_in' in session and session['logged_in']:
        user_id = session.get('user_id')
        if user_id:
            connection = create_server_connection()
            cursor = connection.cursor()

            try:
                # strftime is a method used to format date time object into a string 
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Find auctions that have ended and insert into transaction table
                cursor.execute("SELECT Car.car_id, Car.seller_id, Bid.bidder_id AS bidder_id, \
                                Bid.bid_amount AS winning_bid_amount, U.email AS winner_email \
                                FROM Bid \
                                JOIN Car ON Bid.car_id = Car.car_id \
                                JOIN User U ON Bid.bidder_id = U.user_id \
                                WHERE Car.auction_end_time <= %s \
                                AND Bid.bid_amount = ( \
                                    SELECT MAX(bid_amount) \
                                    FROM Bid \
                                    WHERE car_id = Car.car_id \
                                )", (current_time,))
                winners_data = cursor.fetchall()

                # Update auction status and notify winners via email
                for winner in winners_data:
                    car_id = winner[0]
                    seller_id = winner[1]
                    bidder_id = winner[2]
                    winning_bid_amount = winner[3]
                    winner_email = winner[4]

                    # Check if a transaction for this car_id already exists
                    cursor.execute("SELECT * FROM Transaction WHERE car_id = %s", (car_id,))
                    existing_transaction = cursor.fetchone()

                    if not existing_transaction:
                        print(car_id, bidder_id, seller_id, winning_bid_amount, current_time)
                        
                        # Winner details inserted into the transaction table with status 'completed'
                        cursor.execute("INSERT INTO Transaction (car_id, buyer_id, seller_id, transaction_amount, transaction_time, transaction_status) \
                                        VALUES (%s, %s, %s, %s, %s, 'completed')", (car_id, bidder_id, seller_id, winning_bid_amount, current_time))
                        connection.commit()

                        # Send notification email to the winner using Flask-Mail
                        msg = Message('Congratulations! You Won the Bid',
                                      sender='exampleprojectcs@gmail.c',
                                      recipients=[winner_email])
                        msg.body = f'You have won the bid for car ID {car_id}. Congratulations! Please proceed with the payment.'
                        mail.send(msg)

                # Fetch past sales data for auctions that have ended
                cursor.execute("SELECT Car.make, Car.model, MAX(Bid.bid_amount) AS winning_price, Car.auction_end_time \
                                FROM Bid \
                                JOIN Car ON Bid.car_id = Car.car_id \
                                WHERE Car.seller_id = %s AND Car.auction_end_time <= %s \
                                GROUP BY Car.make, Car.model, Car.auction_end_time", (user_id, current_time))
                past_sales = cursor.fetchall()

                # Fetch current auctions data with bidder names sorted by bid amount
                cursor.execute("SELECT U.username AS bidder_name, Bid.bid_amount \
                                FROM Bid \
                                JOIN User U ON Bid.bidder_id = U.user_id \
                                WHERE Bid.car_id IN (SELECT Car.car_id FROM Car WHERE Car.seller_id = %s AND Car.auction_end_time > %s) \
                                ORDER BY Bid.bid_amount DESC", (user_id, current_time))
                current_auctions = cursor.fetchall()

                # Generate and save the current auction graph
                plt.figure(figsize=(10, 6))
                plt.barh([row[0] for row in current_auctions], [row[1] for row in current_auctions], color='skyblue')
                plt.xlabel('Bid Amount (Rs)')
                plt.ylabel('Bidder Names')
                plt.title('Current Auction: Bid Amounts by Bidder')
                plt.gca().invert_yaxis()  # Invert y-axis for better visualization
                current_auction_plot = 'static/plots/current_auction_plot.png'
                plt.savefig(current_auction_plot)
                plt.close()


                # Calculate Profit Trend
                cursor.execute("SELECT transaction_time, (transaction_amount - starting_bid_price) AS profit \
                                FROM Transaction \
                                JOIN Car ON Transaction.car_id = Car.car_id \
                                WHERE Transaction.seller_id = %s", (user_id,))
                profit_data = cursor.fetchall()


                # Generate and save the profit trend graph
                plt.figure(figsize=(10, 6))
                plt.plot([row[0] for row in profit_data], [row[1] for row in profit_data], marker='o', color='green', linestyle='-', linewidth=2)
                plt.xlabel('Date-Time')
                plt.ylabel('Profit (Rs)')
                plt.title('Profit Trend')
                plt.grid(True)
                profit_plot = 'static/plots/profit_plot.png'
                plt.savefig(profit_plot)
                plt.close()


                cursor.close()
                connection.close()

                return render_template('seller_dashboard.html', past_sales=past_sales, current_auctions=current_auctions, current_auction_plot=current_auction_plot, profit_plot=profit_plot)
            except Exception as e:
                error_message = str(e)
                return render_template('seller_dashboard.html', error_message=error_message)
        else:
            return "Seller ID not found in session."
    else:
        return redirect(url_for('login_route'))




@app.route('/login', methods=['GET', 'POST'])
def login_route():
    error_message = None
    success_message = None
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = create_server_connection()
        cursor = connection.cursor()
        try:
            # Check if user has an account
            cursor.execute("SELECT * FROM User WHERE email = %s", (email,))
            existing_user = cursor.fetchone()
            if not existing_user:
                error_message = "Please sign up first."
            else:
                stored_password_hash = existing_user[2]

                # Check if password is correct
                if password == stored_password_hash:
                    success_message = "Login successful!"
                    session['logged_in'] = True 
                    session['user_id'] = existing_user[0] 
                    session['user_type'] = existing_user[8]
                    return redirect(url_for('dashboard_route'))
                else:
                    error_message = "Incorrect password. Please try again."
        except mysql.connector.Error as err:
            error_message = str(err)
        finally:
            cursor.close()
            connection.close()
    
    return render_template('login.html', error=error_message, success=success_message)



@app.route('/sell_car', methods=['GET'])
def sell_car_form():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('login_route'))

    connection = create_server_connection()
    cursor = connection.cursor()
    try:

        # Check if there is ongoing auction (seller is allowed to post only one auction at a time)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("SELECT auction_end_time FROM Car WHERE seller_id = %s AND auction_end_time > %s", (user_id, current_time))
        auctions = cursor.fetchall()

        if auctions:
            auction_status = "Auction ongoing, you cannot post new auctions"
            return render_template('sell_car.html', auction_status=auction_status)
        else:
            return render_template('sell_car.html')
    except Exception as e:
        error_message = str(e)
        return render_template('sell_car.html', error_message=error_message)
    finally:
        cursor.close()
        connection.close()



@app.route('/sell_car', methods=['POST'])
def sell_car():
    make = request.form['make']
    model = request.form['model']
    year = request.form['year']
    VIN = request.form['vin']
    mileage = request.form['mileage']
    fuel_type = request.form['fuel_type'] 
    car_condition = request.form['condition']
    starting_bid_price = request.form['starting_bid']
    auction_start_time = request.form['auction_start']
    auction_end_time = request.form['auction_end']
    front_image = request.files['front_image']
    back_image = request.files['back_image']
    side_image = request.files['side_image']
    top_image = request.files['top_image']

    error_message = None

    # Auction start time must be >= current time and auction end time must be > start time
    if auction_start_time < datetime.now().strftime('%Y-%m-%dT%H:%M'):
        error_message = "Auction start datetime must be greater than or equal to current datetime."
        return render_template('sell_car.html', error_message=error_message)

    if auction_start_time >= auction_end_time:
        error_message = "Auction end datetime should be greater than auction start datetime."
        return render_template('sell_car.html', error_message=error_message)

    front_image_path = save_image(front_image)
    back_image_path = save_image(back_image)
    side_image_path = save_image(side_image)
    top_image_path = save_image(top_image)


    if 'user_id' not in session:
        return redirect(url_for('login_route'))
    user_id = session['user_id'] 

    connection = create_server_connection()
    cursor = connection.cursor()
    try:
        sql = """INSERT INTO Car (make, model, year, VIN, mileage, fuel_type, car_condition, starting_bid_price, 
                auction_start_time, auction_end_time, seller_id, front_image_path, back_image_path, side_image_path, top_image_path) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql, (make, model, year, VIN, mileage, fuel_type, car_condition, starting_bid_price,
                             auction_start_time, auction_end_time, user_id, front_image_path, back_image_path,
                             side_image_path, top_image_path))
        
        connection.commit()
        success_message = "Auction is live!"
        return render_template('sell_car.html', success_message = success_message)
    
    except mysql.connector.Error as err:
        return str(err)
    finally:
        cursor.close()
        connection.close()

# Specific folder for saving images uploaded by the seller, so that paths can be stored in the database
# OS module is used to handle file paths and generate a usable URL or path for accessing the uploaded image
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def save_image(image):
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return os.path.join('uploads', filename).replace('\\','/')




# Displays car details on the website
@app.route('/car_details')
def car_details_route():
    car_id = request.args.get('car_id')
    if 'logged_in' in session and session['logged_in']:
        connection = create_server_connection()
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT make, model, VIN, mileage, fuel_type, car_condition, starting_bid_price, auction_end_time, front_image_path, side_image_path, back_image_path, top_image_path FROM Car WHERE car_id = %s", (car_id,))
            car_details = cursor.fetchone()
            if car_details:
                car = {
                    'make': car_details[0],
                    'model': car_details[1],
                    'VIN': car_details[2],
                    'mileage': car_details[3],
                    'fuel_type': car_details[4],
                    'car_condition': car_details[5],
                    'starting_bid_price': car_details[6],
                    'auction_end_time': car_details[7],
                    'front_image_path': car_details[8],
                    'side_image_path': car_details[9],
                    'back_image_path': car_details[10],
                    'top_image_path': car_details[11],
                }

                car_photos = [car['front_image_path'], car['side_image_path'], car['back_image_path'], car['top_image_path']]

                return render_template('car_details.html', car=car, car_photos=car_photos, car_id=car_id)
            else:
                error_message = "Car not found."
                return render_template('car_details.html', error_message=error_message)
        except Exception as e:
            error_message = str(e)
            return render_template('car_details.html', error_message=error_message)
        finally:
            cursor.close()
            connection.close()
    else:
        return redirect(url_for('login_route'))



# Checking for which car id the bid was submitted
@app.route('/user_details', methods=['GET'])
def submit_bid_form():
    car_id = request.args.get('car_id')
    if car_id:
        session['car_id'] = car_id
    else:
        session.pop('car_id', None)

    return render_template('user_details.html', car_id=car_id)




@app.route('/user_details', methods=['POST'])
def submit_bid():
    error_message = None
    success_message = None

    full_name = request.form['full_name']
    address = request.form['address']
    phone_number = request.form['phone_number']
    bid_amount = request.form['bid_amount']

    user_id = session.get('user_id')
    car_id = session.get('car_id')

    if user_id is None or car_id is None:
        error_message = "Bidder ID or Car ID not found in session."
        return render_template('user_details.html', error_message=error_message, car_id=car_id)

    try:
        connection = create_server_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT starting_bid_price FROM Car WHERE car_id = %s", (car_id,))
        starting_bid_price = cursor.fetchone()[0]

        # Check if the bid amount is greater than or equal to the starting bid price
        if float(bid_amount) >= starting_bid_price:
            cursor.execute("SELECT full_name, address, phone_number FROM User WHERE user_id = %s", (user_id,))
            user_details = cursor.fetchone()
            
        # Check if the user details entered in the bid form match with the account details of the user
            if user_details and user_details[0] == full_name and user_details[1] == address and user_details[2] == phone_number:
                bid_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                sql = """INSERT INTO Bid (car_id, bidder_id, bid_amount, bid_time) 
                        VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (car_id, user_id, bid_amount, bid_time))
                connection.commit()
                success_message = "Bid submitted successfully!"
                return render_template('user_details.html', success_message=success_message, car_id=car_id)
            else:
                error_message = "User details do not match. Please check your details and try again."
                return render_template('user_details.html', error_message=error_message, car_id=car_id)
        else:
            error_message = "Bid amount should be greater than or equal to the starting bid price."
            return render_template('user_details.html', error_message=error_message, car_id=car_id)


    except mysql.connector.Error as err:
        return str(err)
    finally:
        cursor.close()
        connection.close()

        
if __name__ == '__main__':
    app.run(debug=True)
