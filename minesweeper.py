from blessed import Terminal
from gameLib import *
import copy
import argparse

sprites ={ # stores the sprites we can use in the game
    "RECTANGLE" : chr(int("0x2588",0)),
    "FLAG" : chr(int("0x25B6",0)),
    "BOMB" : chr(int("0x00A4",0)),
    "SWEEPER" : chr(int("0x25AF",0)),
    "BLANK" : chr(int("0x00B7",0)),
    "CLEAR" : chr(int("0x2592",0))
}

def color(r,g,b):
    return {
        "red":r,
        "green":g,
        "blue":b
    }

colors = {
    "RED" : color(255,0,0),
    "GREEN1" : color(100,255,100),
    "GREEN2" : color(20,100,20),
    "GREEN3" : color(110,130,110),
    "BLACK" : color(0,0,0),
    "ORANGE" : color(255,100,20),
    "BLUE" : color(75,150,255),
    "GRAY" : color(150,150,150)
}

class Game():
    running = True
    gameExit = None

    boardCorner = np.array([10,3])
    def __init__(self,term:Terminal,cur:Cursor,boardsize,nBombs:int) -> None:
        self.boardsize = boardsize
        self.nBombs = nBombs
        self.term = term
        self.cur = cur
        self.tiles = [[Tile(np.array([i,j]),self) for i in range(self.boardsize[0])] for j in range(self.boardsize[1])]
        for n in range(nBombs):
            j = np.random.randint(boardsize[1])
            i = np.random.randint(boardsize[0])
            self.tiles[j][i] = Bomb([i,j],self)
    
    def __repr__(self) -> str:
        return f"Game"
    
    def forAllTiles(self,f):
        # applys a function f to all tiles in game
        for row in self.tiles:
            for t in row:
                f(t)
                
    def draw(self):
        game.forAllTiles(lambda x: x.draw(self.cur))

    def onBoard(self,pos):

        # just tells you if a given position is on the board or not
        return pos[0] >= 0 and pos[1] >= 0 and pos[0] < self.boardsize[0] and pos[1] < self.boardsize[1]
    
    def getFlagged(self):
        f = []
        self.forAllTiles(lambda x: f.append(x) if x.isFlagged else None)
        return f
        
    def getBombs(self):
        b = []
        self.forAllTiles(lambda x: b.append(x) if isinstance(x,Bomb) else None)
        return b
    
    def getHidden(self):
        f = []
        self.forAllTiles(lambda x: f.append(x) if not x.isDug else None)
        return f

    def checkWin(self):
        b = self.getBombs()
        f = self.getFlagged()
        h = self.getHidden()
        
        win = False
        if len(f) == self.nBombs:
            win = True
            for fi in f:
                if fi not in b:
                    win = False
        if len(h) == self.nBombs and self.running:
            win = True
        if win:
            self.running = False
            self.gameExit = "WIN"
            
class Tile():
    nAdjBombs = None
    sprite = sprites["BLANK"] # default sprite is rectangle for now
    isBomb = False # default is that its clear
    cScheme = ["GREEN2","GRAY"] # color and on color
    isDug = False
    isFlagged = False

    def __init__(self,pos:np.ndarray,game:Game) -> None:
        self.pos = pos # this is the board position, not the cur position
        self.game = game
    
    def __repr__(self) -> str:
        return f"Tile at {self.pos}"

    def updateSprite(self):
        if self.isFlagged:
            self.sprite = sprites["FLAG"]
            self.cScheme = ["ORANGE","GRAY"]
        elif self.isDug:
            if self.nAdjBombs == 0:
                self.sprite = sprites["CLEAR"]
                self.cScheme = ["GREEN2","GRAY"] # color and on color
            else:
                self.sprite = str(self.nAdjBombs)
                self.cScheme = ["GREEN2","GREEN3"]
        else:
            self.sprite = sprites["BLANK"]

    def draw(self,cur:Cursor):
        cur.setPos(self.pos+self.game.boardCorner)
        termSetColor(self.game.term,self.cScheme)
        cur.pr(self.sprite)

    def getAdjacent(self):
        adj = []
        for i in range(self.pos[0]-1,self.pos[0]+2):
            for j in range(self.pos[1]-1,self.pos[1]+2):
                if game.onBoard([i,j]) and self.game.tiles[j][i] != self:
                    adj.append(self.game.tiles[j][i])
        return adj
    
    def countBombs(self):
        adj = self.getAdjacent()
        self.nAdjBombs = sum([1 if isinstance(a,Bomb) else 0 for a in adj])
    
    def placeFlag(self):
        if not self.isDug:
            self.isFlagged = not self.isFlagged
            
    def dig(self):
        if not self.isFlagged:
            self.isDug = True
            self.updateZeros()
            self.updateSprite()

    def updateZeros(self):
        adj = self.getAdjacent()
        for a in adj:
            if self.nAdjBombs == 0 and not a.isDug:
                a.dig()

    def setDug(self):
        self.isDug = True

class Bomb(Tile):
    isBomb = True
    cScheme = ["GREEN2","GRAY"]

    def __repr__(self) -> str:
        return f"Bomb at {self.pos}"
    
    def dig(self):
        if not self.isFlagged:
            self.isDug = True
            self.updateZeros()
            self.updateSprite()
            self.game.running = False
            self.game.gameExit = "LOSE"
    
    def updateSprite(self):
        if self.isFlagged:
            self.sprite = sprites["FLAG"]
            self.cScheme = ["ORANGE","GRAY"]
        elif self.isDug:
            self.sprite = sprites["BOMB"]
            self.cScheme = ["RED","GRAY"]
        else:
            self.sprite = sprites["BLANK"]

class Sweeper():
    pos = np.array([0,0])
    sprite = sprites["SWEEPER"]
    cScheme = ["GREEN1","GRAY"]

    def __init__(self,game:Game,cur:Cursor) -> None:
        self.game = game
        self.cur = cur

    def __repr__(self) -> str:
        return f"Sweeper at {self.pos}"  
    
    def getTile(self) -> Tile:
        return game.tiles[self.pos[1]][self.pos[0]]
    
    def move(self,inp):
        copypos = copy.deepcopy(self.cur.pos)
        self.cur.move(dPad(term,inp))
        if not game.onBoard(self.cur.pos - self.game.boardCorner):
            self.cur.pos = copypos
        self.pos = self.cur.pos - self.game.boardCorner

    def draw(self):
        self.cur.setPos(self.pos+self.game.boardCorner)
        termSetColor(self.game.term,self.cScheme)
        self.cur.pr(self.sprite)

    def placeFlag(self,inp):
        dir = dPad(self.game.term,inp)
        t = self.getTile()
        if dir == "f":
            t.placeFlag()
            self.game.checkWin()
            
    def dig(self,inp):
        dir = dPad(self.game.term,inp)
        t = self.getTile()
        if dir == "d":
            t.dig()
            self.game.checkWin()

    def handleInp(self,inp):
        self.move(inp)
        self.placeFlag(inp)
        self.dig(inp)
        t = self.getTile()
        t.updateSprite()

def termSetColor(term,cScheme):
    print(term.color_rgb(**colors[cScheme[0]]) + term.on_color_rgb(**colors[cScheme[1]]))

#region parser
parser = argparse.ArgumentParser(description='Intake some optional args.')
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')
parser.add_argument('--large', dest='size', action='store_const',
                    const="large", default="medium",
                    help='large board (default: medium)')
parser.add_argument('--small', dest='size', action='store_const',
                    const="small", default="medium",
                    help='small board (default: medium)')
parser.add_argument('--medium', dest='size', action='store_const',
                    const="medium", default="medium",
                    help='medium board (default: medium)')


parser.add_argument('--hard', dest='difficulty', action='store_const',
                    const="hard", default="hard",
                    help='hard difficulty (default: moderate)')
parser.add_argument('--easy', dest='difficulty', action='store_const',
                    const="easy", default="moderate",
                    help='easy difficulty (default: moderate)')
parser.add_argument('--moderate', dest='difficulty', action='store_const',
                    const="moderate", default="hard",
                    help='moderate difficulty (default: moderate)')

args = parser.parse_args()
boardSize = {
    "small":[10,5],
    "medium":[20,10],
    "large":[40,15]
}[args.size]

nBombs = {
    "easy":.1,
    "moderate":.13,
    "hard":.17
}[args.difficulty]

nBombs = int(boardSize[0]*boardSize[1]*nBombs)

#endregion

term = Terminal()
tileCur = Cursor(term)
playerCur = Cursor(term)
textCur = Cursor(term)
textCur.setPos([0,0])

game = Game(term,tileCur,boardSize,nBombs)
sweeper = Sweeper(game,playerCur)
playerCur.pos = game.boardCorner+np.array([1,1])
textTheme = ["GREEN1","BLACK"]
textWidth = 30

with term.hidden_cursor(), term.cbreak(), term.location():
    game.forAllTiles(lambda x: x.countBombs())
    termSetColor(term,textTheme)
    print(term.clear)
    textCur.pr("MINESWEEPER".ljust(textWidth)+"\n"+"ARROWS - move".ljust(textWidth)+"\n"+"D - dig".ljust(textWidth)+"\n"+"F - flag".ljust(textWidth)+"\n"+"press any key to begin".ljust(textWidth))
    # textCur.pr()
    inp = term.inkey()
    print(term.clear)
    oddloop = True
    # textCur.pr("ARROWS - move".ljust(textWidth)+"\n"+"D - dig".ljust(textWidth)+"\n"+"f - flag".ljust(textWidth))

    while game.running:
        oddloop = not oddloop
        inp = term.inkey(timeout=.1)
        termSetColor(term,["BLACK","BLACK"])
        game.draw()
        
        sweeper.handleInp(inp)
        if oddloop:
            sweeper.draw()
        
        termSetColor(term,textTheme)
        termSetColor(term,textTheme)
        textCur.pr(f"{len(game.getFlagged())} / {len(game.getBombs())}".ljust(textWidth)+"\n"+f" ".ljust(textWidth))
    

    game.forAllTiles(lambda x: x.setDug())
    game.forAllTiles(lambda x: x.updateSprite())
    game.draw()
    termSetColor(term,textTheme)
    textCur.pr("GAME OVER".ljust(textWidth)+"\n"+f"You {game.gameExit}".ljust(textWidth)+"\n"+"press any key to quit".ljust(textWidth))
    inp = term.inkey()
    print(term.normal)
    print(term.clear)

