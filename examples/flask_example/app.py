"""
Flask example for PayTechUZ.
"""
import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash

# Add parent directory to path to import paytechuz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from paytechuz import create_gateway
from .models import db, Order
from .forms import OrderForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'example-secret-key-for-testing-only'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Payment gateway configuration
PAYME_ID = 'your-payme-id'
PAYME_KEY = 'your-payme-key'
CLICK_SERVICE_ID = 'your-service-id'
CLICK_MERCHANT_ID = 'your-merchant-id'
CLICK_SECRET_KEY = 'your-secret-key'


@app.route('/')
def index():
    """
    Home page.
    """
    return redirect(url_for('order_list'))


@app.route('/orders')
def order_list():
    """
    List all orders.
    """
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('orders/list.html', orders=orders)


@app.route('/orders/create', methods=['GET', 'POST'])
def order_create():
    """
    Create a new order.
    """
    form = OrderForm()
    if form.validate_on_submit():
        order = Order(amount=form.amount.data)
        db.session.add(order)
        db.session.commit()
        flash('Order created successfully!', 'success')
        return redirect(url_for('order_detail', order_id=order.id))
    return render_template('orders/create.html', form=form)


@app.route('/orders/<int:order_id>')
def order_detail(order_id):
    """
    Display order details.
    """
    order = Order.query.get_or_404(order_id)
    return render_template('orders/detail.html', order=order)


@app.route('/orders/<int:order_id>/pay/<string:gateway_type>')
def order_payment(order_id, gateway_type):
    """
    Handle order payment.
    """
    order = Order.query.get_or_404(order_id)
    
    # Create payment gateway
    if gateway_type == 'payme':
        gateway = create_gateway(
            'payme',
            payme_id=PAYME_ID,
            payme_key=PAYME_KEY,
            is_test_mode=True
        )
    elif gateway_type == 'click':
        gateway = create_gateway(
            'click',
            service_id=CLICK_SERVICE_ID,
            merchant_id=CLICK_MERCHANT_ID,
            secret_key=CLICK_SECRET_KEY,
            is_test_mode=True
        )
    else:
        flash('Invalid payment gateway!', 'error')
        return redirect(url_for('order_detail', order_id=order.id))
    
    # Create payment
    callback_url = url_for('payment_callback', order_id=order.id, _external=True)
    return_url = url_for('order_detail', order_id=order.id, _external=True)
    
    payment = gateway.create_payment(
        amount=float(order.amount),
        account_id=order.id,
        description=f"Payment for order #{order.id}",
        return_url=return_url,
        callback_url=callback_url
    )
    
    # Redirect to payment URL
    return redirect(payment['payment_url'])


@app.route('/orders/<int:order_id>/callback', methods=['GET', 'POST'])
def payment_callback(order_id):
    """
    Handle payment callbacks.
    """
    order = Order.query.get_or_404(order_id)
    
    # In a real application, you would check the payment status
    # and update the order accordingly
    
    if request.method == 'POST':
        # This would be called by the payment gateway
        return {'status': 'success'}
    
    return redirect(url_for('order_detail', order_id=order.id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
