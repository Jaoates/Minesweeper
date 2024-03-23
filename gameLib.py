import numpy as np
from blessed import Terminal

class Cursor():
    pos = np.array([0,0])
    def __init__(self,term:Terminal) -> None:
        self.term = term
    
    def __repr__(self) -> str:
        return f"Cursor at {self.pos}"
    
    def setPos(self,*args) -> None:
        try:
            iter(args)
            assert(len(args) == 1)
            self.pos = np.array(args[0])
        except:
            self.pos = np.array([args[0][0],args[0][1]])
            
    def move(self,dir):
        if dir == False:
            pass
        elif dir == "L" and self.pos[0] > 0:
            self.pos += np.array([-1,0])
        elif dir == "R" and self.pos[0] < self.term.width:
            self.pos += np.array([1,0])
        elif dir == "U" and self.pos[1] > 0:
            self.pos += np.array([0,-1])
        elif dir == "D" and self.pos[1] < self.term.height:
            self.pos += np.array([0,1])
    
    def pr(self,characters): # method to print things at the curser
        print(self.term.move_xy(int(self.pos[0]),int(self.pos[1])) + str(characters))


def dPad(term:Terminal,inp):

    d = {
        term.KEY_LEFT: "L",
        term.KEY_RIGHT: "R",
        term.KEY_UP: "U",
        term.KEY_DOWN: "D",
        "d" : "d",
        "f" : "f"
    }
    dir = d.get(inp.code,False)
    if not dir:
        dir = d.get(inp,False)
    return dir
        