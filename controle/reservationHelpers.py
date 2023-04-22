import datetime

from flask_mail import Message
from app import mail,db
from models.Reservation import Reservation,ReservationState,getStringFromState


def updateAllOutDatedStates() -> None:
    """This function updates past Reservations and sets them to be fullfilled
    """
    Reservation.query.filter(Reservation.time <= (datetime.datetime.now()-datetime.timedelta(minutes=30)).timestamp(),
                            Reservation.reservation_state==getStringFromState(ReservationState.Waiting)).update(
        dict(reservation_state=getStringFromState(ReservationState.Fullfilled))
    )
    db.session.commit()

def getSoonestFreeTimeSlot() -> int:
    """Returns the timestamp of the earliest available vaccination timeSlot

    Returns:
        int: timestamp of the earliest available vaccination timeSlot
    """
    booked:list[Reservation] = Reservation.query.filter(Reservation.time >= datetime.datetime.now().timestamp()).all()
    booked.sort(key=lambda reservation : reservation.time)

    today = datetime.date.today()
    latestToday = datetime.datetime(today.year,today.month,today.day,hour=17,minute=30) #5:30 pm

    currentSlot = datetime.datetime.fromtimestamp(((datetime.datetime.now().timestamp()+1799)//1800)*1800)#complicated math that rounds to next occurende of 0 minutes or 30 minutes

    if(currentSlot > latestToday):
        today +=datetime.timedelta(days=1)
        currentSlot = datetime.datetime(today.year,today.month,today.day,hour=8)
    reservation_iterator = 0
    
    if len(booked) == 0:
        return currentSlot.timestamp()
    else:
        while currentSlot <= latestToday:#check if a slot is available today
            if len(booked)==reservation_iterator or booked[reservation_iterator].time!=currentSlot.timestamp():
                return currentSlot.timestamp()
            currentSlot += datetime.timedelta(minutes=30)#next slot in time
            reservation_iterator+=1#next reservation

        while True:#keeps checking in future days till it finds a slot
            currentSlot = datetime.datetime(today.year,today.month,today.day,hour=8)# first time slot of the day at 8 am
            for slot in range(0,20):
                if len(booked)==reservation_iterator or booked[reservation_iterator].time!=currentSlot.timestamp():
                    return currentSlot.timestamp()
                currentSlot += datetime.timedelta(minutes=30)#next slot in time
                reservation_iterator+=1#next reservation
            today +=datetime.timedelta(days=1)#next day

from config import GMAIL
def send_email(subject,receipents,body):
    msg = Message(subject, sender=GMAIL, recipients=[receipents])
    msg.body = body
    mail.send(msg)