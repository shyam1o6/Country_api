from flask import Flask,jsonify,request
from config import Config
from flask_migrate import Migrate
from models import  db,Country,State

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return ' this is main page and this link will provide to <a href="/api/Country">Go to Country API</a>'

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
    #this state method was explain by ai tool due to failure of state with the same country
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
    if 'state' in data:
        country.state = data['state']
    db.session.commit()
    return jsonify(country.to_dict())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)