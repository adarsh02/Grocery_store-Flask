from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Items, User, Cart,User_History
from flask_login import login_required, current_user
from  website.__init__ import db 
from website.admin import apply_filters
from datetime import datetime,date,timedelta
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc

views = Blueprint("views", __name__)


@views.route('/user_home')
@login_required
def user_home():
    if request.method == 'POST':
        return search_and_filter()

    # For GET request or when no filters are applied, display all items
    items = Items.query.all()
    categories = set(item.category for item in items if item is not None)
    categs = {category: [] for category in categories}
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    # Group items by category
    for item in items:
        if item is not None:
            categs[item.category].append(item)

    # Sort the items within each category
    for category in categs:
        categs[category] = sorted(categs[category], key=lambda x: x.item_name)

    all_categories = set(item.category for item in Items.query.all())  # Fetch all categories for the dropdown

    # Fetch the actual items from the Items table using the best-selling item IDs
    
    return render_template('user_home.html', categs=categs, all_categories=all_categories,cart_items=cart_items)

@views.route('/add_to_cart/<item_id>', methods=['POST'])
@login_required
def add_to_cart(item_id):
    user_id = current_user.id  # Replace with the actual user ID
    no_of_items = int(request.form.get('no_of_items'))

    if item_id and no_of_items:
        try:
            item_id = int(item_id)
            no_of_items = int(no_of_items)
            if no_of_items <= 0:
                raise ValueError()
        except ValueError:
            return "Invalid item ID or quantity. Please try again."

    cart_item = Cart.query.filter_by(user_id=user_id, item_id=item_id).first()
    if cart_item:
        cart_item.no_of_item = no_of_items
    else:
        cart_item = Cart(user_id=user_id, item_id=item_id, no_of_item=no_of_items)
        db.session.add(cart_item)
    db.session.commit()

    flash('Item added to cart successfully!', 'success')
    return redirect(url_for('views.user_home'))


@views.route('/cart')
@login_required
def cart():
    user_id = current_user.id  

    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = 0.0

    for cart_item in cart_items:
        item = Items.query.get(cart_item.item_id)
        total_price += item.price * cart_item.no_of_item
    total_price=round(total_price, 2)

    items = Items.query.all()

    return render_template('cart.html', cart_items=cart_items, items=items, total_price=total_price)

@views.route('/increase_quantity/<int:item_id>', methods=['POST'])
@login_required
def increase_quantity(item_id):
    user_id = current_user.id  
    no_of_items = int(request.form.get('no_of_items'))

    cart_item = Cart.query.filter_by(user_id=user_id, item_id=item_id).first()
    if cart_item:
        cart_item.no_of_item = no_of_items
        db.session.commit()

    # Redirect back to the cart page
    return redirect(url_for('views.cart'))

@views.route('/delete_item_from_cart/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    user_id = current_user.id  

    cart_item = Cart.query.filter_by(user_id=user_id, item_id=item_id).first()
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

    return redirect(url_for('views.cart'))

@views.route('/search_and_filter_user', methods=['POST'])
@login_required
def search_and_filter():
    search_term = request.form.get('search_term')
    category_search = request.form.get('category_search')
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    min_items_left = request.form.get('min_items_left')
    max_items_left = request.form.get('max_items_left')
    min_expiry = request.form.get('min_expiry')
    max_expiry = request.form.get('max_expiry')

    # Query the items based on the selected filters
    items = Items.query

    filters = {
        'search_term': search_term,
        'category_search': category_search,
        'min_price': min_price,
        'max_price': max_price,
        'min_items_left': min_items_left,
        'max_items_left': max_items_left,
        'min_expiry': min_expiry,
        'max_expiry': max_expiry
    }

    # Apply filters to the query
    items = apply_filters(items, filters)

    # Execute the query to get the filtered items
    filtered_items = items.all()

    # If there is a search term and filtered_items exist, perform search on the filtered results
    if search_term and filtered_items:
        search_term = f'%{search_term}%'  
        filtered_items = Items.query.filter(
            or_(Items.item_name.ilike(search_term), Items.category.ilike(search_term))
        ).all()

    # Render the template with the filtered items and all_categories for the dropdown
    categs = {category: [] for category in set(item.category for item in filtered_items)}
    for item in filtered_items:
        categs[item.category].append(item)

    all_categories = set(item.category for item in Items.query.all())  # Fetch all categories for the dropdown
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    return render_template('user_home.html', categs=categs, all_categories=all_categories,cart_items=cart_items)

@views.route('/buy', methods=['POST'])
@login_required
def buy():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    address = request.form.get('delivery_address')

    # If the cart is empty, show a message and redirect to the cart page
    if not cart_items:
        flash('Your cart is empty. Add items to your cart first.', 'warning')
        return redirect(url_for('views.cart'))

    # Create a new entry in User_History for each cart item and reduce the item quantity
    for cart_item in cart_items:
        item = Items.query.get(cart_item.item_id)

        if cart_item.no_of_item > item.no_of_items_left:
            flash(f"Insufficient quantity available for {item.item_name}. The purchase cannot be completed.", 'danger')
            return redirect(url_for('views.cart'))

        item.no_of_items_left -= cart_item.no_of_item  # Reduce the available quantity
        purchase = User_History(user_id=user_id, item_id=cart_item.item_id, no_of_items=cart_item.no_of_item, date_of_purchase=datetime.now(), address=address)
        db.session.add(purchase)
        db.session.delete(cart_item)  # Remove the item from the cart after purchase

    # Commit changes to the database
    db.session.commit()

    # Show a success message and redirect to the home page
    flash('Thank you for your purchase! Your order will be delivered soon.', 'success')
    return redirect(url_for('views.user_home'))







@views.route('/checkout/<total_price>')
@login_required
def checkout(total_price):

    # Check if the user has any purchase history
    user_history = User_History.query.filter_by(user_id=current_user.id).first()
    first_time_user = True if not user_history else False
    total_price=float(total_price)
    # Apply the 25% discount if it's a first-time user
    if first_time_user:
        total_price *= 0.75  # Apply 25% discount
    total_price=round(total_price,2)
    return render_template('checkout.html', total_price=total_price, first_time_user=first_time_user)
@views.route('/order_history')
@login_required
def order_history():
    user_id = current_user.id  

    # Retrieve the user's order history from the database
    order_history = User_History.query.filter_by(user_id=user_id).order_by(User_History.date_of_purchase.desc()).all()

    return render_template('order_history.html', order_history=order_history)



@views.route("/user_profile", methods=["GET", "POST"])
@login_required
def user_profile():
    if request.method == "POST":
        # Handle user details update
        new_email = request.form.get("email")
        new_first_name = request.form.get("first_name")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        current_password = request.form.get("current_password")

        # Verify current password
        if not check_password_hash(current_user.password, current_password):
            flash("Current password is incorrect. Please try again.", "danger")
            return redirect(url_for("profile.user_profile"))

        # Update user details
        current_user.email = new_email
        current_user.first_name = new_first_name

        # Check if a new password is provided and matches the confirmation
        if new_password and new_password == confirm_password:
            current_user.password = generate_password_hash(new_password)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("views.user_home"))

    return render_template("user_profile.html", user=current_user)


