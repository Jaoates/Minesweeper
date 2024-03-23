from blessed import Terminal
from gameLib import *
import copy
import argparse

# globally used sprites for game
sprites ={ # stores the sprites we can use in the game
    "RECTANGLE" : chr(int("0x2588",0)),
    "FLAG" : chr(int("0x25B6",0)),
    "BOMB" : chr(int("0x00A4",0)),
    "SWEEPER" : chr(int("0x25AF",0)),
    "BLANK" : chr(int("0x00B7",0)),
    "CLEAR" : chr(int("0x2592",0))
}
# helper to make color dicts
def color(r,g,b):
    return {
        "red":r,
        "green":g,
        "blue":b
    }

# globally used colors for game
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

# game class, holds board and some other game state
class Game():
    running = True
    gameExit = None
    # defines the upper left corner of the gameboard in the terminal, units of terminal chars
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
        # calls draw for all tiles in the board
        game.forAllTiles(lambda x: x.draw(self.cur))

    def onBoard(self,pos):
        # just tells you if a given position is on the board or not
        return pos[0] >= 0 and pos[1] >= 0 and pos[0] < self.boardsize[0] and pos[1] < self.boardsize[1]
    
    def getFlagged(self):
        # returns a list of all tiles which are flagged on the board
        f = []
        self.forAllTiles(lambda x: f.append(x) if x.isFlagged else None)
        return f
        
    def getBombs(self):
        # returns all tiles which are Bombs on the board
        b = []
        self.forAllTiles(lambda x: b.append(x) if isinstance(x,Bomb) else None)
        return b
    
    def getHidden(self):
        # returns all tiles which are not yet revealed
        h = []
        self.forAllTiles(lambda x: h.append(x) if not x.isDug else None)
        return h

    def checkWin(self):
        # checks if the game has been one based on the board state
        b = self.getBombs()
        f = self.getFlagged()
        h = self.getHidden()
        
        win = False
        if len(f) == self.nBombs: # if the number flags matches the number of bombs...
            win = True
            for fi in f:
                if fi not in b: # as long as no flags are placed on non-bombs
                    win = False
        if len(h) == self.nBombs and self.running: # if you havent lost and there are as many hidden tiles as bombs
            win = True
        if win:
            self.running = False
            self.gameExit = "WIN"
            
class Tile():
    nAdjBombs = None # number of adjcent bombs is initiallied to None
    sprite = sprites["BLANK"] # default sprite is rectangle for now
    isBomb = False # default is that its clear
    cScheme = ["GREEN2","GRAY"] # color and on color
    isDug = False # tiles start hidden
    isFlagged = False # Tiles start unflagged

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
            if self.nAdjBombs == 0: # set the sprite to a safe square with no adjacent bombs
                self.sprite = sprites["CLEAR"]
                self.cScheme = ["GREEN2","GRAY"] # color and on color
            else:
                self.sprite = str(self.nAdjBombs) # set the sprite to an a number character based on 
                self.cScheme = ["GREEN2","GREEN3"]
        else:
            self.sprite = sprites["BLANK"]
            self.cScheme = ["GREEN2","GRAY"]

    def draw(self,cur:Cursor):
        cur.setPos(self.pos+self.game.boardCorner) # set the position of the cursor
        termSetColor(self.game.term,self.cScheme)
        cur.pr(self.sprite) # print a sprite at the cursor

    def getAdjacent(self):
        # returns all tiles adjacent to this one should be between 3 (corner) and 8 (center)
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
        # recurive function for digging all tiles which have zero adjacent bombs
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
        # same method but with BOMB sprite, should probably refactor this bc its gross but whatever
        if self.isFlagged:
            self.sprite = sprites["FLAG"]
            self.cScheme = ["ORANGE","GRAY"]
        elif self.isDug:
            self.sprite = sprites["BOMB"]
            self.cScheme = ["RED","GRAY"]
        else:
            self.sprite = sprites["BLANK"]
            self.cScheme = ["GREEN2","GRAY"]

class Sweeper():
    # the player sprite
    pos = np.array([0,0])
    sprite = sprites["SWEEPER"]
    cScheme = ["GREEN1","GRAY"]

    def __init__(self,game:Game,cur:Cursor) -> None:
        self.game = game
        self.cur = cur

    def __repr__(self) -> str:
        return f"Sweeper at {self.pos}"  
    
    def getTile(self) -> Tile:
        # gets the tile under the Sweeper
        return game.tiles[self.pos[1]][self.pos[0]]
    
    def move(self,inp):
        # move the cursor if it wont move it off the board
        # this is pretty disgusting but i don't care
        copypos = copy.deepcopy(self.cur.pos)
        self.cur.move(dPad(term,inp))
        if not game.onBoard(self.cur.pos - self.game.boardCorner):
            self.cur.pos = copypos
        self.pos = self.cur.pos - self.game.boardCorner

    def draw(self):
        # draw the cursor
        self.cur.setPos(self.pos+self.game.boardCorner)
        termSetColor(self.game.term,self.cScheme)
        self.cur.pr(self.sprite)

    def placeFlag(self,inp):
        # handles an input and invokes the Tile.placeflag() method if it is relevant
        dir = dPad(self.game.term,inp)
        t = self.getTile()
        if dir == "f":
            t.placeFlag()
            self.game.checkWin()
            
    def dig(self,inp):
        # same as placeFlag() for digging
        dir = dPad(self.game.term,inp)
        t = self.getTile()
        if dir == "d":
            t.dig()
            self.game.checkWin()

    def handleInp(self,inp):
        # handles user input
        self.move(inp)
        self.placeFlag(inp)
        self.dig(inp)
        t = self.getTile()
        t.updateSprite()

def termSetColor(term,cScheme):
    #helper to set terminal colors using the colors dict
    print(term.color_rgb(**colors[cScheme[0]]) + term.on_color_rgb(**colors[cScheme[1]]))

#region parser
# this region handles comandline arguments for difficulty and board size
parser = argparse.ArgumentParser(description='Intake some optional args.')
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

# set up the game cursors
term = Terminal()
tileCur = Cursor(term)
playerCur = Cursor(term)
textCur = Cursor(term)
textCur.setPos([0,0])

# set up the game peices
game = Game(term,tileCur,boardSize,nBombs)
sweeper = Sweeper(game,playerCur)
playerCur.pos = game.boardCorner+np.array([1,1])
textTheme = ["GREEN1","BLACK"]
textWidth = 30

# for blinking things
oddloop = True

with term.hidden_cursor(), term.cbreak(), term.location():
    game.forAllTiles(lambda x: x.countBombs())

    # initial message
    termSetColor(term,textTheme)
    print(term.clear)
    textCur.pr("MINESWEEPER".ljust(textWidth)+"\n"+"ARROWS - move".ljust(textWidth)+"\n"+"D - dig".ljust(textWidth)+"\n"+"F - flag".ljust(textWidth)+"\n"+"press any key to begin".ljust(textWidth))
    
    # wait for input
    inp = term.inkey()
    print(term.clear)

    while game.running:
        oddloop = not oddloop # flip the blinky thing
        inp = term.inkey(timeout=.1) # wait for input but just for a tiny bit, this sets the blinking rate
        termSetColor(term,["BLACK","BLACK"])
        game.draw()
        
        sweeper.handleInp(inp)
        if oddloop:
            sweeper.draw()
        
        # print the game text
        termSetColor(term,textTheme)
        textCur.pr(f"{len(game.getFlagged())} / {len(game.getBombs())}".ljust(textWidth)+"\n"+f" ".ljust(textWidth))
    
    # if the game is done
    game.forAllTiles(lambda x: x.setDug())
    game.forAllTiles(lambda x: x.updateSprite())
    game.draw()
    termSetColor(term,textTheme)
    textCur.pr("GAME OVER".ljust(textWidth)+"\n"+f"You {game.gameExit}".ljust(textWidth)+"\n"+"press any key to quit".ljust(textWidth))
    inp = term.inkey()
    print(term.normal)
    print(term.clear)

