from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///glamhub.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(os.path.join(UPLOAD_FOLDER, 'services'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'products'), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-password'
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@glamhub.com'

from models import db, User, Salon, Service, Product, Staff, Booking, Order, OrderItem, CartItem, Review, DeliveryPartner

db.init_app(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'customer_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    
    if Salon.query.count() == 0:
        print("Creating sample data...")
        
        user = User(name='Sample Salon Owner', email='salon@example.com', phone='9876543210', role='salon')
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        salon = Salon(
            user_id=user.id,
            name='Glamour Studio',
            description='Premium beauty and wellness services.',
            address='123 MG Road, Near Phoenix Mall',
            city='Mumbai',
            pincode='400001',
            phone='9876543210',
            image_url='https://images.unsplash.com/photo-1562322140-8baeececf3df?w=800',
            rating=4.8,
            total_reviews=245,
            is_verified=True,
            is_active=True
        )
        db.session.add(salon)
        db.session.flush()
        
        services_data = [
            {'name': 'Premium Haircut', 'category': 'Haircut', 'price': 599, 'duration_minutes': 45, 
             'description': 'Professional haircut'},
            {'name': 'Deep Cleansing Facial', 'category': 'Facial', 'price': 1299, 'duration_minutes': 60,
             'description': 'Deep facial'},
            {'name': 'Full Body Massage', 'category': 'Massage', 'price': 1999, 'duration_minutes': 90,
             'description': 'Relaxing massage'},
        ]
        
        for service_data in services_data:
            service = Service(salon_id=salon.id, **service_data, is_available=True)
            db.session.add(service)
        
        staff_data = [
            {'name': 'Priya Sharma', 'specialization': 'Hair Stylist', 'phone': '9876543221', 'is_available': True},
            {'name': 'Rahul Kumar', 'specialization': 'Makeup Artist', 'phone': '9876543222', 'is_available': True},
        ]
        
        for staff_info in staff_data:
            staff = Staff(salon_id=salon.id, **staff_info)
            db.session.add(staff)
        
        products_data = [
            {'name': 'Moroccan Argan Oil Hair Serum', 'category': 'Hair care', 'price': 899, 'stock': 50,
             'description': 'Premium argan oil'},
            {'name': 'Vitamin C Face Serum', 'category': 'Skin care', 'price': 1299, 'stock': 30,
             'description': 'Brightening serum'},
        ]
        
        for product_data in products_data:
            product = Product(salon_id=salon.id, **product_data, is_available=True)
            db.session.add(product)
        
        db.session.flush()
        
        customer = User(name='Priya Singh', email='customer@example.com', phone='9876543220', role='customer')
        customer.set_password('password123')
        db.session.add(customer)
        db.session.flush()
        
        admin = User(name='Admin', email='admin@glamhub.com', phone='0000000000', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        
        sample_service = Service.query.first()
        sample_staff = Staff.query.first()
        
        if sample_service and sample_staff:
            booking1 = Booking(
                user_id=customer.id,
                salon_id=salon.id,
                service_id=sample_service.id,
                staff_id=sample_staff.id,
                booking_date=(datetime.now() + timedelta(days=2)).date(),
                booking_time=datetime.strptime('14:00', '%H:%M').time(),
                status='pending',
                total_amount=sample_service.price,
                notes='Please use organic products',
                created_at=datetime.utcnow()
            )
            db.session.add(booking1)
            
            second_service = Service.query.offset(1).first() or sample_service
            booking2 = Booking(
                user_id=customer.id,
                salon_id=salon.id,
                service_id=second_service.id,
                staff_id=sample_staff.id,
                booking_date=(datetime.now() + timedelta(days=3)).date(),
                booking_time=datetime.strptime('16:00', '%H:%M').time(),
                status='confirmed',
                total_amount=second_service.price,
                notes='Looking forward!',
                created_at=datetime.utcnow() - timedelta(hours=2)
            )
            db.session.add(booking2)
            
            booking3 = Booking(
                user_id=customer.id,
                salon_id=salon.id,
                service_id=sample_service.id,
                staff_id=sample_staff.id,
                booking_date=(datetime.now() - timedelta(days=5)).date(),
                booking_time=datetime.strptime('11:00', '%H:%M').time(),
                status='completed',
                total_amount=sample_service.price,
                notes='Great!',
                created_at=datetime.utcnow() - timedelta(days=5)
            )
            db.session.add(booking3)
        
        reviews_data = [
            {'user_id': customer.id, 'salon_id': salon.id, 'rating': 5, 'comment': 'Amazing service!'},
        ]
        
        for review_data in reviews_data:
            review = Review(**review_data, created_at=datetime.utcnow())
            db.session.add(review)
        
        order1 = Order(
            user_id=customer.id,
            salon_id=salon.id,
            order_type='delivery',
            status='pending',
            total_amount=2248.0,
            delivery_fee=80.0,
            delivery_address='456 Link Road, Andheri West, Mumbai',
            created_at=datetime.utcnow()
        )
        db.session.add(order1)
        db.session.flush()
        
        product1 = Product.query.first()
        if product1:
            order_item1 = OrderItem(order_id=order1.id, product_id=product1.id, quantity=1, price=product1.price)
            db.session.add(order_item1)
        
        db.session.commit()
        print("✅ Sample data created!")
        print("=" * 60)
        print("Customer: customer@example.com / password123")
        print("Salon: salon@example.com / password123")
        print("Admin: admin@glamhub.com / admin123")
        print("=" * 60)

@app.route('/')
def home():
    salons = Salon.query.filter_by(is_active=True, is_verified=True).order_by(Salon.rating.desc()).limit(6).all()
    return render_template('customer/home.html', salons=salons)

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('customer_register'))
        
        user = User(name=name, email=email, phone=phone, role='customer')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('customer_login'))
    
    return render_template('customer/register.html')

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, role='customer').first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('home'))
        
        flash('Invalid credentials!', 'danger')
    
    return render_template('customer/login.html')

@app.route('/customer/logout')
@login_required
def customer_logout():
    logout_user()
    flash('Logged out!', 'info')
    return redirect(url_for('home'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    city = request.args.get('city', '')
    
    salons_query = Salon.query.filter_by(is_active=True, is_verified=True)
    
    if query:
        salons_query = salons_query.filter(Salon.name.ilike(f'%{query}%'))
    if city:
        salons_query = salons_query.filter(Salon.city.ilike(f'%{city}%'))
    
    salons = salons_query.order_by(Salon.rating.desc()).all()
    
    return render_template('customer/search.html', salons=salons, query=query, city=city)

@app.route('/salon/<int:salon_id>')
def salon_detail(salon_id):
    salon = Salon.query.get_or_404(salon_id)
    services = Service.query.filter_by(salon_id=salon_id, is_available=True).all()
    products = Product.query.filter_by(salon_id=salon_id, is_available=True).all()
    reviews = Review.query.filter_by(salon_id=salon_id).order_by(Review.created_at.desc()).all()
    staff = Staff.query.filter_by(salon_id=salon_id, is_available=True).all()
    
    all_reviews = Review.query.filter_by(salon_id=salon_id).all()
    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for review in all_reviews:
        rating_counts[review.rating] = rating_counts.get(review.rating, 0) + 1
    
    return render_template('customer/salon_detail.html', salon=salon, services=services, products=products, reviews=reviews, staff=staff, rating_counts=rating_counts)

@app.route('/booking/<int:service_id>', methods=['GET', 'POST'])
@login_required
def booking(service_id):
    service = Service.query.get_or_404(service_id)
    salon = service.salon
    staff_list = Staff.query.filter_by(salon_id=salon.id, is_available=True).all()
    
    if request.method == 'POST':
        booking_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        booking_time = datetime.strptime(request.form.get('time'), '%H:%M').time()
        staff_id = request.form.get('staff_id')
        notes = request.form.get('notes', '')
        
        new_booking = Booking(
            user_id=current_user.id,
            salon_id=salon.id,
            service_id=service.id,
            staff_id=staff_id if staff_id else None,
            booking_date=booking_date,
            booking_time=booking_time,
            total_amount=service.price,
            notes=notes,
            status='pending'
        )
        
        db.session.add(new_booking)
        db.session.commit()
        
        flash('Booking created!', 'success')
        return redirect(url_for('booking_success', booking_id=new_booking.id))
    
    return render_template('customer/booking.html', service=service, salon=salon, staff_list=staff_list, datetime=datetime, timedelta=timedelta)

@app.route('/booking/success/<int:booking_id>')
@login_required
def booking_success(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('home'))
    return render_template('customer/booking_success.html', booking=booking)

@app.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('customer/my_bookings.html', bookings=bookings)

@app.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized', 'success': False}), 403
        
        if booking.status not in ['pending', 'confirmed']:
            return jsonify({'error': 'Cannot cancel', 'success': False}), 400
        
        booking.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Booking cancelled'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('customer/cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash('Product added!', 'success')
    return redirect(url_for('cart'))

@app.route('/cart/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('cart'))
    
    action = request.form.get('action')
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
        else:
            db.session.delete(cart_item)
            db.session.commit()
            return redirect(url_for('cart'))
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    
    flash('Item removed!', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Cart is empty!', 'warning')
        return redirect(url_for('cart'))
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        order = Order(
            user_id=current_user.id,
            salon_id=cart_items[0].product.salon_id,
            order_type='delivery',
            status='pending',
            total_amount=total + 50,
            delivery_fee=50,
            delivery_address=f"{name}, {phone}, {address}",
            created_at=datetime.utcnow()
        )
        db.session.add(order)
        db.session.flush()
        
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
        
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        db.session.commit()
        
        flash('Order placed!', 'success')
        return redirect(url_for('order_success', order_id=order.id))
    
    return render_template('customer/checkout.html', cart_items=cart_items, total=total)

@app.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('home'))
    return render_template('customer/order_success.html', order=order)

@app.route('/profile')
@login_required
def profile():
    bookings_count = Booking.query.filter_by(user_id=current_user.id).count()
    orders_count = Order.query.filter_by(user_id=current_user.id).count()
    return render_template('customer/profile.html', bookings_count=bookings_count, orders_count=orders_count)

@app.route('/salon/register', methods=['GET', 'POST'])
def salon_register():
    if request.method == 'POST':
        name = request.form.get('owner_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        salon_name = request.form.get('salon_name')
        description = request.form.get('description')
        address = request.form.get('address')
        city = request.form.get('city')
        pincode = request.form.get('pincode')
        salon_phone = request.form.get('salon_phone')
        
        if User.query.filter_by(email=email).first():
            flash('Email exists!', 'danger')
            return redirect(url_for('salon_register'))
        
        user = User(name=name, email=email, phone=phone, role='salon')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        salon = Salon(
            user_id=user.id,
            name=salon_name,
            description=description,
            address=address,
            city=city,
            pincode=pincode,
            phone=salon_phone,
            is_verified=False,  # Changed to False
            is_active=False      # Changed to False
        )
        db.session.add(salon)
        db.session.commit()
        
        flash('Registration successful! Please wait for admin approval.', 'success')
        return redirect(url_for('salon_login'))
    
    return render_template('salon/register.html')

    
    return render_template('salon/register.html')

@app.route('/salon/login', methods=['GET', 'POST'])
def salon_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, role='salon').first()
        
        if user and user.check_password(password):
            # Check if salon is verified
            salon = Salon.query.filter_by(user_id=user.id).first()
            
            if not salon or not salon.is_verified:
                flash('Your salon is pending admin verification. Please wait for approval.', 'warning')
                return redirect(url_for('salon_login'))
            
            if not salon.is_active:
                flash('Your salon account has been deactivated. Contact admin.', 'danger')
                return redirect(url_for('salon_login'))
            
            login_user(user)
            flash('Welcome!', 'success')
            return redirect(url_for('salon_dashboard'))
        
        flash('Invalid credentials!', 'danger')
    
    return render_template('salon/login.html')


@app.route('/salon/dashboard')
@login_required
def salon_dashboard():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    bookings = Booking.query.filter_by(salon_id=salon.id).order_by(Booking.created_at.desc()).limit(10).all()
    orders = Order.query.filter_by(salon_id=salon.id).order_by(Order.created_at.desc()).limit(10).all()
    total_bookings = Booking.query.filter_by(salon_id=salon.id).count()
    total_orders = Order.query.filter_by(salon_id=salon.id).count()
    completed_bookings = Booking.query.filter_by(salon_id=salon.id, status='completed').all()
    total_revenue = sum(booking.total_amount for booking in completed_bookings)
    
    return render_template('salon/dashboard.html', salon=salon, bookings=bookings, orders=orders, total_bookings=total_bookings, total_orders=total_orders, total_revenue=total_revenue)

@app.route('/salon/logout')
@login_required
def salon_logout():
    logout_user()
    flash('Logged out!', 'info')
    return redirect(url_for('salon_login'))

@app.route('/salon/services')
@login_required
def salon_services():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    services = Service.query.filter_by(salon_id=salon.id).all()
    return render_template('salon/services.html', services=services, salon=salon)

@app.route('/salon/service/add', methods=['GET', 'POST'])
@login_required
def add_service():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'services', filename)
                file.save(filepath)
                image_url = f'/static/uploads/services/{filename}'
        
        service = Service(
            salon_id=salon.id,
            name=request.form.get('name'),
            category=request.form.get('category'),
            price=float(request.form.get('price')),
            duration_minutes=int(request.form.get('duration_minutes')),
            description=request.form.get('description'),
            image_url=image_url,
            is_available=True
        )
        db.session.add(service)
        db.session.commit()
        
        flash('Service added!', 'success')
        return redirect(url_for('salon_services'))
    
    return render_template('salon/add_service.html', salon=salon)

@app.route('/salon/service/edit/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    service = Service.query.get_or_404(service_id)
    
    if service.salon_id != salon.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('salon_services'))
    
    if request.method == 'POST':
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'services', filename)
                file.save(filepath)
                service.image_url = f'/static/uploads/services/{filename}'
        
        service.name = request.form.get('name')
        service.category = request.form.get('category')
        service.price = float(request.form.get('price'))
        service.duration_minutes = int(request.form.get('duration_minutes'))
        service.description = request.form.get('description')
        
        db.session.commit()
        flash('Service updated!', 'success')
        return redirect(url_for('salon_services'))
    
    return render_template('salon/edit_service.html', service=service, salon=salon)

@app.route('/salon/service/delete/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    if current_user.role != 'salon':
        return jsonify({'error': 'Access denied'}), 403
    
    service = Service.query.get_or_404(service_id)
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    
    if service.salon_id != salon.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(service)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/salon/products')
@login_required
def salon_products():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    products = Product.query.filter_by(salon_id=salon.id).all()
    return render_template('salon/products.html', products=products, salon=salon)

@app.route('/salon/product/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'products', filename)
                file.save(filepath)
                image_url = f'/static/uploads/products/{filename}'
        
        product = Product(
            salon_id=salon.id,
            name=request.form.get('name'),
            category=request.form.get('category'),
            price=float(request.form.get('price')),
            stock=int(request.form.get('stock')),
            description=request.form.get('description'),
            image_url=image_url,
            is_available=True
        )
        db.session.add(product)
        db.session.commit()
        
        flash('Product added!', 'success')
        return redirect(url_for('salon_products'))
    
    return render_template('salon/add_product.html', salon=salon)

@app.route('/salon/bookings')
@login_required
def salon_bookings():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    bookings = Booking.query.filter_by(salon_id=salon.id).order_by(Booking.created_at.desc()).all()
    return render_template('salon/bookings.html', bookings=bookings, salon=salon)

@app.route('/salon/booking/accept/<int:booking_id>', methods=['POST'])
@login_required
def accept_booking(booking_id):
    if current_user.role != 'salon':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        salon = Salon.query.filter_by(user_id=current_user.id).first()
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.salon_id != salon.id:
            return jsonify({'error': 'Unauthorized', 'success': False}), 403
        
        booking.status = 'confirmed'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Booking accepted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/salon/booking/reject/<int:booking_id>', methods=['POST'])
@login_required
def reject_booking(booking_id):
    if current_user.role != 'salon':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        salon = Salon.query.filter_by(user_id=current_user.id).first()
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.salon_id != salon.id:
            return jsonify({'error': 'Unauthorized', 'success': False}), 403
        
        booking.status = 'cancelled'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Booking rejected'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/salon/booking/complete/<int:booking_id>', methods=['POST'])
@login_required
def complete_booking(booking_id):
    if current_user.role != 'salon':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        salon = Salon.query.filter_by(user_id=current_user.id).first()
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.salon_id != salon.id:
            return jsonify({'error': 'Unauthorized', 'success': False}), 403
        
        booking.status = 'completed'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Booking completed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/salon/orders')
@login_required
def salon_orders():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    orders = Order.query.filter_by(salon_id=salon.id).order_by(Order.created_at.desc()).all()
    return render_template('salon/orders.html', orders=orders, salon=salon)

@app.route('/salon/staff')
@login_required
def salon_staff():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    staff = Staff.query.filter_by(salon_id=salon.id).all()
    return render_template('salon/staff.html', staff=staff, salon=salon)

@app.route('/salon/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        staff = Staff(
            salon_id=salon.id,
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            specialization=request.form.get('specialization'),
            is_available=True
        )
        db.session.add(staff)
        db.session.commit()
        
        flash('Staff added!', 'success')
        return redirect(url_for('salon_staff'))
    
    return render_template('salon/add_staff.html', salon=salon)

@app.route('/salon/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
@login_required
def edit_staff(staff_id):
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    staff = Staff.query.get_or_404(staff_id)
    
    if staff.salon_id != salon.id:
        flash('Unauthorized!', 'danger')
        return redirect(url_for('salon_staff'))
    
    if request.method == 'POST':
        staff.name = request.form.get('name')
        staff.phone = request.form.get('phone')
        staff.specialization = request.form.get('specialization')
        staff.is_available = request.form.get('is_available') == 'on'
        
        db.session.commit()
        flash('Staff updated!', 'success')
        return redirect(url_for('salon_staff'))
    
    return render_template('salon/edit_staff.html', staff=staff, salon=salon)

@app.route('/salon/staff/delete/<int:staff_id>', methods=['POST'])
@login_required
def delete_staff(staff_id):
    if current_user.role != 'salon':
        return jsonify({'error': 'Access denied'}), 403
    
    staff = Staff.query.get_or_404(staff_id)
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    
    if staff.salon_id != salon.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(staff)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/salon/reviews')
@login_required
def salon_reviews():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    reviews = Review.query.filter_by(salon_id=salon.id).order_by(Review.created_at.desc()).all()
    return render_template('salon/reviews.html', reviews=reviews, salon=salon)

@app.route('/salon/settings')
@login_required
def salon_settings():
    if current_user.role != 'salon':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salon = Salon.query.filter_by(user_id=current_user.id).first()
    return render_template('salon/settings.html', salon=salon)

@app.route('/delivery/register', methods=['GET', 'POST'])
def delivery_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        vehicle_type = request.form.get('vehicle_type')
        vehicle_number = request.form.get('vehicle_number')
        
        if User.query.filter_by(email=email).first():
            flash('Email exists!', 'danger')
            return redirect(url_for('delivery_register'))
        
        user = User(name=name, email=email, phone=phone, role='delivery')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        delivery_partner = DeliveryPartner(
            user_id=user.id,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number,
            is_verified=False,  # Changed to False
            is_active=False      # Changed to False
        )
        db.session.add(delivery_partner)
        db.session.commit()
        
        flash('Registration successful! Please wait for admin approval.', 'success')
        return redirect(url_for('delivery_login'))
    
    return render_template('delivery/register.html')


@app.route('/delivery/login', methods=['GET', 'POST'])
def delivery_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, role='delivery').first()
        
        if user and user.check_password(password):
            # Check if delivery partner is verified
            partner = DeliveryPartner.query.filter_by(user_id=user.id).first()
            
            if not partner or not partner.is_verified:
                flash('Your account is pending admin verification. Please wait for approval.', 'warning')
                return redirect(url_for('delivery_login'))
            
            if not partner.is_active:
                flash('Your account has been deactivated. Contact admin.', 'danger')
                return redirect(url_for('delivery_login'))
            
            login_user(user)
            flash('Welcome!', 'success')
            return redirect(url_for('delivery_dashboard'))
        
        flash('Invalid credentials!', 'danger')
    
    return render_template('delivery/login.html')


@app.route('/delivery/dashboard')
@login_required
def delivery_dashboard():
    if current_user.role != 'delivery':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    total_deliveries = Order.query.filter_by(delivery_partner_id=current_user.id, status='delivered').count()
    today_deliveries = Order.query.filter_by(delivery_partner_id=current_user.id, status='delivered').filter(db.func.date(Order.delivered_at) == datetime.utcnow().date()).count()
    
    return render_template('delivery/dashboard.html', total_deliveries=total_deliveries, today_deliveries=today_deliveries)

@app.route('/delivery/orders')
@login_required
def delivery_orders():
    if current_user.role != 'delivery':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    available_orders = Order.query.filter(Order.status.in_(['pending', 'preparing']), Order.delivery_partner_id.is_(None)).order_by(Order.created_at.desc()).all()
    accepted_orders = Order.query.filter_by(delivery_partner_id=current_user.id, status='out_for_delivery').order_by(Order.created_at.desc()).all()
    completed_orders = Order.query.filter_by(delivery_partner_id=current_user.id, status='delivered').order_by(Order.delivered_at.desc()).limit(10).all()
    
    return render_template('delivery/active_orders.html', available_orders=available_orders, accepted_orders=accepted_orders, completed_orders=completed_orders)

@app.route('/delivery/history')
@login_required
def delivery_history():
    if current_user.role != 'delivery':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    completed_orders = Order.query.filter_by(delivery_partner_id=current_user.id, status='delivered').order_by(Order.delivered_at.desc()).all()
    total_deliveries = len(completed_orders)
    total_earnings = sum(order.delivery_fee for order in completed_orders)
    delivery_partner = DeliveryPartner.query.filter_by(user_id=current_user.id).first()
    avg_rating = delivery_partner.rating if delivery_partner else 0.0
    
    return render_template('delivery/history.html', completed_orders=completed_orders, total_deliveries=total_deliveries, total_earnings=total_earnings, avg_rating=avg_rating)

@app.route('/delivery/earnings')
@login_required
def delivery_earnings():
    if current_user.role != 'delivery':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    completed_orders = Order.query.filter_by(delivery_partner_id=current_user.id, status='delivered').all()
    total_deliveries = len(completed_orders)
    total_earnings = sum(order.delivery_fee for order in completed_orders)
    
    return render_template('delivery/earnings.html', total_deliveries=total_deliveries, total_earnings=total_earnings)

@app.route('/delivery/order/accept/<int:order_id>', methods=['POST'])
@login_required
def accept_delivery_order(order_id):
    if current_user.role != 'delivery':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.status not in ['pending', 'preparing']:
            return jsonify({'error': 'Order not available', 'success': False}), 400
        
        if order.delivery_partner_id is not None:
            return jsonify({'error': 'Already assigned', 'success': False}), 400
        
        order.delivery_partner_id = current_user.id
        order.status = 'out_for_delivery'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order accepted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/delivery/order/reject/<int:order_id>', methods=['POST'])
@login_required
def reject_delivery_order(order_id):
    if current_user.role != 'delivery':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    return jsonify({'success': True, 'message': 'Order rejected'})

@app.route('/delivery/order/complete/<int:order_id>', methods=['POST'])
@login_required
def complete_delivery_order(order_id):
    if current_user.role != 'delivery':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.delivery_partner_id != current_user.id:
            return jsonify({'error': 'Unauthorized', 'success': False}), 403
        
        order.status = 'delivered'
        order.delivered_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order delivered'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/delivery/logout')
@login_required
def delivery_logout():
    logout_user()
    flash('Logged out!', 'info')
    return redirect(url_for('delivery_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email, role='admin').first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        flash('Invalid credentials!', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    total_users = User.query.filter(User.role != 'admin').count()
    total_salons = Salon.query.count()
    total_bookings = Booking.query.count()
    total_orders = Order.query.count()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_salons=total_salons,
                         total_bookings=total_bookings,
                         total_orders=total_orders,
                         recent_bookings=recent_bookings,
                         recent_orders=recent_orders)

@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    users = User.query.filter(User.role != 'admin').all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/salons')
@login_required
def admin_salons():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    salons = Salon.query.all()
    return render_template('admin/salons.html', salons=salons)

@app.route('/admin/bookings')
@login_required
def admin_bookings():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/orders')
@login_required
def admin_orders():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/delivery-partners')
@login_required
def admin_delivery_partners():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('home'))
    
    delivery_partners = DeliveryPartner.query.all()
    return render_template('admin/delivery_partners.html', delivery_partners=delivery_partners)

@app.route('/admin/salon/verify/<int:salon_id>', methods=['POST'])
@login_required
def verify_salon(salon_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        salon = Salon.query.get_or_404(salon_id)
        salon.is_verified = True
        salon.is_active = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Salon verified successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/admin/salon/reject/<int:salon_id>', methods=['POST'])
@login_required
def reject_salon(salon_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        salon = Salon.query.get_or_404(salon_id)
        user = User.query.get(salon.user_id)
        
        # Delete salon and user from database
        db.session.delete(salon)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Salon and user deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/admin/delivery/verify/<int:partner_id>', methods=['POST'])
@login_required
def verify_delivery_partner(partner_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        partner = DeliveryPartner.query.get_or_404(partner_id)
        partner.is_verified = True
        partner.is_active = True
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Delivery partner verified'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/admin/delivery/reject/<int:partner_id>', methods=['POST'])
@login_required
def reject_delivery_partner(partner_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied', 'success': False}), 403
    
    try:
        partner = DeliveryPartner.query.get_or_404(partner_id)
        user = User.query.get(partner.user_id)
        
        # Delete delivery partner and user from database
        db.session.delete(partner)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Delivery partner and user deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out!', 'info')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False') == 'True'
    app.run(debug=debug, host='0.0.0.0', port=port)
