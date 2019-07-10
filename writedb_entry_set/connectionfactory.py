import logging
import sys
import psycopg2 as driver
import psycopg2.extensions

class ConnectionFactory(object):

    def __init__(self, host, database, user, password, port):

        self.logger = logging.getLogger("writedb_entry_set")
        self.logger.debug("Initialising connection factory for database", database)

        self.host = host
        self.database = database
        self.port = port
        self.user = user
        self.password = password
        
        self.single_connection = None
        
        self.connections = {}
        self.connection = None

    
    def _connect(self):
        if sys.platform[:4] == 'java':
            conn = driver.connect("jdbc:postgresql://%s:%s/%s" % (self.host, self.port, self.database), self.user, self.password, "org.postgresql.Driver")

        else:
            connect_cmd = "dbname='%s' user='%s' host='%s'" % (self.database, self.user, self.host)
            if self.password:
                # required to handle trusted connection without password
                connect_cmd = connect_cmd + " password='%s'" % self.password

            if self.port:
                # required to connect to non-default postgresql port value e.g. pathdbsrv1b.internal.sanger.ac.uk:10120/bigtest5
                connect_cmd = connect_cmd + " port=%s" % self.port

            conn = driver.connect(connect_cmd);

            self.logger.debug("Opened connection to %s", self.database)

        return conn
    
    def getConnection(self, name = "DEFAULT"):
        if name not in self.connections:
            self.logger.debug ("Can't find connection '%s'. Creating..." % name)
            self.connections[name] = self._connect()
        if self.connections[name].closed != 0:
            self.logger.debug ("Connection '%s' is closed. Reopening..." % name)
            self.connections[name] = self._connect()
        return self.connections[name]
    
    def close(self, name = "DEFAULT"):
        if self.getConnection(name).closed != 1:
            self.getConnection(name).close()
            del self.connections[name]
    
    def reset(self, name = "DEFAULT"):
        self.close(name)
        return self.getConnection(name)
    
    def __repr__(self):
        s = ""
        comma=""
        for att in self.__dict__:
            if att == 'password': continue
            s+= comma + att + ' = "' + str(self.__dict__[att]) + '"'
            comma=", "
        s= "<ConnectionFactory(" + s + ")>"
        return s

