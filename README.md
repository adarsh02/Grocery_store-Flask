# Online Grocery Store using Flask

This project is a web application for an online grocery store allowing users to view and
purchase items from different categories. Users can create accounts, log in, and add items to
their cart and buy those items. This web application also includes an admin panel to add and
manage categories,add and manage items to the webpage, and view sales data in charts. The
goal is to provide a user-friendly shopping experience and efficient inventory management
for the admin.
## Features

### User Module

1. **User Registration and Login**: Users can register for an account and log in to the system using their email and password.

2. **Browse and Search Items**: Users can browse items by category and search for items using keywords.

3. **Filter and Sorting**: Users can filter items based on various criteria such as price range, items left, and expiry date.

4. **Add to Cart**: Users can add items to their cart and specify the quantity.

5. **Cart Management**: Users can view their cart, adjust quantities, and remove items.

6. **Purchase History**: Users can view their purchase history, including order details and delivery addresses.

7. **Checkout and Payment**: Users can proceed to checkout, view the total cost, and make payment for the selected items.

### Admin Module

1. **Admin Login**: Admins can log in to the admin module using their credentials.

2. **Manage Categories**: Admins can add, edit, and delete categories for grocery items.

3. **Manage Items**: Admins can add, edit, and delete items within categories. They can also manage item details such as price, quantity, expiry date, and manufacture date.

4. **Generate Reports**: Admins can generate reports, including charts that show revenue by category, top bought items, and top revenue-generating items.

## How to Run the Application

### Steps

1. Clone the repository: 
```
git clone <repository_url>
```
2. Navigate to the project directory: `
```
cd Grocery_store-Flask
```
3. Run the Flask app:
```
   python main.py
```

The application will be accessible at `http://127.0.0.1:5000/`.

## Code Structure

The project consists of several Python files organized into modules:

1. `main.py`: The main entry point of the application. It initializes the Flask app, sets up the database, and registers blueprints.

2. `website/__init__.py`: Defines the Flask app and database configuration, including blueprints for different modules.

3. `website/auth.py`: Implements user authentication functionalities, including user login, registration, and authentication.

4. `website/views.py`: Defines the user module functionalities, such as browsing items, managing the cart, purchasing items, and user profile management.

5. `website/admin.py`: Implements the admin module functionalities, including managing categories, items, and generating reports.

6. `website/models.py`: Contains the database models using SQLAlchemy, including `User`, `Cart`, `Items`, and `User_History`.

7. `static/` and `templates/`: Contains static files (CSS, images) and HTML templates for rendering the web pages.

## Requirements

The `requirements.txt` file lists all the required packages and their versions for the project. Install these packages using the command: `pip install -r requirements.txt`.


