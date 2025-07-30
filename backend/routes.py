from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user,logout_user
import matplotlib
from backend.models import User, ParkingLot, ParkingSpot, ReserveParking, ParkingHistory
from datetime import datetime
from app import app, db
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import io
import base64


def init_routes(app):
    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                flash('Login successful!', 'success')
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid username or password', 'danger')
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            full_name = request.form['full_name']
            email = request.form['email']
            contact = request.form['contact']
            address = request.form['address']
            pincode = request.form['pincode']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists', 'danger')
                return redirect(url_for('register'))
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'danger')
                return redirect(url_for('register'))

            user = User(username=username, email=email, full_name=full_name, address=address, pincode=pincode, contact_number=contact)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('index'))

    @app.route('/user/dashboard')
    @login_required
    def user_dashboard():
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
            
        # Get active reservation
        active_reservation = ReserveParking.query.filter_by(
            user_id=current_user.id, 
            is_active=True
        ).first()
        
        # Get parking history
        parking_history = ParkingHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(ParkingHistory.leaving_timestamp.desc()).all()
        
        return render_template(
            'Users/dashboard.html', 
            active_reservation=active_reservation,
            parking_history=parking_history
        )
        
    
    
    
    
        
    
    @app.route('/admin/dashboard')
    @login_required
    def admin_dashboard():
        parking_lot = ParkingLot.query.all()
        return render_template('admin/dashboard.html', parking_lot=parking_lot)

    @app.route('/admin/add_parking_lot')
    @login_required
    def add_parking_lot():
        
        return render_template('admin/add_parking_lot.html')
    
    @app.route('/admin/add_parking_lot', methods=['POST'])
    @login_required
    def add_parking_lot_post():
        
        prime_location_name = request.form.get('prime_location_name')
        address = request.form.get('address')
        pin_code = request.form.get('pin_code')
        price_per_hour = request.form.get('price_per_hour')
        maximum_number_of_spots = request.form.get('maximum_number_of_spots')
        
        if not prime_location_name or not address or not pin_code or not price_per_hour or not maximum_number_of_spots:
            flash('All fields are required', 'danger')
            return redirect(url_for('add_parking_lot'))
        

        parking_lot = ParkingLot(prime_location_name=prime_location_name, address=address, pin_code=pin_code, price_per_hour=float(price_per_hour), maximum_number_of_spots=int(maximum_number_of_spots))
        db.session.add(parking_lot)
        
        db.session.commit()
        # Create parking spots
        for i in range(1, parking_lot.maximum_number_of_spots + 1):
            spot = ParkingSpot(lot_id=parking_lot.id, spot_number=i)
            db.session.add(spot)
        db.session.commit()
        flash('Parking lot added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    
    @app.route('/admin/view_parking_lot/<int:lot_id>')
    @login_required
    def view_parking_lot(lot_id):   
        parking_lot = ParkingLot.query.get_or_404(lot_id)
        parking_spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        reservations = {
        r.spot_id: r for r in ReserveParking.query.filter_by(is_active=True).all()
    }
        
        return render_template('admin/view_parking_lot.html', parking_lot=parking_lot, parking_spots=parking_spots,reservations=reservations)
    
    @app.route('/admin/edit_parking_lot/<int:lot_id>', methods=['GET', 'POST'])
    @login_required
    def edit_parking_lot(lot_id):
        if not current_user.is_admin:
            return redirect(url_for('user_dashboard'))
            
        lot = ParkingLot.query.get_or_404(lot_id)
        if request.method == 'POST':
            lot.prime_location_name = request.form.get('prime_location_name')
            lot.address = request.form.get('address')
            lot.pin_code = request.form.get('pin_code')
            lot.price_per_hour = float(request.form.get('price_per_hour'))
            new_max_spots = int(request.form.get('maximum_number_of_spots'))
            
            current_spots = len(lot.parking_spots)
            if new_max_spots > current_spots:
                for i in range(current_spots + 1, new_max_spots + 1):
                    spot = ParkingSpot(lot_id=lot.id, spot_number=i)
                    db.session.add(spot)
            elif new_max_spots < current_spots:
                spots_to_remove = lot.parking_spots[new_max_spots:]
                for spot in spots_to_remove:
                    if spot.status == 'O':
                        flash('Cannot reduce spots - some spots are occupied')
                        return redirect(url_for('edit_parking_lot', lot_id=lot_id))
                    db.session.delete(spot)
                    
            lot.maximum_number_of_spots = new_max_spots
            db.session.commit()
            flash('Parking lot updated successfully!')
            return redirect(url_for('admin_dashboard'))
        return render_template('admin/edit_parking_lot.html', lot=lot)
    
    @app.route('/admin/confirm_delete_parking_lot/<int:lot_id>', methods=['GET'])
    @login_required
    def confirm_delete_parking_lot(lot_id):
        if not current_user.is_admin:
            return redirect(url_for('user_dashboard'))
        parking_lot = ParkingLot.query.get_or_404(lot_id)
        return render_template('admin/delete_parking_lot.html', parking_lot=parking_lot)

    
    @app.route('/admin/delete_parking_lot/<int:lot_id>', methods=['POST'])
    @login_required
    def delete_parking_lot(lot_id):
        if not current_user.is_admin:
            return redirect(url_for('user_dashboard'))
            
        lot = ParkingLot.query.get_or_404(lot_id)
        
        # Check for active reservations
        for spot in lot.parking_spots:
            active_reservations = ReserveParking.query.filter_by(
                spot_id=spot.id,
                is_active=True
            ).first()
            
            if active_reservations:
                flash('Cannot delete parking lot - there are active reservations', 'danger')
                return redirect(url_for('admin_dashboard'))
                
            # Delete all historical reservations for this spot
            ReserveParking.query.filter_by(spot_id=spot.id).delete()
            
        # Now safe to delete the parking lot (cascade will handle spots)
        db.session.delete(lot)
        db.session.commit()
        
        flash('Parking lot deleted successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/view_parking_spot/<int:reservation_id>')
    @login_required
    def view_parking_spot(reservation_id):
        reservation = ReserveParking.query.get_or_404(reservation_id)
        Estimated_cost=(datetime.utcnow() - reservation.parking_timestamp).total_seconds() / 3600 * reservation.parking_spot.parking_lot.price_per_hour
        return render_template('admin/view_parking_spot.html',reservation=reservation,Estimated_cost=Estimated_cost)
    
    @app.route('/admin/user_info')
    @login_required
    def user_info():
        if not current_user.is_admin:
            return redirect(url_for('user_dashboard'))
            
        users = User.query.filter(User.id != current_user.id).all()
        return render_template('admin/user_info.html', users=users)
        
    def create_revenue_chart(revenue_by_location):
        plt.figure(figsize=(12, 6))
        locations = list(revenue_by_location.keys())
        revenues = list(revenue_by_location.values())
        
        plt.bar(locations, revenues)
        plt.title('Revenue by Location')
        plt.xlabel('Location')
        plt.ylabel('Revenue ($)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    def create_bookings_chart(bookings_by_location):
         # Bookings Distribution Chart
        plt.figure(figsize=(10, 8))
        locations = list(bookings_by_location.keys())
        bookings = list(bookings_by_location.values())
        
        plt.pie(bookings, labels=locations, autopct='%1.1f%%', startangle=90)
        plt.title('Bookings Distribution by Location')
        plt.axis('equal')
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')
        
    @app.route('/admin/summary')
    @login_required
    def admin_summary():
        if not current_user.is_admin:
            return redirect(url_for('user_dashboard'))
            
        # Get all parking history
        parking_history = ParkingHistory.query.all()
        
        # Calculate overall statistics
        total_revenue = sum(record.parking_cost for record in parking_history)
        total_bookings = len(parking_history)
        
        # Get revenue by location
        revenue_by_location = {}
        for record in parking_history:
            if record.lot_name in revenue_by_location:
                revenue_by_location[record.lot_name] += record.parking_cost
            else:
                revenue_by_location[record.lot_name] = record.parking_cost
                
        # Get bookings by location
        bookings_by_location = {}
        for record in parking_history:
            if record.lot_name in bookings_by_location:
                bookings_by_location[record.lot_name] += 1
            else:
                bookings_by_location[record.lot_name] = 1
                
        # Create revenue chart
        
        revenue_chart= create_revenue_chart(revenue_by_location)
        bookings_chart= create_bookings_chart(bookings_by_location)
        
        
        
        parking_lots = ParkingLot.query.all()
        total_spots = sum(lot.maximum_number_of_spots for lot in parking_lots)
        occupied_spots = ParkingSpot.query.filter_by(status='O').count()
        available_spots = total_spots - occupied_spots
        
        # Calculate average duration
        total_duration = sum((record.leaving_timestamp - record.parking_timestamp).total_seconds() / 3600 
                           for record in parking_history)
        avg_duration = total_duration / total_bookings if total_bookings > 0 else 0
        
        

        return render_template(
            'admin/summary.html',
            total_revenue=round(total_revenue, 2),
            total_bookings=total_bookings,
            total_spots=total_spots,
            occupied_spots=occupied_spots,
            available_spots=available_spots,
            avg_duration=round(avg_duration, 1),
            revenue_chart=revenue_chart,
            bookings_chart=bookings_chart
        )
    @app.route('/admin/records')
    @login_required
    def view_parking_records():
        # Get all parking records with user information
        parking_records = ParkingHistory.query.order_by(ParkingHistory.leaving_timestamp.desc()).all()
        return render_template('admin/records.html', parking_records=parking_records)

    #Users:
    @app.route('/edit_profile')
    @login_required
    def edit_profile():
        return render_template('/Users/edit_profile.html', user=current_user)

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile_post():  

        username = request.form.get('username')
        email = request.form.get('email')
        contact_number = request.form.get('contact')
        cpassword = request.form.get('cpassword')
        password = request.form.get('new_password')
        user = current_user
        if not user.check_password(cpassword):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('edit_profile'))
        if not username or not email or not contact_number:
            flash('All fields are required', 'danger')
            return redirect(url_for('edit_profile'))
        if User.query.filter_by(username=username).first() and username != current_user.username:
            flash("Username already exists. Try some other username", 'danger')
            return redirect(url_for('edit_profile'))
        
        current_user.username = username
        current_user.email = email
        current_user.contact_number = contact_number
        if password:
            current_user.set_password(password)
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    @app.route('/parking-lots')
    @login_required
    def view_parking_lots():
        searchInput= request.args.get('searchInput')
        searchCriteria = request.args.get('searchCriteria')
        if searchCriteria and searchInput:
            if searchCriteria == 'location':
                parking_lots = ParkingLot.query.filter(
                    ParkingLot.prime_location_name.ilike(f'%{searchInput}%')
                ).all()
            elif searchCriteria == 'pincode':
                parking_lots = ParkingLot.query.filter(
                    ParkingLot.pin_code.ilike(f'%{searchInput}%')
                ).all()
            else:
                flash('Invalid search criteria', 'danger')
                return redirect(url_for('view_parking_lots'))
        else:
            parking_lots = ParkingLot.query.all()
        
        # Calculate available spots for each lot
        for lot in parking_lots:
            lot.available_spots = ParkingSpot.query.filter_by(
                lot_id=lot.id, 
                status='A'
            ).count()
            
        return render_template('Users/parking_lots.html', parking_lots=parking_lots, searchInput=searchInput)

    @app.route('/reserve/<int:lot_id>', methods=['GET', 'POST'])
    @login_required
    def reserve_spot(lot_id):
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
            
        active_reservation = ReserveParking.query.filter_by(
            user_id=current_user.id, 
            is_active=True
        ).first()
        if active_reservation:
            flash('You already have an active parking reservation')
            return redirect(url_for('user_dashboard'))
            
        lot = ParkingLot.query.get_or_404(lot_id)
        
        if request.method == 'POST':
            available_spot = ParkingSpot.query.filter_by(
                lot_id=lot_id, 
                status='A'
            ).first()
            
            if not available_spot:
                flash('No parking spots available in this lot')
                return redirect(url_for('view_parking_lots'))
                
            vehicle_number = request.form.get('vehicle_number')
            
            reservation = ReserveParking(
                spot_id=available_spot.id,
                user_id=current_user.id,
                vehicle_number=vehicle_number,
                parking_timestamp=datetime.utcnow()
            )
            
            available_spot.status = 'O'
            
            db.session.add(reservation)
            db.session.commit()
            
            flash('Parking spot reserved successfully!')
            return redirect(url_for('user_dashboard'))
            
        return render_template('Users/reserve.html', lot=lot)
    
    @app.route('/release/<int:reservation_id>',methods=['POST','GET'])
    @login_required
    def release_spot(reservation_id):
        reservation = ReserveParking.query.get_or_404(reservation_id)

        if request.method == 'POST':
            release_time = datetime.utcnow()

            # Duration in hours
            duration = (release_time - reservation.parking_timestamp).total_seconds() / 3600

            # Price per hour
            price_per_hour = reservation.parking_spot.parking_lot.price_per_hour
            cost = round(duration * price_per_hour, 2)

            # Create parking history record
            history = ParkingHistory(
                lot_name=reservation.parking_spot.parking_lot.prime_location_name,
                lot_address=reservation.parking_spot.parking_lot.address,
                spot_number=reservation.parking_spot.spot_number,
                price_per_hour=price_per_hour,
                user_id=reservation.user_id,
                vehicle_number=reservation.vehicle_number,
                parking_timestamp=reservation.parking_timestamp,
                leaving_timestamp=release_time,
                parking_cost=cost
            )
            
            # Update reservation
            reservation.leaving_timestamp = release_time
            reservation.parking_cost = cost 
            reservation.is_active = False

            spot = reservation.parking_spot
            spot.status = 'A'
            
            # Add history record and commit all changes
            db.session.add(history)
            db.session.commit()
            
            flash('Parking spot released successfully!', 'success')
            return redirect(url_for('user_dashboard'))

        current_time = datetime.utcnow()
        Estimated_cost=(datetime.utcnow() - reservation.parking_timestamp).total_seconds() / 3600 * reservation.parking_spot.parking_lot.price_per_hour
        cost_preview = round(Estimated_cost, 2)
        return render_template(
            'Users/release_spot.html',
            reservation=reservation,
            current_time=current_time,
            cost_preview=cost_preview
        )
        
    def create_location_chart(location_stats):    
        plt.figure(figsize=(10, 8))
        locations = list(location_stats.keys())
        values = list(location_stats.values())
        
        plt.pie(values, labels=locations, autopct='%1.1f%%', startangle=90)
        plt.title('Parking Location Distribution', pad=20)
        plt.axis('equal')
        
        # Convert plot to base64 string
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    @app.route('/user/summary')
    @login_required
    def user_summary():
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
            
        # Get all parking history for the user
        parking_history = ParkingHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(ParkingHistory.parking_timestamp.desc()).all()
        
        # Calculate summary statistics
        total_parkings = len(parking_history)
        total_cost = sum(record.parking_cost for record in parking_history)
        total_hours = sum((record.leaving_timestamp - record.parking_timestamp).total_seconds() / 3600 
                         for record in parking_history)
        
        # Get most visited locations
        location_stats = {}
        for record in parking_history:
            location_stats[record.lot_name] = location_stats.get(record.lot_name, 0) + 1
        
        # Create charts
        
        location_chart = create_location_chart(location_stats)
                
        return render_template(
            'Users/summary.html',
            total_parkings=total_parkings,
            total_cost=round(total_cost, 2),
            total_hours=round(total_hours, 1),
            location_chart=location_chart,
            parking_history=parking_history
        )
        
        
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
