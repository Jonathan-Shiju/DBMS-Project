from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

class InventoryStatus(enum.Enum):
    ADDED = "added"
    REMOVED = "removed"
    SOLD = "sold"
    IN_STOCK = "in stock"
    EXPIRED = "expired"

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)  # Added phone field
    orders = db.relationship('Order', backref='customer', lazy=True)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_name = db.Column(db.String(100), nullable=False)
    date_prescribed = db.Column(db.String(20), nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)  # Added date field
    total = db.Column(db.Float, nullable=False)  # Added total field
    status = db.Column(db.String(20), nullable=False)  # Added status field
    medicines = db.relationship('Medicine', backref='order', lazy=True)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Added quantity field
    price = db.Column(db.Float, nullable=False)  # Added price field
    inventory_status = db.Column(db.Enum(InventoryStatus), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'phone': c.phone,
        'actions': 'View Orders'
    } for c in customers])

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    new_customer = Customer(name=data['name'], email=data['email'], phone=data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({ 'message': 'Customer added successfully!' })

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.get_json()
    customer = Customer.query.get_or_404(id)
    customer.name = data.get('name', customer.name)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    db.session.commit()
    return jsonify({ 'message': 'Customer updated successfully!' })

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    new_prescription = Prescription(doctor_name=data['doctor_name'], date_prescribed=data['date_prescribed'])
    db.session.add(new_prescription)
    db.session.flush()
    new_order = Order(
        customer_id=data['customer_id'],
        prescription_id=new_prescription.id,
        date=data['date'],
        total=data['total'],
        status=data['status']
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({ 'message': 'Order and Prescription added successfully!' })

@app.route('/orders', methods=['GET'])
def get_orders():
    customer_id = request.args.get('customer_id')
    orders = Order.query.filter_by(customer_id=customer_id).all() if customer_id else Order.query.all()
    return jsonify([{
        'id': o.id,
        'customer_id': o.customer_id,
        'prescription_id': o.prescription_id,
        'date': o.date,
        'total': o.total,
        'status': o.status,
        'actions': 'View Medicines'
    } for o in orders])

@app.route('/medicines', methods=['POST'])
def add_medicine_route():
    data = request.get_json()
    new_medicine = Medicine(
        name=data['name'],
        quantity=data['quantity'],
        price=data['price'],
        inventory_status=InventoryStatus(data['inventory_status']),
        order_id=data['order_id']
    )
    db.session.add(new_medicine)
    db.session.commit()
    return jsonify({ 'message': 'Medicine added successfully!' })

@app.route('/medicines', methods=['GET'])
def get_medicines_route():
    order_id = request.args.get('order_id')
    medicines = Medicine.query.filter_by(order_id=order_id).all() if order_id else Medicine.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'quantity': m.quantity,
        'price': m.price,
        'inventory_status': m.inventory_status.value
    } for m in medicines])

@app.route('/medicines/<int:id>', methods=['PUT'])
def update_inventory(id):
    data = request.get_json()
    medicine = Medicine.query.get_or_404(id)
    medicine.inventory_status = InventoryStatus(data['inventory_status'])
    db.session.commit()
    return jsonify({ 'message': 'Inventory updated successfully!' })

# NEW DELETE Route for medicines:
@app.route('/medicines/<int:id>', methods=['DELETE'])
def delete_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    db.session.delete(medicine)
    db.session.commit()
    return jsonify({ 'message': 'Medicine deleted successfully!' })

@app.route('/prescriptions/<int:id>', methods=['PUT'])
def update_prescription(id):
    data = request.get_json()
    prescription = Prescription.query.get_or_404(id)
    prescription.doctor_name = data.get('doctor_name', prescription.doctor_name)
    prescription.date_prescribed = data.get('date_prescribed', prescription.date_prescribed)
    db.session.commit()
    return jsonify({ 'message': 'Prescription updated successfully!' })

if __name__ == "__main__":
    with app.app_context():  
        db.create_all()
        print("Database and tables created successfully!")
    app.run(debug=True)
