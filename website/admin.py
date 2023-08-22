from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Items,User,Cart,User_History
from flask_login import login_required, current_user
from  website.__init__ import db 
from datetime import datetime,date,timedelta
from sqlalchemy import or_
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import pandas as pd
from flask import current_app
admin=Blueprint("admin",__name__)


@admin.route('/admin_home', methods=['GET', 'POST'])
@login_required
def admin_home():
    if request.method == 'POST':
        return search_and_filter()

    # For GET request or when no filters are applied, display all items
    items = Items.query.all()
    categories = set(item.category for item in items if item is not None)
    categs = {category: [] for category in categories}

    # Group items by category
    for item in items:
        if item is not None:
            categs[item.category].append(item)

    # Sort the items within each category
    for category in categs:
        categs[category] = sorted(categs[category], key=lambda x: x.item_name)

    all_categories = set(item.category for item in Items.query.all())  # Fetch all categories for the dropdown


    return render_template('admin_home.html', categs=categs, all_categories=all_categories)


# Edit Category
@admin.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    category = Items.query.get_or_404(category_id)

    if request.method == 'POST':
        new_name = request.form.get('new_name')
        if new_name:
            # Update the category name for all items with the same category
            items_to_update = Items.query.filter_by(category=category.category).all()
            for item in items_to_update:
                item.category = new_name
            db.session.commit()
            flash('Category name updated successfully for all items!', 'success')
            return redirect(url_for('admin.admin_home'))

    return render_template('edit_category.html', category=category)

# Delete Category
@admin.route('/delete_category/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Items.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin.admin_home'))

# Add New Item to Category
# Add New Item to Category
@admin.route('/add_item/<int:category_id>', methods=['GET', 'POST'])
@login_required
def add_item(category_id):
    category = Items.query.get_or_404(category_id)

    if request.method == 'POST':
        item_name = request.form.get('item_name')
        price = float(request.form.get('price'))
        no_of_items_left = int(request.form.get('no_of_items_left'))
        expiry_date_str = request.form.get('expiry_date')
        manufacture_date_str = request.form.get('manufacture_date')
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        manufacture_date = datetime.strptime(manufacture_date_str, '%Y-%m-%d').date()

        # Check if a row with only the category name and other values as NULL exists
        existing_item = Items.query.filter_by(category=category.category).filter_by(item_name=None).first()

        if existing_item:
            # Update the existing row with the new item details
            existing_item.item_name = item_name
            existing_item.price = price
            existing_item.no_of_items_left = no_of_items_left
            existing_item.expiry_date = expiry_date
            existing_item.manufacture_date = manufacture_date
        else:
            # Create a new item
            existing_item = Items.query.filter_by(category=category.category, item_name=item_name).first()

            if existing_item:
                flash('An item with the same name already exists!', 'danger')
            else:
                new_item = Items(
                    category=category.category,
                    item_name=item_name,
                    price=price,
                    no_of_items_left=no_of_items_left,
                    expiry_date=expiry_date,
                    manufacture_date=manufacture_date
                )

                db.session.add(new_item)

        db.session.commit()
        flash('New item added successfully!', 'success')
        return redirect(url_for('admin.admin_home', category_id=category_id))

    return render_template('add_item.html', category=category)

# Edit Item
@admin.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Items.query.get_or_404(item_id)

    if request.method == 'POST':
        item_name = request.form.get('item_name')
        price = float(request.form.get('price'))
        no_of_items_left = int(request.form.get('no_of_items_left'))
        expiry_date_str = request.form.get('expiry_date')
        manufacture_date_str = request.form.get('manufacture_date')

        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        manufacture_date = datetime.strptime(manufacture_date_str, '%Y-%m-%d').date()

        # Check if an item with the same name exists in the database (excluding the current item)
        existing_item = Items.query.filter_by(category=item.category, item_name=item_name).filter(Items.item_id != item_id).first()

        if existing_item:
            flash('An item with the same name already exists!', 'danger')
        else:
            # Update the item details
            item.item_name = item_name
            item.price = price
            item.no_of_items_left = no_of_items_left
            item.expiry_date = expiry_date
            item.manufacture_date = manufacture_date

            db.session.commit()
            flash('Item details updated successfully!', 'success')
            return redirect(url_for('admin.admin_home'))

    return render_template('edit_item.html', item=item)

# Delete Item
@admin.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Items.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('admin.admin_home'))

# Add New Category
@admin.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name')

        new_category = Items(category=category_name)
        db.session.add(new_category)
        db.session.commit()
        flash('New category added successfully!', 'success')
        return redirect(url_for('admin.admin_home'))

    return render_template('add_category.html')

# Helper function to apply filters to the query
def apply_filters(query, filters):
    search_term = filters.get('search_term')

    # Filter by search term (if specified)
    if search_term:
        search_term = f'%{search_term}%'
        query = query.filter(
            or_(Items.item_name.ilike(search_term), Items.category.ilike(search_term))
        )

    # Filter by category (if specified)
    category_search = filters.get('category_search')
    if category_search:
        query = query.filter(Items.category.ilike(f'%{category_search}%'))

    # Filter by price range (if specified)
    min_price = filters.get('min_price')
    if min_price:
        query = query.filter(Items.price >= min_price)

    max_price = filters.get('max_price')
    if max_price:
        query = query.filter(Items.price <= max_price)

    # Filter by items left range (if specified)
    min_items_left = filters.get('min_items_left')
    if min_items_left:
        query = query.filter(Items.no_of_items_left >= min_items_left)

    max_items_left = filters.get('max_items_left')
    if max_items_left:
        query = query.filter(Items.no_of_items_left <= max_items_left)

    # Filter by days to expiry range (if specified)
    min_expiry = filters.get('min_expiry')
    if min_expiry:
        today = date.today()
        query = query.filter(Items.expiry_date >= today + timedelta(days=int(min_expiry)))

    max_expiry = filters.get('max_expiry')
    if max_expiry:
        today = date.today()
        query = query.filter(Items.expiry_date <= today + timedelta(days=int(max_expiry)))

    return query

@admin.route('/search_and_filter', methods=['POST'])
@login_required
def search_and_filter():
    search_term = request.form.get('search_term')
    category_search = request.form.get('category_search')
    filter_type = request.form.get('filter_type')
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
        search_term = f'%{search_term}%'  # Add wildcards before and after the search term
        filtered_items = Items.query.filter(
            or_(Items.item_name.ilike(search_term), Items.category.ilike(search_term))
        ).all()

    # Render the template with the filtered items and all_categories for the dropdown
    categs = {category: [] for category in set(item.category for item in filtered_items)}
    for item in filtered_items:
        categs[item.category].append(item)

    all_categories = set(item.category for item in Items.query.all())  # Fetch all categories for the dropdown

    return render_template('admin_home.html', categs=categs, all_categories=all_categories)

@admin.route('/charts')
@login_required
def charts():
    # Retrieve data from the User_History table
    user_history_data = User_History.query.all()
    data = []
    for entry in user_history_data:
        if entry.item:
            data.append({'category': entry.item.category, 'item_name': entry.item.item_name, 'price': entry.item.price, 'no_of_items': entry.no_of_items})

    # Create a DataFrame from the data
    df = pd.DataFrame(data)

    # Calculate revenue for each item and add it to the DataFrame
    df['revenue'] = df['price'] * df['no_of_items']

    # Calculate total revenue for each category
    category_revenue = df.groupby('category')['revenue'].sum()

    # Calculate total number of items bought for each item
    item_bought_count = df.groupby('item_name')['no_of_items'].sum()

    # Sort the DataFrames in descending order to get the highest values first
    category_revenue = category_revenue.sort_values(ascending=False)
    item_bought_count = item_bought_count.sort_values(ascending=False)

    # Generate the charts
    
    plt.bar(category_revenue.index, category_revenue.values, color='skyblue')
    plt.xlabel('Category')
    plt.ylabel('Revenue')
    plt.title('Highest Revenue-Generating Categories')
    plt.xticks(rotation=30)  # Rotate x-axis labels
    chart_file_path1 = 'website/static/chart1.png'
    plt.savefig(chart_file_path1)
    plt.clf()
    
    
    # Chart 2: Highest bought items (by number of items)
     # Three rows, one column, second position
    plt.bar(item_bought_count.index[:10], item_bought_count.values[:10], color='lightgreen')
    plt.xlabel('Item Name')
    plt.ylabel('Number of Items Bought')
    plt.title('Highest Bought Items (by Number of Items)')
    plt.xticks(rotation=30)  # Rotate x-axis labels
    chart_file_path2 = 'website/static/chart2.png'
    plt.savefig(chart_file_path2)
    plt.clf()

    # Chart 3: Highest revenue-generating items
    highest_revenue_items = df.groupby('item_name')['revenue'].sum().sort_values(ascending=False)[:10] # Three rows, one column, third position
    plt.bar(highest_revenue_items.index, highest_revenue_items.values, color='lightcoral')
    plt.xlabel('Item Name')
    plt.ylabel('Revenue')
    plt.title('Highest Revenue-Generating Items')
    plt.xticks(rotation=30)  # Rotate x-axis labels

    chart_file_path3 = 'website/static/chart3.png'
    plt.savefig(chart_file_path3)
    plt.clf()

    # Render the HTML page with the charts
    return render_template('charts.html', chart_file_path1=url_for('static', filename='chart1.png'), chart_file_path2=url_for('static', filename='chart2.png'), chart_file_path3=url_for('static', filename='chart3.png'))
