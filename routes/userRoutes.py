from flask import Blueprint,request,jsonify,Response

from controle.authHelpers import authenticateAs
from controle.reservationHelpers import updateAllOutDatedStates
from models.User import User,user_schema,user_schema_many,UserType,getStringFromType
from models.Reservation import Reservation,getStringFromState,ReservationState
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

import datetime

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
    user:User = authenticateAs(request,UserType.Admin)
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
    user:User = authenticateAs(request,UserType.Staff)
    if user is None:#Neither staff nor admin
        return {'error':'Invalid token, or user does not have access to this route!'},403
    
    users = User.query.filter(User.user_type==getStringFromType(UserType.Patient)).all()
    
    return jsonify(user_schema_many.dump(users))

@users_bp.route('/downloadCertificate/<int:requestID>', methods=["GET"])
def retrieve_user_certificate(requestID):
    """Retrieves user certificate, requestID represents which certificate is being retireved

    Returns:
        Http response
    """
    updateAllOutDatedStates()
    user:User = authenticateAs(request,UserType.Patient)
    if user is None:#Neither patient nor staff nor admin
        return {'error':'Invalid token, or user does not have access to this route!'},403
    
    certificate :Reservation = Reservation.query.filter(Reservation.user_id==user.user_id,
                                                        Reservation.reservation_id==requestID,
                                                        Reservation.reservation_state==getStringFromState(ReservationState.Fullfilled)
                                                        ).first()

    if certificate is None:
        return {'error':'Requested certificate does not exist!'},403

    # Create a list of data for the vaccine certificate
    certificate_data = [
        ['Vaccine Name:', "Pfizer"],
        ['Dose Number:',str(certificate.dose_number)],
        ['Patient Name:', user.name],
        ['Issued By:', 'AUB Covax'],
        ['Date:',str(datetime.date.fromtimestamp(certificate.time))]
    ]

    # Create a PDF document
    doc = SimpleDocTemplate("vaccine_certificate.pdf", pagesize=landscape(letter))
    elements = []

    # Create a table to hold the certificate data
    table = Table(certificate_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)

    # Build the PDF document and return it as a response
    doc.build(elements)
    with open("vaccine_certificate.pdf", "rb") as f:
        pdf_data = f.read()
    return Response(pdf_data, content_type='application/pdf')
