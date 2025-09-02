# Parking Management System

A web-based parking management system built with Flask that allows users to reserve parking spots and administrators to manage parking lots.

## Features

- **User Features:**
  - User registration and authentication
  - View available parking lots
  - Search parking lots by location or pincode
  - Reserve parking spots
  - Release parking spots with cost calculation
  - View parking history and statistics
  - Personal dashboard with active reservations

- **Admin Features:**
  - Manage parking lots (Add, Edit, Delete)
  - Monitor parking spot status
  - View user information
  - Access revenue statistics and analytics
  - View comprehensive booking reports
  - Generate data visualizations

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd 23F3003284_parking_app
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv .venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Make sure your virtual environment is activated


2. Run the application:
   ```bash
   python app.py
   ```

3. Access the application in your web browser:
   ```
   http://localhost:5000
   ```

## Default Admin Account
To use admin account:
Username: admin
Password: admin

## Usage

### For Users
1. Register for a new account
2. Log in with your credentials
3. Browse available parking lots
4. Reserve a parking spot
5. View your active reservations
6. Release spots when done
7. Check your parking history and statistics

### For Administrators
1. Log in with admin credentials
2. Access the admin dashboard
3. Manage parking lots
4. Monitor parking spots
5. View user information
6. Check revenue statistics

## Security Features
- Password hashing
- User session management
- Protected admin routes
- Input validation

## Technology Stack

- **Backend:** Flask
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Login
- **Frontend:** Bootstrap
- **Charts:** Matplotlib
