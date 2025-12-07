# 💇‍♀️ GlamHub - Salon Booking & Beauty Products Delivery Platform

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**GlamHub** is a comprehensive full-stack web platform that connects customers with salons for beauty services and product delivery. Built with Flask, it features separate portals for customers, salon partners, delivery partners, and administrators.

> **Developed by USH-Studios** 🎨

---

## 🌟 Features

### 👤 Customer Portal
- 🔍 Browse and search salons by location
- 📅 Book salon appointments with preferred staff
- 🛒 Shop beauty products with cart management
- 💳 Checkout with Cash on Delivery (COD)
- 📱 Track bookings and order history
- ⭐ Rate and review salons
- 👤 User profile management

### 🏪 Salon Partner Portal
- 📊 Comprehensive business dashboard
- ✂️ Manage services (add, edit, delete with image uploads)
- 📦 Manage product inventory
- 👥 Manage staff members
- 📅 Accept, reject, or complete bookings
- 📦 Track product orders
- ⭐ View customer reviews
- 💰 Revenue tracking

### 🚚 Delivery Partner Portal
- 📋 View available delivery orders
- ✅ Accept delivery assignments
- 🚗 Mark orders as delivered
- 💰 Track earnings and delivery history
- ⭐ Rating system

### 🔐 Admin Panel
- 👥 Manage all users (customers, salons, delivery partners)
- ✅ Verify/Reject salon registrations
- ✅ Verify/Reject delivery partner registrations
- 📊 Monitor platform statistics
- 📅 Oversee all bookings and orders
- 🏪 View all registered salons

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask 3.0+
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** Flask-Login
- **Password Security:** Werkzeug Security

### Frontend
- **HTML5/CSS3:** Custom responsive design
- **JavaScript:** Vanilla JS for interactive features
- **Fonts:** Google Fonts (Inter)

### Key Libraries
- Flask==3.0.0
- Flask-SQLAlchemy==3.1.1
- Flask-Login==0.6.3
- Flask-Mail==0.9.1
- Werkzeug==3.0.1


## Python app.py

The application will start at `http://127.0.0.1:5000`

---

## 🔑 Demo Credentials

### Admin Access
- **URL:** `http://127.0.0.1:5000/admin/login`
- **Email:** `admin@glamhub.com`
- **Password:** `admin123`

### Customer Account
- **URL:** `http://127.0.0.1:5000/customer/login`
- **Email:** `customer@example.com`
- **Password:** `password123`

### Salon Partner Account
- **URL:** `http://127.0.0.1:5000/salon/login`
- **Email:** `salon@example.com`
- **Password:** `password123`

### Delivery Partner
- **URL:** `http://127.0.0.1:5000/delivery/register`
- **Note:** Register first, then get admin approval

---

## 📋 Database Models

### User
- Multi-role authentication (customer, salon, delivery, admin)
- Secure password hashing
- Profile management

### Salon
- Business information
- Verification status
- Rating system

### Service
- Service offerings with pricing
- Duration and availability
- Image uploads

### Product
- Product catalog with stock management
- Image uploads
- Category organization

### Booking
- Appointment scheduling
- Staff assignment
- Status tracking (pending, confirmed, completed, cancelled)

### Order
- Product orders with delivery
- Status tracking (pending, out_for_delivery, delivered)
- Delivery partner assignment

### Staff
- Salon staff management
- Specialization tracking

### Review
- Customer feedback system
- Star ratings (1-5)

### DeliveryPartner
- Vehicle information
- Verification status
- Rating system

---

## 🔐 Security Features

- ✅ Password hashing with Werkzeug
- ✅ Role-based access control (RBAC)
- ✅ Admin verification for salons and delivery partners
- ✅ Protected routes with Flask-Login
- ✅ Session management
- ✅ SQL injection prevention with SQLAlchemy ORM

---

## 📱 Key Functionalities

### Booking System
1. Customer selects salon and service
2. Chooses preferred date, time, and staff
3. Booking created with pending status
4. Salon accepts/rejects booking
5. Upon completion, customer can leave review

### Order & Delivery System
1. Customer adds products to cart
2. Proceeds to checkout with delivery address
3. Order created with pending status
4. Delivery partner accepts order
5. Status updates: out_for_delivery → delivered
6. Delivery partner earns delivery fee

### Admin Verification Workflow
1. New salon/delivery partner registers
2. Account created but inactive
3. Admin reviews registration
4. Admin approves (activates) or rejects (deletes)
5. Approved users can now login

---

## 🎨 UI/UX Highlights

- 🎯 Modern, clean design with gradient themes
- 📱 Fully responsive for mobile and desktop
- 🎨 Color-coded user interfaces for different portals
- ⚡ Fast loading with optimized CSS
- 🖼️ Image upload support for services and products
- 📊 Dashboard analytics with visual indicators

---

## 🔄 API Endpoints

### Customer Routes
