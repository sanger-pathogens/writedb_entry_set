import getpass
import os

def get_password(password_key):
    """
        Gets a password, first looking for an environmental variable for it (using the password_key as variable name), and falling back
        to prompting the user for it. 
    """
    password=None
    if password_key in os.environ:
        password = os.environ[password_key]
    if password == None:
        password=getpass.getpass()
    return password

def set_password(password_key, password = None):
    """
        Allows you to store a password for child processes of this process to use. If no password is supplied, then the user will be prompted. It cannot 
        store the password for the parent environment, however.
    """
    if password == None:
        password=getpass.getpass()
    os.putenv(password_key, password)

