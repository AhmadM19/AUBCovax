from flask import Blueprint,request,jsonify

from app import db
from controle.authHelpers import authenticateAs
from controle.reservationHelpers import getSoonestFreeTimeSlot,updateAllOutDatedStates
from models.User import User,UserType
from models.Reservation import Reservation,reservation_schema,reservation_schema_many

reservations_bp = Blueprint('reservations', __name__, url_prefix='/reservations')

@reservations_bp.route('/getmine', methods=["GET"])
def retrieve_current_user_reservations():
    """Retrieves logged in users reservations/certificates, only works for patients

    Returns:
        Http response
    """
    updateAllOutDatedStates()#please always call when dealing with reservations to ensure all is up to date
    user:User = authenticateAs(request,UserType.Patient)
    if user is None:
        return {'error':'Invalid token, or user not a patient!'},403
    
    reservations = Reservation.query.filter(Reservation.user_id==user.user_id).all()
    
    return jsonify(reservation_schema_many.dump(reservations))

@reservations_bp.route('/getByUser', methods=["GET"])
def retrieve_reservations_by_id():
    """Retrieves user reservations/certificates by ID, only works if the logged in user is a staff member
    or an administrator

    Returns:
        Http response
    """
    updateAllOutDatedStates()#please always call when dealing with reservations to ensure all is up to date
    user:User = authenticateAs(request,UserType.Staff)
    if user is None:
        user:User = authenticateAs(UserType.Admin)
    if user is None:#Neither staff nor admin
        return {'error':'Invalid token, or user does not have access to this route!'},403
    
    body = request.get_json()
    if ("user_id" not in body):
        return {'error':'Missing value!'},400
    
    reservations = Reservation.query.filter(Reservation.user_id==body["user_id"]).all()
    
    return jsonify(reservation_schema_many.dump(reservations))

