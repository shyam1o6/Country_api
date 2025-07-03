from flask import Flask,jsonify,request
from config import Config
from flask_migrate import Migrate
from models import  db,Country,State,User
#this import are for Swagger 
from flask_restx import Api, Resource, fields, Namespace
#this is authienticate part 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
#authenticate part 
app.config['JWT_SECRET_KEY'] = '1234445'
jwt = JWTManager(app)

# Swagger API setup
api = Api(app, title="Country-State API", version="1.0", description="CRUD API with Swagger UI")

# Namespace for countries
ns = api.namespace('countries', description='Country operations')
auth_ns = api.namespace('auth', description='Authentication operations')
#user models
user_model = auth_ns.model('User', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

# Swagger models
state_model = ns.model('State', {
    'name': fields.String(required=True, description='State name')
})

country_model = ns.model('Country', {
    'id': fields.Integer(readonly=True),
    'country': fields.String(required=True, description='Country name'),
    'states': fields.List(fields.String, description='List of state names')
})

# the namesspace routes Routes
@auth_ns.route('/signup')
class Signup(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.get_json()
        hashed_password = generate_password_hash(data['password'])
        new_user = User(username=data['username'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return {"message": "User created Successfully "}, 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and check_password_hash(user.password, data['password']):
            token = create_access_token(identity=user.username)
            return {"access_token": token}
        return {"message": "Invalid credentials please signup if you not did already "}, 401
@auth_ns.route('/secure-data')
class SecureData(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {"message": f"Hello, {current_user}! This is protected data."}

@ns.route('/')
class CountryList(Resource):
    @ns.marshal_list_with(country_model)#decorater 
    def get(self):
        return Country.query.all()

    @ns.expect(country_model)
    @ns.marshal_with(country_model, code=201)
    def post(self):
        data = request.json
        new_country = Country(country=data['country'])
        db.session.add(new_country)
        db.session.commit()

        if 'states' in data:
            for state_name in data['states']:
                state = State(name=state_name, country_id=new_country.id)
                db.session.add(state)
            db.session.commit()
            return new_country, 201

@ns.route('/<int:country_id>')
class CountryItem(Resource):
    @ns.marshal_with(country_model)
    def get(self, country_id):
        """Get a specific country by ID"""
        return Country.query.get_or_404(country_id)

    @ns.expect(country_model)
    @ns.marshal_with(country_model)
    def put(self, country_id):
        """Update a country's name"""
        country = Country.query.get_or_404(country_id)
        data = request.json
        if 'country' in data:
            country.country = data['country']
        db.session.commit()
        return country

    def delete(self, country_id):
        """Delete a country"""
        country = Country.query.get_or_404(country_id)
        db.session.delete(country)
        db.session.commit()
        return {'message': 'Country deleted'}, 204



@app.route('/')
def index():
    return ' this is main page and this link will provide to <a href="/api/Country">Go to Country API</a>andGo to <a href="/docs">/docs</a> to see Swagger UI.'

@app.route('/api/Country')
def country():
    country=Country.query.all()
    return jsonify([con.to_dict() for con in country])

@app.route('/api/Country',methods=['POST'])
def create_country():
    data= request.get_json()
    new_country = Country(country=data['country'])
    db.session.add(new_country)
    db.session.commit()
    if 'states' in data:
        for state_name in data['states']:
            state = State(name=state_name, country_id=new_country.id)
            db.session.add(state)
        db.session.commit()
#till this part but now i understand when this problem i will face again 
    return jsonify(new_country.to_dict()), 201

@app.route('/api/Country/<int:country_id>',methods=['GET'])
def get_country(country_id):
    con=Country.query.get_or_404(country_id)
    return jsonify(con.to_dict())


@app.route('/api/Country/<int:country_id>', methods=['PUT'])
def update_country(country_id):
    data = request.get_json()
    country = Country.query.get_or_404(country_id)
    if 'country' in data:
        country.country = data['country']
    db.session.commit()
    return jsonify(country.to_dict())

@app.route('/api/Country/<int:country_id>', methods=['DELETE'])
def delete_country(country_id):
    country = Country.query.get_or_404(country_id)
    db.session.delete(country)
    db.session.commit()
    return jsonify({"message": "Country deleted"}), 204


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)