from flask import Blueprint,request,jsonify

from controle.authHelpers import authenticateAs
from models.User import User,user_schema,user_schema_many,UserType,getStringFromType

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/getMine', methods=["GET"])
def retrieve_user_data():
    """Retrieves user data

    Returns:
        Http response
    """
    user:User = authenticateAs(request,UserType.Patient)
    if user is None:#Neither patient nor staff nor admin
        return {'error':'Invalid token, or user does not have access to this route!'},403
    
    patient=User.query.filter(User.user_id==user.user_id).first()
    
    return jsonify(user_schema.dump(patient))

@users_bp.route('/getAll', methods=["GET"])
def retrieve_all_users_data():
    """Retrieves all user data, only works if the logged in user is an administrator

    Returns:
        Http response
    """
    user:User = authenticateAs(UserType.Admin)
    if user is None:#Neither staff nor admin
        return {'error':'Invalid token, or user does not have access to this route!'},403
    
    users = User.query.all()
    
    return jsonify(user_schema_many.dump(users))

@users_bp.route('/getPatients', methods=["GET"])
def retrieve_all_patient_data():
    """Retrieves all Patient user data, only works if the logged in user is a staff, for admin users, please refer
    to retrieve_all_user_data() instead.

    Returns:
        Http response
    """
    user:User = authenticateAs(UserType.Staff)
    if user is None:#Neither staff nor admin
        return {'error':'Invalid token, or user does not have access to this route!'},403
    
    users = User.query.filter(User.user_type==getStringFromType(UserType.Patient)).all()
    
    return jsonify(user_schema_many.dump(users))

