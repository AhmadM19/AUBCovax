from enum import Enum

class UserType(Enum):
    """This class represents the different types of users"""
    Patient = 0
    Staff = 1
    Admin = 2
    Invalid = 3

def getStringFromType(type: UserType) -> str:
    """Function to convert UserType to str for practical reasons

    Args:
        state (UserType): type to be converted

    Returns:
        str: string representation of type, or null if UserType.Invalid
    """
    if(type==UserType.Patient):
        return "Patient"
    if(type==UserType.Staff):
        return "Staff"
    if(type==UserType.Admin):
        return "Admin"
    
def getTypeFromString(str: str)->UserType:
    """Function to convert str to UserType for practical reasons

    Args:
        str (str): string to be converted to type

    Returns:
        UserType: userType corresponding to string, UserType.Invalid if type is invalid
    """
    if(str=="Patient"):
        return UserType.Patient
    if(str=="Staff"):
        return UserType.Staff
    if(str=="Admin"):
        return UserType.Admin
    
    return UserType.Invalid