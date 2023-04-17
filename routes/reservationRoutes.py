from flask import Blueprint,request,jsonify

from app import db
from controle.authHelpers import authenticateAs
from controle.reservationHelpers import getSoonestFreeTimeSlot,updateAllOutDatedStates,send_email
from models.User import User,UserType
from models.Reservation import Reservation, ReservationState,reservation_schema,reservation_schema_many,getStringFromState

reservations_bp = Blueprint('reservations', __name__, url_prefix='/reservations')

@reservations_bp.route('/getMine', methods=["GET"])
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

@reservations_bp.route('/create', methods=["POST"])
def create_new_reservation():
    """create second user reservation and confirms dose one, only works if the logged in user is a staff member

    Returns:
        Http response
    """
    updateAllOutDatedStates()#please always call when dealing with reservations to ensure all is up to date, confirms dose 1 
    staff:User = authenticateAs(request,UserType.Staff)

    if staff is None:
        return {'error':'Invalid token, or user does not have access to this route!'},403
    
    body = request.get_json()
    if ("user_id" not in body):
        return {'error':'Missing value!'},400
    
    first_reservation= Reservation.query.filter(Reservation.user_id==body["user_id"]).first()
    if first_reservation.dose_number==1 and first_reservation.reservation_state==getStringFromState(ReservationState.Waiting):
        return {'error':'Dose one is not taken!'},400
    
    else:
        second_reservation = Reservation(getSoonestFreeTimeSlot())
        second_reservation.user_id = body["user_id"]
        second_reservation.dose_number = 2
        db.session.add(second_reservation)
        db.session.commit()
        return {
            "second_reservation":reservation_schema.dump(second_reservation)
        }  

@reservations_bp.route('/sendCertificate', methods=["POST"])
def send_certificate():
    """send vaccination certificate and confirms dose two, only works if the logged in user is a staff member
    Returns:
        Http response
    """
    updateAllOutDatedStates()#Confirms dose two, please always call when dealing with reservations to ensure all is up to date, confirms dose 1 
    staff:User = authenticateAs(request,UserType.Staff)
    
    if staff is None:
        return {'error':'Invalid token, or user does not have access to this route!'},403
    
    body = request.get_json()
    if ("user_id" not in body):
        return {'error':'Missing value!'},400
    
    user=User.query.filter(User.user_id==body["user_id"]).all()
    sencond_reservation= Reservation.query.filter(Reservation.user_id==body["user_id"]).offset(1).limit(1).first()

    if sencond_reservation.dose_number==2 and sencond_reservation.reservation_state==getStringFromState(ReservationState.Waiting):
        return {'error':'Dose Two is not taken!'},400
    else:
        certificate = {
        'vaccine_name': "Pfizer",
        'patient_name': user.name,
        'patient_phone_number': user.phone_number,
        'issued_by': 'AUB Covax'}

        send_email("Vaccination Certificate",user.email,"Dear,"+ {user.name}+"This an automatic email from AUBCovax to verify that you have taken second dose of vaccine"+{certificate})
        return {
            "success":certificate
        }

