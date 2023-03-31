from flask import Request
import jwt
import datetime

from models.User import User,UserType,getStringFromType

from config import SECRET_KEY

algorithm='HS256'

def create_token(user_id: int) ->str:
    """Creates a JWT encoded token

    Args:
        user_id (int): signed in user id from the User model

    Returns:
        str: and encoded jwt with 30 days before expiry and storing the user id
    """
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
        'iat': datetime.datetime.utcnow(),
        'sub': user_id
    }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=algorithm
    )

def extract_auth_token(request: Request):
    """Extracts the jwt from the flask request if it exists

    Args:
        request (Request): flask request object

    Returns:
        str: jwt token, None if nonexistant
    """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(" ")[1]
    else:
        return None

def decode_token(token:str) -> int:
    """Retrieves user id stored within a jwt

    Args:
        token (str): jwt token

    Returns:
        int: user id
    """
    payload = jwt.decode(token, SECRET_KEY, algorithm)
    return payload['sub']

def authenticateAs(request: Request, type: UserType) -> User:
    """Authenticates a user as a specific type of user from the request jwt

    Args:
        request (Request): flask request
        type (UserType): user type to authenticate as

    Returns:
        User: User object if authentication as specified type was successfull, None otherwise
    """
    hashed_token = extract_auth_token(request)
    try:
        payload = decode_token(hashed_token)
    except:
        return None

    user: User = User.query.filter(User.user_id==payload,
                                   User.user_type==getStringFromType(type)).first()

    return user #could still be None
