from flask import Blueprint,request

from app import db,bcrypt
from controle.authHelpers import create_token,authenticateAs
from controle.reservationHelpers import getSoonestFreeTimeSlot,updateAllOutDatedStates
from models.User import User,user_schema,UserType
from models.Reservation import Reservation,reservation_schema

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/signup', methods=["POST"])
def create_user():
    """Creates a new user in the database and books a reservation at the earliest
    possible time for him

    Returns:
        Http response
    """
    body = request.get_json()
    if ("name" not in body)\
        or ("password" not in body)\
        or ("date_of_birth" not in body)\
        or ("id_card" not in body)\
        or ("date_of_birth" not in body)\
        or ("phone_number" not in body)\
        or ("email" not in body)\
        or ("address" not in body)\
        or ("condition" not in body):
        return {'error':'Missing values!'},400
    
    name = body["name"]
    password = body["password"]
    date_of_birth = body["date_of_birth"]
    id_card = body["id_card"]
    phone_number = body["phone_number"]
    email = body["email"]
    address = body["address"]
    condition = body["condition"]

    new_user = User(name,password,date_of_birth,id_card,phone_number,email,address,condition)

    first_reservation = Reservation(getSoonestFreeTimeSlot())
    try:
        db.session.add(new_user)
        db.session.commit()
        first_reservation.user_id = new_user.user_id
        db.session.add(first_reservation)
        db.session.commit()
    except:
        if new_user.user_id != None: #cleanup in case of failure
            db.session.delete(new_user)
            db.session.commit()
        return {'error':'User already exists, or failed to reserve!'},403
    
    #TODO: send an email
    return {
        "user":user_schema.dump(new_user),
        "first_reservation":reservation_schema.dump(first_reservation)
    }

@auth.route('/signin', methods=['POST'])
def get_token():
    """Generates a JWS token to identify the user with the requested credentials, and specifies the user type

    Returns:
        Http response
    """
    body = request.get_json()
    if ("email" not in body) or ("password" not in body):
        return {'error':'Missing values!'},400
    email = body["email"]
    password = body["password"]
    
    user: User = User.query.filter_by(email=email).first()
    if user is None:
        return {'error':'User not found!'},403
    
    if bcrypt.check_password_hash(user.password, password)==False:
        return {'error':'Incorrect password!'},403
    
    token = create_token(user.user_id)

    return {
            "token": token,
            "user_type": user.user_type
            }