from blessed import Terminal
from gameLib import *


# print(term.clear)
# for i in range(10):
#     print(term.move_xy(i,0)+term.green_on_black + str(i))
#     time.sleep(1)

term = Terminal()
c = Cursor(term)
ctext = Cursor(term)
ctext.setPos([0,0])
print(term.clear)
c.pos = np.array([10,10])

color = {
    "red":200,
    "green":100,
    "blue":100
}


with term.hidden_cursor(), term.cbreak(), term.location():
    for i in range(200):
        print(term.color_rgb(**color))
        inp = term.inkey(timeout=1000)
        c.move(dPad(term,inp))
        c.pr(chr(int("0x2588", 0)))
        ctext.pr(f"{c.pos}\n{[term.width,term.height]}\n{i}\n{inp}")

print(term.normal)