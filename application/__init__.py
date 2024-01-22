from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from flask_migrate import Migrate


app = Flask(__name__)
CORS(app)
# external 
# postgres://noteapp_2lrf_user:LUHqIe6yNBV8qbMiV3owvCffs0YiUW6E@dpg-cmmvm10l5elc73cen5kg-a.singapore-postgres.render.com/noteapp_2lrf
# Internal 
# postgres://noteapp_2lrf_user:LUHqIe6yNBV8qbMiV3owvCffs0YiUW6E@dpg-cmmvm10l5elc73cen5kg-a/noteapp_2lrf 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://noteapp_2lrf_user:LUHqIe6yNBV8qbMiV3owvCffs0YiUW6E@dpg-cmmvm10l5elc73cen5kg-a/noteapp_2lrf '
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Table 1 for dashboard 

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    para = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Table 2 for User Sign in adn Sign up 
    
class User(db.Model):
    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect({url_for('http://localhost:3000/')})

@app.route('/signup',methods=['POST'])
def signup():
    try:
        user_data = request.get_json()
        email = user_data.get('email')
        password = user_data.get('password')

        # Check if the email is already in use
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create a new user instance
        new_user = User(email=email, password=password)

        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'User': 'Created'})
    except Exception as e:
        return jsonify({'error ayya': str(e)}), 400  # Return a 400 status code for a bad request
    
@app.route('/signin',methods=['POST'])
def signin():
    try:
        login_data = request.get_json()

        # Get email and password from the JSON request
        email = login_data.get('email')
        password = login_data.get('password')

        # Check if the email exists in the database
        user = User.query.filter_by(email=email).first()
        if user:
            # Verify the password (without hashing for demonstration purposes)
            if user.password == password:
                # Include user_id in the response
                # print(user.name)
                response_data = {'message': 'Login successful', 'user_id': user.id,'user_name':user.email}
                return jsonify(response_data)
            else:
                return jsonify({'error': 'Invalid password'}), 401
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/tasks', methods=['GET'])
def get_tasks():
     user_id = request.args.get('user_id')
    #  user_id=7
     if user_id is None:
        return jsonify({'error': 'User ID not provided'}), 400

     tasks = Task.query.filter_by(user_id=user_id).all()
    # tasks = Task.query.all()
     task_list = [{
                    'id':task.id,
                  'date':task.date,
                  'title': task.title,
                  'type':task.type,
                  'para':task.para
                    } for task in tasks]
     return jsonify(task_list)

@app.route("/addnote", methods=['POST'])
def addnote():
    try:
        data = request.get_json()
        print("Received Data:", data)
        user_id = data.get('user_id')
        print("User ID:", user_id)
        if user_id is None:
            return jsonify({'error': 'User ID not provided'}), 400

        new_task = Task(
            date=data['date'],
            title=data['title'],
            type=data['type'],
            para=data['para'],
            user_id=user_id
        )
        print("Task=>",new_task)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task Created'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400  # Return a 400 status code for a bad request


@app.route('/deletenote/<int:task_id>', methods=['DELETE'])
def delete_note(task_id):
    # task = Task.query.get(task_id)
    user_id = request.args.get('user_id')
    if user_id is None:
        return jsonify({'error': 'User ID not provided'}), 400

    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if task:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task Deleted'})
    else:
        return jsonify({'message': 'Task not found'}), 404
    

# if __name__ == '__main__':
#     app.run(debug=True)
