from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from . import orders
from .. import db
from ..models.order import Order, Cargo, PaymentMethod
from ..models.location import PickupPoint
from ..models.company import InsuranceType

@orders.route('/')
@login_required
def index():
    if current_user.is_admin_user():
        all_orders = Order.query.all()
    else:
        all_orders = Order.query.filter_by(client_id=current_user.id).all()
    return render_template('orders/index.html', orders=all_orders)

@orders.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        # Обработка и валидация данных формы
        payment_method_id = request.form.get('payment_method_id')
        if not payment_method_id:
            flash('Необходимо выбрать способ оплаты', 'danger')
            return redirect(url_for('orders.new'))
            
        pickup_point_id = request.form.get('pickup_point_id')
        if not pickup_point_id:
            flash('Необходимо выбрать пункт выдачи', 'danger')
            return redirect(url_for('orders.new'))
            
        # Для страховки проверяем, была ли она выбрана
        insurance_type_id = request.form.get('insurance_type_id')
        if not insurance_type_id:
            insurance_type_id = None  # Если не выбрано, сохраняем как NULL
                
        # Create new order
        order = Order(
            client_id=current_user.id,
            payment_method_id=int(payment_method_id),
            insurance_type_id=int(insurance_type_id) if insurance_type_id else None,
            pickup_point_id=int(pickup_point_id),
            delivery_address=request.form.get('delivery_address'),
            delivery_date=request.form.get('delivery_date'),
            price=request.form.get('price'),
            notes=request.form.get('notes') or ''
        )
        db.session.add(order)
        db.session.commit()

        # Create cargo items
        cargo_names = request.form.getlist('cargo_name[]')
        cargo_weights = request.form.getlist('cargo_weight[]')
        cargo_volumes = request.form.getlist('cargo_volume[]')
        cargo_types = request.form.getlist('cargo_type[]')
        package_types = request.form.getlist('package_type[]')

        for i in range(len(cargo_names)):
            cargo = Cargo(
                name=cargo_names[i],
                weight=cargo_weights[i],
                volume=cargo_volumes[i],
                order_id=order.id,
                cargo_type=cargo_types[i],
                package_type=package_types[i]
            )
            db.session.add(cargo)

        db.session.commit()
        flash('Заказ успешно создан.')
        return redirect(url_for('orders.view', id=order.id))

    # Get data for form
    payment_methods = PaymentMethod.query.all()
    insurance_types = InsuranceType.query.all()
    pickup_points = PickupPoint.query.all()

    return render_template('orders/new.html',
                         payment_methods=payment_methods,
                         insurance_types=insurance_types,
                         pickup_points=pickup_points)

@orders.route('/<int:id>', methods=['GET'])
@login_required
def view(id):
    order = Order.query.get_or_404(id)
    if not current_user.is_admin_user() and order.client_id != current_user.id:
        flash('У вас нет прав для просмотра этого заказа.')
        return redirect(url_for('orders.index'))
    return render_template('orders/view.html', order=order)

@orders.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    order = Order.query.get_or_404(id)
    if not current_user.is_admin_user() and order.client_id != current_user.id:
        flash('У вас нет прав для редактирования этого заказа.')
        return redirect(url_for('orders.index'))

    if request.method == 'POST':
        # Обработка и валидация данных формы
        payment_method_id = request.form.get('payment_method_id')
        if not payment_method_id:
            flash('Необходимо выбрать способ оплаты', 'danger')
            return redirect(url_for('orders.edit', id=id))
            
        pickup_point_id = request.form.get('pickup_point_id')
        if not pickup_point_id:
            flash('Необходимо выбрать пункт выдачи', 'danger')
            return redirect(url_for('orders.edit', id=id))
            
        # Для страховки проверяем, была ли она выбрана
        insurance_type_id = request.form.get('insurance_type_id')
        
        order.payment_method_id = int(payment_method_id)
        order.insurance_type_id = int(insurance_type_id) if insurance_type_id else None
        order.pickup_point_id = int(pickup_point_id)
        order.delivery_address = request.form.get('delivery_address')
        order.delivery_date = request.form.get('delivery_date')
        order.price = request.form.get('price')
        order.notes = request.form.get('notes') or ''

        # Update cargo items
        cargo_ids = request.form.getlist('cargo_id[]')
        cargo_names = request.form.getlist('cargo_name[]')
        cargo_weights = request.form.getlist('cargo_weight[]')
        cargo_volumes = request.form.getlist('cargo_volume[]')
        cargo_types = request.form.getlist('cargo_type[]')
        package_types = request.form.getlist('package_type[]')

        # Delete removed cargo items
        existing_cargo_ids = [int(id) for id in cargo_ids if id]
        for cargo in order.cargos:
            if cargo.id not in existing_cargo_ids:
                db.session.delete(cargo)

        # Update or create cargo items
        for i in range(len(cargo_names)):
            if cargo_ids[i]:
                # Update existing cargo
                cargo = Cargo.query.get(cargo_ids[i])
                cargo.name = cargo_names[i]
                cargo.weight = cargo_weights[i]
                cargo.volume = cargo_volumes[i]
                cargo.cargo_type = cargo_types[i]
                cargo.package_type = package_types[i]
            else:
                # Create new cargo
                cargo = Cargo(
                    name=cargo_names[i],
                    weight=cargo_weights[i],
                    volume=cargo_volumes[i],
                    order_id=order.id,
                    cargo_type=cargo_types[i],
                    package_type=package_types[i]
                )
                db.session.add(cargo)

        db.session.commit()
        flash('Заказ успешно обновлен.')
        return redirect(url_for('orders.view', id=order.id))

    payment_methods = PaymentMethod.query.all()
    insurance_types = InsuranceType.query.all()
    pickup_points = PickupPoint.query.all()

    return render_template('orders/edit.html',
                         order=order,
                         payment_methods=payment_methods,
                         insurance_types=insurance_types,
                         pickup_points=pickup_points)

@orders.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    order = Order.query.get_or_404(id)
    if not current_user.is_admin_user() and order.client_id != current_user.id:
        flash('У вас нет прав для удаления этого заказа.')
        return redirect(url_for('orders.index'))
        
    db.session.delete(order)
    db.session.commit()
    flash('Заказ успешно удален.')
    return redirect(url_for('orders.index')) 