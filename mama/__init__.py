from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "data.db")
    )

    db = SQLAlchemy(app)

    class Category(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        description = db.Column(db.String(50), unique=True, nullable=False)
        items = db.relationship('Item', backref='category', lazy=True)

    class Item(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        quantity = db.Column(db.Float)
        name = db.Column(db.String(120), unique=True, nullable=False)
        price = db.Column(db.Float)
        category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                                nullable=False)

    # db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
