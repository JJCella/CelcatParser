import celcat

import re
import datetime


a = re.match("!celcat *register", "!celcat register td1")

answer = celcat.process("!celcat 09/01/2019", ["1", "2", "3", "E1", "E2", "E3", "TP1", "TP2", "TP3", "TD1", "TD2"])

print(answer)
