from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "data.db")
    )

    db = SQLAlchemy(app)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    class Category(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        description = db.Column(db.String(50), unique=True, nullable=False)
        priority = db.Column(db.Integer)
        items = db.relationship('Item', backref='category', lazy=True)

    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        quantity = db.Column(db.Float)
        name = db.Column(db.String(120), unique=True, nullable=False)
        price = db.Column(db.Float)
        done = db.Column(db.Boolean)
        category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                                nullable=False)

    if not os.path.isfile(os.path.join(app.instance_path, 'data.db')):
        db.create_all()

    @app.route('/')
    def index():
        total = 0
        category_list = Category.query.order_by(Category.priority).all()
        data = Item.query.order_by(Item.name).all()

        items = {}
        for row in data:
            category = Category.query.get(row.category_id)
            if category not in items:
                items[category] = []
            items[category].append(row)
            total += row.quantity * row.price

        restructure_items = {}
        for category in category_list:
            restructure_items[category] = items[category]

        total = '{:,.2f}'.format(total)

        return render_template('index.html',
                               items=restructure_items, total=total)

    @app.route('/categories')
    def category():
        categories = Category.query.order_by(Category.priority).all()
        return render_template('category/categories.html',
                               categories=categories)

    @app.route('/add_category', methods=['GET', 'POST'])
    def add_category():
        if request.method == 'POST':
            new_category = Category(
                description=request.form['description'],
                priority=request.form['priority'],
            )
            db.session.add(new_category)
            db.session.commit()

            return redirect(url_for('add_category'))
        else:
            form = {}

        return render_template('category/add_category.html', form=form)

    @app.route('/edit_category/<id>', methods=['GET', 'POST'])
    def edit_category(id):
        form = Category.query.get(id)
        if request.method == 'POST':
            form.description = request.form['description']
            form.priority = request.form['priority']

            db.session.commit()

            return redirect(url_for('category'))

        return render_template('category/edit_category.html', form=form)

    @app.route('/items')
    def item():
        category_list = Category.query.order_by(Category.priority).all()
        data = Item.query.order_by(Item.name).all()
        items = {}
        for row in data:
            category = Category.query.get(row.category_id)
            if category not in items:
                items[category] = []
            items[category].append(row)

        restructure_items = {}
        for category in category_list:
            restructure_items[category] = items[category]

        return render_template('item/items.html',
                               items=restructure_items)

    @app.route('/add_item', methods=['GET', 'POST'])
    def add_item():
        categories = Category.query.order_by(Category.priority).all()
        if request.method == 'POST':
            new_item = Item(
                quantity=float(request.form['quantity']),
                name=request.form['name'],
                price=float(request.form['price']),
                category_id=int(request.form['category_id']),
                done=False
            )
            db.session.add(new_item)
            db.session.commit()

            return redirect(url_for('add_item'))
        else:
            form = {}
        return render_template('item/add_item.html', form=form, categories=categories)

    @app.route('/edit_item/<id>', methods=['GET', 'POST'])
    def edit_item(id):
        categories = Category.query.order_by(Category.priority).all()
        form = Item.query.get(id)
        if request.method == 'POST':
            form.quantity = float(request.form['quantity'])
            form.name = request.form['name']
            form.price = float(request.form['price'])
            form.category_id = int(request.form['category_id'])

            db.session.commit()

            return redirect(url_for('item'))

        return render_template('item/edit_item.html', form=form, categories=categories)

    @app.route('/flip/<id>')
    def flip(id):
        item = Item.query.get(id)
        item.done = not item.done
        db.session.commit()

        return redirect(url_for('index'))

    return app
