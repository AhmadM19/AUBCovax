from app import db, bcrypt, ma
from models import UserType,getStringFromType

class User(db.Model):
    """SQLalchemy model for users, corresponds to "user" table
    """

    __tablename__ = "user"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    password = db.Column(db.String)
    date_of_birth = db.Column(db.String) #save as something like "dd-mm-yyyy", no need to enforce in db
    id_card = db.Column(db.String,unique=True)
    phone_number = db.Column(db.String,unique=True)
    email = db.Column(db.String,unique=True)
    address = db.Column(db.String)
    condition = db.Column(db.String)

    user_type = db.Column(db.String) #this one is used to diffrentiate between "Admin","Patient","Staff"
    
    def __init__(self,name,password,date_of_birth,id_card,phone_number,email,address,condition) -> None:
        """User constructor, always construct the user as a Patient and encrypts the password

        Args:
            name (str): name
            password (str): password
            date_of_birth (str): date of birth, format as "dd-mm-yyyy"
            id_card (str): id card number
            phone_number (str): phone number
            email (str): email
            address (str): address, format as "city,country"
            condition (str): medical condition(s) of the user
        """
        super(User,self).__init__(name = name,
                                  date_of_birth=date_of_birth,
                                  id_card=id_card,
                                  phone_number=phone_number,
                                  email=email,
                                  address=address,
                                  condition=condition)
        self.password = bcrypt.generate_password_hash(password)
        self.user_type = getStringFromType(UserType.Patient) #always automatically make patient

class UserSchema(ma.Schema):
    """Marshmallow schema to dump User data
    """
    class Meta:
        fields = ("name","date_of_birth", "id_card","phone_number","email","address","condition","user_type")
        model = User

user_schema = UserSchema()
user_schema_many = UserSchema(many=True)