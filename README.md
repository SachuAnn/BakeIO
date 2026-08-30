BakeIO
BakeIO is a web-based dessert and bakery marketplace developed using Django. The platform connects customers with local bakeries, allowing users to discover bakeries, explore desserts, add products to their cart, place orders, manage wishlists, and communicate with bakeries.
The platform also provides dedicated functionality for bakery owners and administrators to manage products, orders, users, and platform activities. AI-powered features are included to enhance product discovery and provide personalized recommendations.

 Features
 
 Customer
- User registration and login
- Browse and explore bakeries
- Discover cakes, desserts, and bakery products
- Search for products and bakeries
- View product details
- Add products to cart
- Place and manage orders
- Track orders
- Add products to wishlist
- Manage user profile
- Receive notifications
- Chat with bakeries
- View order and product information

 Bakery
- Manage bakery profile
- Add and manage bakery products
- Update product information
- Manage product categories
- View customer orders
- Manage incoming orders
- Communicate with customers through chat
- Manage bakery-related information

Admin
- Admin dashboard
- Manage users
- Manage bakeries
- Manage products
- Manage orders
- Monitor platform activities
- Manage system data and notifications

 AI Features
- AI-powered product recommendations
- Personalized dessert suggestions
- Intelligent product discovery
- AI-assisted customer experience
- Recommendation features based on user preferences and interactions

Shopping & Ordering
- Browse bakery products
- Product details
- Shopping cart
- Wishlist
- Order placement
- Order management
- Delivery management
- Order-related notifications

 Chat & Communication
- Customer-bakery communication
- Real-time messaging functionality
- Chat management
- Message notifications

 Technologies Used
### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Django

### Database
- SQLite3

### Other Technologies
- Django Templates
- AI-based features
- Media and static file management

## 📂 Project Structure

```text
BAKEIO/
│
├── .vscode/
│
├── ai_features/
│
├── bakeio/
│
├── bakeries/
│
├── cart/
│
├── chat/
│
├── core/
│
├── delivery/
│
├── explore/
│
├── media/
│
├── notifications/
│
├── orders/
│
├── products/
│
├── static/
│   ├── assets/
│   └── css/
│
├── templates/
│   ├── ai_features/
│   ├── bakeries/
│   ├── bakery/
│   ├── cart/
│   ├── chat/
│   ├── core/
│   └── explore/
│
├── users/
│
├── wishlist/
│
├── base.html
├── db.sqlite3
├── fix_template.py
├── manage.py
└── requirements.txt

Main Modules

Module	Description

Admin	Manage users, bakeries, products, orders, and platform activities
Users	Registration, login, profiles, and user management
Bakeries	Browse and manage bakery information
Products	Manage bakery products and desserts
AI Features	AI-powered recommendations and personalized product discovery
Cart	Add, update, and manage products before ordering
Orders	Place and manage customer orders
Wishlist	Save and manage preferred products
Explore	Discover cakes, desserts, and bakery products
Chat	Communication between customers and bakeries
Delivery	Manage delivery-related functionality
Notifications	Provide order and system notifications
Core	Handles common and shared application functionality

 How to Run

Prerequisites
Make sure the following are installed:
•	Python 3.x 
•	Django 
•	Git 
•	Web Browser
Installation
1.	Clone the repository: 
git clone <repository-url>
2.	Navigate to the project directory: 
cd BAKEIO
3.	Create a virtual environment: 
python -m venv venv
4.	Activate the virtual environment. 
Windows:
venv\Scripts\activate
5.	Install the required dependencies: 
pip install -r requirements.txt
6.	Apply database migrations: 
python manage.py migrate
7.	Run the development server: 
python manage.py runserver
8.	Open your browser and visit: 
http://127.0.0.1:8000/
 Admin Panel
Django's administrative interface can be used to manage application data.
Create an admin/superuser using:
python manage.py createsuperuser
Then access the admin panel through:
http://127.0.0.1:8000/admin/


 Application Workflow

Customer
   │
   ├── Browse Bakeries
   │
   ├── Explore Products
   │
   ├── AI Recommendations
   │
   ├── Add to Wishlist
   │
   ├── Add to Cart
   │
   ├── Place Order
   │
   ├── Track Delivery
   │
   └── Chat with Bakery

Bakery
   │
   ├── Manage Profile
   ├── Add Products
   ├── Manage Products
   ├── Manage Orders
   └── Communicate with Customers

Admin
   │
   ├── Manage Users
   ├── Manage Bakeries
   ├── Manage Products
   ├── Manage Orders
   └── Monitor Platform

Project Objective

The main objective of BakeIO is to provide a convenient digital marketplace for discovering and purchasing bakery products while helping local bakeries reach customers online.
The platform combines e-commerce functionality, bakery management, communication features, delivery management, and AI-powered recommendations into a single application.

 Future Enhancements

•	Online payment gateway integration 
•	Advanced AI recommendation system 
•	Real-time delivery tracking 
•	Email and SMS notifications 
•	Customer reviews and ratings 
•	Advanced search and filtering 
•	Bakery analytics dashboard 
•	Mobile application 
•	Improved AI-based personalization

 License
This project was developed for educational and academic purposes.

Developer
Sachu Ann Thomas


