from flask import Flask, render_template, redirect, url_for, send_from_directory, jsonify, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from sqlalchemy import Text, String, ForeignKey, DateTime, select, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from os import path
from datetime import UTC
from datetime import datetime

from app.settings import Config

app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)
app.secret_key = '170dcfee-6d7c-416f-a2b5-25788465f54a'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Product(db.Model):
	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str] = mapped_column(nullable=False)
	description: Mapped[str] = mapped_column(Text, nullable=True)
	price: Mapped[float] = mapped_column(nullable=False)
	file_name: Mapped[str] = mapped_column(String(20), nullable=True)

	orders: Mapped['Order'] = relationship('Order', back_populates='product', uselist=True)


class Order(db.Model):
	id: Mapped[int] = mapped_column(primary_key=True)
	surname: Mapped[str] = mapped_column(String(100), nullable=True)
	name: Mapped[str] = mapped_column(String(100), nullable=True)
	patronymic: Mapped[str] = mapped_column(String(100), nullable=True)
	phone: Mapped[str] = mapped_column(String(20), nullable=True)
	email: Mapped[str] = mapped_column(String(150), nullable=True)
	payment_method: Mapped[str] = mapped_column(String(50), nullable=False)
	delivery_method: Mapped[str] = mapped_column(String(50), nullable=False)
	address: Mapped[str] = mapped_column(String(300), nullable=False)
	product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
	products_count: Mapped[int] = mapped_column(nullable=False)
	order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

	product: Mapped['Product'] = relationship('Product', back_populates='orders', uselist=False)


login_manager = LoginManager()
login_manager.login_view = 'admin_login'


class AdminUser(UserMixin):
	def __init__(self, id):
		self.id = id


@login_manager.user_loader
def load_user(user_id):
	return AdminUser(user_id)


class SecureAdminIndexView(AdminIndexView):
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('admin_login'))


class SecureModelView(ModelView):
	def is_accessible(self):
		return current_user.is_authenticated

	def inaccessible_callback(self, name, **kwargs):
		return redirect(url_for('admin_login'))


class OrderAdminView(SecureModelView):
	can_create = False
	can_edit = False
	column_display_pk = True


login_manager.init_app(app)
admin = Admin(app, name='Администрирование', index_view=SecureAdminIndexView(), template_mode='bootstrap3')
admin.add_view(SecureModelView(Product, db.session, name='Товары'))
admin.add_view(OrderAdminView(Order, db.session, name='Заказы'))

# Пример новостей
news_list = [
	{"id": "1", "title": "Распознавание орхоно-енисейских рунических надписей методами машинного обучения",
	 "content": open(path.join(path.join(app.config['MEDIA_FOLDER'], 'news_texts'), 'news-1.txt'),
					 encoding='utf-8').read(),
	 "date": "2 дня назад"},
	{"id": "2", "title": "Бинарная классификация одним простым искусственным нейроном. 2 часть",
	 "content": open(path.join(path.join(app.config['MEDIA_FOLDER'], 'news_texts'), 'news-2.txt'),
					 encoding='utf-8').read(),
	 "date": "2 дня назад"},
	{"id": "3", "title": "Webhook у Harbor или как я оповещения о пушах docker images нашей команды делал часть — 1",
	 "content": open(path.join(path.join(app.config['MEDIA_FOLDER'], 'news_texts'), 'news-3.txt'),
					 encoding='utf-8').read(),
	 "date": "2 дня назад"},
	{"id": "4", "title": "Event-Driven архитектура на FastAPI: через паттерн Pub/Sub",
	 "content": open(path.join(path.join(app.config['MEDIA_FOLDER'], 'news_texts'), 'news-4.txt'),
					 encoding='utf-8').read()
		, "date": "2 дня назад"},
]


@app.route('/')
def main():
	return redirect(url_for('catalog'))


@app.route('/news')
def news():
	return render_template('news.html', title='Новости', news=news_list)


@app.route('/catalog')
def catalog():
	products = db.session.scalars(select(Product)).all()
	return render_template('catalog.html', title='Каталог', products=products)


@app.route('/delivery')
def delivery():
	return render_template('delivery.html', title='Доставка и оплата')


@app.route('/contacts')
def contacts():
	return render_template('contacts.html', title='Контакты')


@app.route('/order')
def order():
	products = db.session.scalars(select(Product)).all()
	return render_template('order_form.html', title='Новый заказ', products=products)


@app.route('/media/products/<filename>')
def products_media(filename):
	return send_from_directory(path.join(app.config['MEDIA_FOLDER'], 'products_images'), filename)


@app.route('/media/news/<filename>')
def news_media(filename):
	return send_from_directory(path.join(app.config['MEDIA_FOLDER'], 'news_images'), filename)


@app.route('/submit-order', methods=['POST'])
def submit_order():
	try:
		data = request.form

		new_order = Order(
			surname=data.get('surname'),
			name=data['name'],
			patronymic=data.get('patronymic'),
			phone=data.get('phone'),
			email=data.get('email'),
			payment_method=data['payment_method'],
			delivery_method=data['delivery_method'],
			address=data['address'],
			product_id=int(data['product_id']),
			products_count=int(data['products_count']),
			order_date=datetime.now(UTC)
		)

		db.session.add(new_order)
		db.session.commit()

		return jsonify({
			'status': 'success',
			'order_id': new_order.id,
			'message': 'Order created successfully'
		}), 200

	except Exception as e:
		return jsonify({
			'status': 'error',
			'message': str(e)
		}), 400


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')

		# Проверка логина/пароля (замените на свою логику)
		if username == 'admin' and password == 'password':
			user = AdminUser(1)
			login_user(user)
			return redirect(url_for('admin.index'))
		else:
			flash('Неверные учетные данные', 'error')

	return render_template('admin/login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
	logout_user()
	return redirect(url_for('admin_login'))


if __name__ == '__main__':
	app.run(debug=True)
