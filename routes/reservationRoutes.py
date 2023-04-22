from flask import Blueprint,request,jsonify

from app import db
from controle.authHelpers import authenticateAs
from controle.reservationHelpers import getSoonestFreeTimeSlot,updateAllOutDatedStates,send_email
from models.User import User,UserType
from models.Reservation import Reservation, ReservationState,reservation_schema,reservation_schema_many,getStringFromState

import datetime

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
    if ("user_id" not in body)\
        or ("time" not in body):
        return {'error':'Missing value!'},400
    
    user_id = body["user_id"]
    time = body["time"]

    reservations:list[Reservation] = Reservation.query.filter(Reservation.user_id==user_id).all()
    if len(reservations)>1:
        return {'error':'Dose already scheduled!'},400

    reservation_day = datetime.date.fromtimestamp(time)
    
    if reservation_day < datetime.date.fromtimestamp(reservations[0].time)+datetime.timedelta(days=13):
        return {'error':'Second dose need to be at least 2 weeks after first dose!'},400
    
    first_slot_that_day = datetime.datetime(reservation_day.year,reservation_day.month,reservation_day.day,hour=8)

    if (time % 1800 != 0)\
        or (time < first_slot_that_day.timestamp())\
        or (time > first_slot_that_day.timestamp() + 34200):
        return {'error':'Invalid Time Slot!'},400
    
    second_reservation = Reservation(time)
    second_reservation.user_id = user_id
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
    
    user=User.query.filter(User.user_id==body["user_id"]).first()
    sencond_reservation= Reservation.query.filter(Reservation.user_id==body["user_id"],
                                                  Reservation.dose_number==2).first()

    if sencond_reservation is None or sencond_reservation.reservation_state==getStringFromState(ReservationState.Waiting):
        return {'error':'Dose Two is not taken!'},400
    else:
        certificate = {
        'vaccine_name': "Pfizer",
        'patient_name': user.name,
        'patient_phone_number': user.phone_number,
        'Dose Number:':str(sencond_reservation.dose_number),
        'Date:':str(datetime.date.fromtimestamp(sencond_reservation.time)),
        'issued_by': 'AUB Covax'}

        send_email("Vaccination Certificate",user.email,"Dear,"+ {user.name}+"This an automatic email from AUBCovax to verify that you have taken second dose of vaccine"+{certificate})
        return {
            "success":certificate
        }

