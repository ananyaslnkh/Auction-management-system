# Auction-management-system
Python project using flask framework

# Problem statement:
The traditional methods of conducting car auctions often face challenges in managing the auction process efficiently. These issues hinder the smooth functioning of the auction process and lead to suboptimal outcomes for both sellers and buyers.


# Innovative contribution:
Our innovative contribution to the Car Auction Management System involves implementing Aadhar verification and email verification processes.

Aadhar Verification:
This verification process involves validating the Aadhar number provided by the user using the Verhoeff algorithm.
The Verhoeff algorithm is a checksum formula designed to detect errors in data entry or transmission. It's particularly useful for verifying the accuracy of numbers, such as Aadhar numbers or other identifiers.

Working-
•	The algorithm uses two tables:
-	Multiplication Table: This table shows how to multiply pairs of digits. 
-	Permutation Table: This table tells us how to change digits based on their positions.

•	Processing Digits: When the algorithm processes an Aadhar number:
-	It removes any spaces to make sure the number is consistent.
-	It then goes through each digit from right to left.
-	For each digit, it looks up a replacement digit in the permutation table based on its position.
-	It multiplies the current checksum by this replacement digit according to the multiplication table.
-	It keeps doing this for all digits, updating the checksum each time.

•	Checksum Validation: After processing all digits, the algorithm checks if the final checksum matches a specific value ie. 0. If it does, the Aadhar number is considered valid. If not, it is an invalid Aadhar number.



# Tasks performed

create_verification_code	Generates a random verification code of the specified length using uppercase letters and digits.

send_verification_email	Sends an email containing the verification code to the specified email address.

create_server_connection	Establishes a connection to a MySQL database server using predefined connection parameters.

validate_aadhar_number	Validates an Aadhar number using the Verhoeff algorithm and predefined multiplication and permutation tables.

/signup	-	Handles GET and POST requests for user signup.
-	Checks for existing usernames, emails, and Aadhar numbers in the database.
-	Validates the Aadhar number
-	Uses regex pattern for setting password (password must contain at least 8 characters, including uppercase, lowercase, numbers, and special characters)
-	Sends a verification mail
/verify	Handles GET and POST requests for verifying the verification code sent via email.
Inserts verified users into the database and renders the verification status

/dashboard	Redirects users to dashboards based on user type

/buyer_dashboard	Displays a dashboard for buyers with search functionality to search cars, view car details, and bid 

/seller_dashboard	-	Displays a dashboard for sellers with information on past sales, current auctions, and profit trends.
-	Used matplotlib for statistics
-	Finds the winners and notifies them via email 
-	Inserts winner details in transaction table and with transaction status ‘completed’

/login	-	Handles GET and POST requests for user login.
-	Retrieves email and password from the form.
-	Checks if the user exists in the database and verifies the password.
-	Sets session variables upon successful login and redirects to the dashboard.
/sell_car methods=['GET']	Checks if the user has an ongoing auction (limiting one auction per seller at a time)

/sell_car methods=['POST']	-	Handles the form submission for selling a car.
-	Validates the auction start and end times, ensuring start time >= current time and end time > start time
-	Saves uploaded images of the car and stores their paths in the database.
-	OS module is used to handle file paths and generate a usable URL or path for accessing the uploaded image
-	Inserts car details into the database and renders success or error messages.

save_image(image)	-	Saves an uploaded image to a specific folder (static/uploads) and returns the path.
-	Uses the secure_filename function to ensure filenames are safe

/car_details	Displays details of a specific car based on the car_id

user_details methods=['GET']	-	Handles GET requests to display the bid submission form for a specific car.
-	Retrieves the car_id from the query parameters and stores it in the session

submit_bid	-	Handles the form submission for submitting a bid on a car.
-	Retrieves user details and bid amount from the form.
-	Validates the bid amount against the starting bid price.
-	Checks if the user details entered in the bid form match the account details of the user.
-	Inserts the bid into the database if all conditions are met.
