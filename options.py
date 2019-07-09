import os
import configparser

from password import get_password

class OptionException(Exception):
    """
        An error parsing options.
    """
    def __init__(self, value, code):
        self.value = value
        self.code = code
    
    def __str__(self):
        return repr({ "value": self.value , "code" : self.code})
    
    def __repr__(self):
        return "<ServerException(%s,%s,%s)" % (self.value, self.code)


def parse_database_uri(uri):
    
    host = "" #@UnusedVariable
    port = 0
    database = ""
    user = ""
    
    if "/" not in uri:
        raise OptionException("Invalid database uri '%s'. Please provide a database uri in the form of 'localhost:5432/database?user'." % uri)
    
    split = uri.split("/")
    
    host = split[0]
    if ":" in split[0]:
        (host, port) = split[0].split(":")
    
    
    if "?" in split[1]:
        (database, user) = split[1].split("?")
    else:
        raise OptionException("Must provide a user name in '%s'. Please provide a database uri in the form of 'localhost:5432/database?user'." % uri)
    
    return (host, port, database, user)

