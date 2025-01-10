from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from os import environ

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration       
cloudinary.config( 
    cloud_name = "dnumlnadg", 
    api_key = environ.get('CLOUDINARY_API_KEY'), 
    api_secret = environ.get('CLOUDINARY_API_SECRET'), # Click 'View API Keys' above to copy your API secret
    secure=True
)

# Habilitar CORS para toda la aplicación
CORS(app)

db = SQLAlchemy(app)

# Modelo de Producto
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    supplier = db.Column(db.String(50), nullable=False)
    img = db.Column(db.String(200), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "category": self.category,
            "supplier": self.supplier,
            "img": self.img
        }

# Crear la base de datos y las tablas
with app.app_context():
    db.create_all()


# ruta general
@app.route('/', methods=["GET"])
def home():
    return "Welcome API!"

# Ruta para manejar los productos
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products])

    elif request.method == 'POST':
        data = request.form
        img_file = request.files.get('img')
        print("🚀 ~ img_file:", img_file)

        upload_result = cloudinary.uploader.upload(img_file, folder="imgs-products-store")
        img_path = upload_result["secure_url"]
        print(img_path)

        new_product = Product(
            name=data['name'],
            price=data['price'],
            quantity=data['quantity'],
            category=data['category'],
            supplier=data['supplier'],
            img=img_path
        )
        db.session.add(new_product)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Duplicate entry"}), 400
        return jsonify(new_product.to_dict()), 201

# Ruta para actualizar un producto
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    print("valor de: ", id)
    data = request.get_json()
    product = Product.query.get(id)
    if product:
        product.name = data['name']
        product.price = data['price']
        product.quantity = data['quantity']
        product.category = data['category']
        product.supplier = data['supplier']
        product.img = data['img']
        db.session.commit()
        return jsonify(product.to_dict())
    else:
        return jsonify({"error": "Product not found"}), 404

# Ruta para eliminar un producto
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Product deleted id: {id}"})
    else:
        return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)