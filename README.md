# PySide6 Food Ordering

A desktop food ordering application built with Python and PySide6. This application allows users to browse food menus, manage their shopping cart, place orders, and view order history. Administrators can manage food menus and monitor customer orders.

## Features

### User

- User registration and login
- View available food menus
- Select food quantity
- Add food to shopping cart
- Remove items from cart
- Clear shopping cart
- Add order notes
- Confirm food orders
- View order history
- Cancel pending orders
- Logout

### Admin

- Admin login
- Add new food menus
- Edit food menus
- Delete food menus
- View customer orders
- Update order status
- Cancel orders
- Automatically refresh order data
- Logout

### Shopping Cart

- Add multiple food items
- Manage food quantities
- Automatically calculate total price
- Display total items
- Add order notes
- Confirm orders from the shopping cart

### Order Status

Orders have three possible statuses:

- `Menunggu`
- `Selesai`
- `Dibatalkan`

## Technologies

- Python
- PySide6
- SQLite
- Qt Designer
- PyInstaller

## Project Structure

```text
pyside6-food-ordering/
│
├── __pycache__/
├── build/
├── dist/
├── ui/
│   ├── login.ui
│   ├── admin.ui
│   ├── user.ui
│   ├── cart.ui
│   └── riwayat.ui
│
├── Aplikasi PemesananMakanan.spec
├── data.db
├── database.py
└── main.py
```

## Demo Admin Account

The application includes a default admin account for testing the administrator features.

```text
Username: admin
Password: admin123
Role: Admin
```

## Learning Goals

This project was created to practice and demonstrate:

- Python programming
- Object-oriented programming
- Desktop GUI development
- PySide6
- Qt Designer
- SQLite database integration
- CRUD operations
- User authentication
- Role-based access
- Shopping cart functionality
- Order management
- Database operations
- PyInstaller application packaging
