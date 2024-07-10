CREATE DATABASE AMS;
USE AMS;

CREATE TABLE Admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(20),
    email VARCHAR(50),
    password_hash VARCHAR(20)
);

CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(20),
    password_hash VARCHAR(20),
    email VARCHAR(50),
    full_name VARCHAR(100),
    address VARCHAR(300),
    phone_number VARCHAR(10),
    aadhar_number VARCHAR(12),
    user_type ENUM('seller', 'buyer'),
    is_verified BOOLEAN DEFAULT FALSE
);

CREATE TABLE Car (
    car_id INT PRIMARY KEY AUTO_INCREMENT,
    make VARCHAR(200),
    model VARCHAR(50),
    year INT,
    VIN VARCHAR(17),
    mileage INT,
    car_condition VARCHAR(150),
    starting_bid_price DECIMAL(10, 2),
    auction_start_time DATETIME,
    auction_end_time DATETIME,
    current_bid DECIMAL(10, 2),
    seller_id INT,
    FOREIGN KEY (seller_id) REFERENCES User(user_id)
);

CREATE TABLE Bid (
    bid_id INT PRIMARY KEY AUTO_INCREMENT,
    car_id INT,
    bidder_id INT,
    bid_amount DECIMAL(10, 2),
    bid_time DATETIME,
    FOREIGN KEY (car_id) REFERENCES Car(car_id),
    FOREIGN KEY (bidder_id) REFERENCES User(user_id)
);

CREATE TABLE Transaction (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    car_id INT,
    buyer_id INT,
    seller_id INT,
    transaction_amount DECIMAL(10, 2),
    transaction_time DATETIME,
    transaction_status ENUM('pending', 'completed'),
    FOREIGN KEY (car_id) REFERENCES Car(car_id),
    FOREIGN KEY (buyer_id) REFERENCES User(user_id),
    FOREIGN KEY (seller_id) REFERENCES User(user_id)
);

CREATE TABLE Auction (
    auction_id INT PRIMARY KEY AUTO_INCREMENT,
    car_id INT,
    auction_start_time DATETIME,
    auction_end_time DATETIME,
    highest_bid_id INT,
    FOREIGN KEY (car_id) REFERENCES Car(car_id),
    FOREIGN KEY (highest_bid_id) REFERENCES Bid(bid_id)
);

ALTER TABLE Admin AUTO_INCREMENT = 1;
ALTER TABLE User AUTO_INCREMENT = 1;
ALTER TABLE Car AUTO_INCREMENT = 101;
ALTER TABLE Bid AUTO_INCREMENT = 1;
ALTER TABLE Transaction AUTO_INCREMENT = 1;
ALTER TABLE Auction AUTO_INCREMENT = 111;
select * from User;
select * from Car;
delete from User;