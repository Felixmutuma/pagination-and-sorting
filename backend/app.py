from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # Replace with your DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CORS(app)

# Sample Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    price = db.Column(db.Float)

@app.route('/items', methods=['GET'])
def get_items():
    # Pagination parameters
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))

    # Sorting parameters
    sort_field = request.args.get('sort_field', 'id')  # Default to 'id'
    sort_order = request.args.get('sort_order', 'asc')  # Default to ascending
    
    
    # Query the database
    query = Item.query

    # Apply sorting
    if sort_field == 'name':
        if sort_order == 'asc':
            query = query.order_by(Item.name.asc())  # Alphabetical ascending
        else:
            query = query.order_by(Item.name.desc())  # Alphabetical descending
    else:
        # Default sorting (numeric, e.g., by 'id')
        if sort_order == 'asc':
            query = query.order_by(getattr(Item, sort_field))
        else:
            query = query.order_by(getattr(Item, sort_field).desc())

    # Paginate the results
    paginated_items = query.paginate(page=page, per_page=page_size, error_out=False)
    
    # Format the response
    items = [
        {
            "id": item.id,
            "name": item.name,
            "price": item.price
        }
        for item in paginated_items.items
    ]

    return jsonify({
        "items": items,
        "total": paginated_items.total,
        "pages": paginated_items.pages,
        "current_page": paginated_items.page,
    })


@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()

    new_item = Item(
        name = data['name'],
        price = data['price']
    )

    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message":"Item created successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
