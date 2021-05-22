import socket
import uuid
import os.path
from os import path

class systemInfo:

    uuidFilename = 'uuid.cfg'
    tagFilename = 'tag.cfg'

    def generateUuid(self):
        return str(uuid.uuid4())

    def createUuidIfNotExist(self):
        if not path.exists(self.uuidFilename):
            newUuid = self.generateUuid()
            f_uuid = open(self.uuidFilename,'w')
            f_uuid.write(str(newUuid))
            f_uuid.close()


    def getUuid(self):
        self.createUuidIfNotExist()
        f_uuid = open(self.uuidFilename,'r')
        myUuid = f_uuid.readline()
        f_uuid.close()
        return myUuid

    def getTag(self):
        if path.exists(self.tagFilename):
            f_tag = open(self.tagFilename,'r')
            myTag = f_tag.readline().rstrip()
            f_tag.close()
            return myTag
        else:
            return ""

    def __init__(self):
        self.hostname = socket.gethostname()
        self.uuid = self.getUuid()
        self.deviceTag = self.getTag()
    
