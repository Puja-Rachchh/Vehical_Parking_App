# app.py
from config import create_app, db, login_manager
from backend.models import User, ParkingLot, ParkingSpot, ReserveParking

app = create_app()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#import routes  # Import routes to register them with the app
if __name__ == '__main__':
    with app.app_context():
        from backend.routes import init_routes
        init_routes(app)
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Creating admin user...")
            admin = User(username='admin', email='admin@example.com',full_name='Admin User', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
        else:
            print(f"Admin  user exists. Admin status: {admin.is_admin}")
    app.run(debug=True)
