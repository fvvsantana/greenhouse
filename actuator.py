import numpy as np
import socket

"""
Véi, foca no código


        .---.
       /o   o\
    __(=  "  =)__
     //\'-=-'/\\
        )   (_
       /      `"=-._
      /       \     ``"=.
     /  /   \  \         `=..--.
 ___/  /     \  \___      _,  , `\
`-----' `""""`'-----``"""`  \  \_/
                             `-`

""""""

class Actuator:
    def _init_ (self, type, serialNumber):
        self.type = type
        self.serialNumber = serialNumber
        if type > 3 and type < 8:
            self.ID = type << 5
            if serialNumber < 32 and serialNumber > 0:
                self.ID += serialNumber
            else:
                raise AttributeException("ERROR: Invalid serial number. Must be inbetween 1 to 31")
        else:
            raise AttributeException("ERROR: Invalid type. Must be inbetween 4 to 7")

    
