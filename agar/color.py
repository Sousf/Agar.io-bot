import random

class Shade():
    SHADES = []
    def random_shade(self):
        index = random.randint(0, len(self.SHADES)-1)
        return self.SHADES[index]

class Red(Shade):
    # reds
    VERMILLION = (219, 44, 4)
    TERRACOTTA = (240, 126, 101)
    CHESTNUT = (148, 81, 67)
    RUFOUS = (163, 43, 16)
    KOBE = (140, 44, 22)
    SHADES = [VERMILLION, 
              TERRACOTTA, 
              CHESTNUT, 
              RUFOUS, 
              KOBE]

class Green(Shade):
    # greens
    MINT = (145, 249, 229)
    AQUAMARINE = (118, 247, 191)
    MARINE = (95, 221, 157)
    MIDDLE = (73, 145, 103)
    RIFLE = (63, 69, 49)
    SHADES = [MINT, 
              AQUAMARINE,
              MARINE, 
              MIDDLE, 
              RIFLE]

class Blue(Shade):
    # sky
    SKY = (68, 190, 227)
    MUNSELI = (36, 139, 171)
    CG = (11, 124, 158)
    SAPPHIRE = (30, 103, 125)
    MIDNIGHT = (4, 65, 84)
    SHADES = [SKY,
              MUNSELI,
              CG,
              SAPPHIRE,
              MIDNIGHT]

class Yellow(Shade):
    # yellows
    MINDARO = (206, 240, 105)
    CRAYOLA = (203, 230, 124)
    MIDDLE = (172, 194, 109)
    OLIVE = (160, 173, 118)
    EBONY = (92, 99, 69)
    SHADES = [MINDARO,
              CRAYOLA,
              MIDDLE,
              OLIVE,
              EBONY]

class Color(Shade):
    RED = Red
    GREEN = Green
    BLUE = Blue
    YELLOW = Yellow
    COLORS = [RED, GREEN, BLUE, YELLOW]
    SHADES = []
    for color in COLORS:
        for shade in color.SHADES:
            SHADES.append(shade)

if __name__ == "__main__":
    print(Color().random_shade())