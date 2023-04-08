from app import db, ma
from enum import Enum

class ReservationState(Enum):
    """This class represents the different states for a reservation"""
    Waiting = 0
    Fullfilled = 1

def getStringFromState(state: ReservationState) -> str:
    """Function to convert ReservationState to str for practical reasons

    Args:
        state (UserType): state to be converted

    Returns:
        str: string representation of state
    """
    if(state==ReservationState.Waiting):
        return "Waiting"
    if(state==ReservationState.Fullfilled):
        return "Fullfilled"
    
def getStateFromString(str: str)->ReservationState:
    """Function to convert str to ReservationState for practical reasons

    Args:
        str (str): string to be converted to state

    Returns:
        ReservationState: reservation state corresponding to string
    """
    if(str=="Waiting"):
        return ReservationState.Waiting
    if(str=="Fullfilled"):
        return ReservationState.Fullfilled

class Reservation(db.Model):
    """SQLalchemy model for reservations, corresponds to "reservation" table
    """

    __tablename__ = "reservation"

    reservation_id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)  #as timestamp (a timestamp is the number of seconds since 1/1/1970 at 12:00 am GMT)
    user_id = db.Column(db.Integer,db.ForeignKey("user.user_id"))

    reservation_state = db.Column(db.String) #this one is used to diffrentiate between "Waiting" and "Fullfilled" (Fullfilled also means has a certificate)
    
    def __init__(self,date,slot,user_id) -> None:
        super(Reservation,self).__init__(date=date,
                                         slot=slot,
                                         user_id=user_id)
        self.reservation_state = getStringFromState(ReservationState.Waiting) #always automatically set "Waiting"

class ReservationSchema(ma.Schema):
    """Marshmallow schema to dump Reservation data
    """
    class Meta:
        fields = ("time","user_id","reservation_state")
        model = Reservation

reservation_schema_schema = ReservationSchema()
reservation_schema_many = ReservationSchema(many=True)
