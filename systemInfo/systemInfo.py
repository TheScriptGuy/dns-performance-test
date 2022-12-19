import socket
import os.path
from os import path

class systemInfo:
    """systemInfo class."""
 
    uuidFilename = 'uuid.cfg'
    tagFilename = 'tag.cfg'

    def getHostname(self):
        """Get the hostname where the script is running from."""
        return socket.gethostname()

    def getUuid(self):
        """Get the uuid."""
        myUuid = ""

        if path.exists(self.uuidFilename):
            f_uuid = open(self.uuidFilename, 'r')
            myUuid = f_uuid.readline()
            f_uuid.close()

        return myUuid

    def getTag(self):
        """Get the tag."""
        myTag = ""
        if path.exists(self.tagFilename):
            f_tag = open(self.tagFilename, 'r')
            myTag = f_tag.readline().rstrip()
            f_tag.close()

        return myTag

    def __init__(self):
        """Initialize all the variables."""
        self.hostname = self.getHostname()
        self.uuid = self.getUuid()
        self.deviceTag = self.getTag()

