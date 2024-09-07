# Basic data structures and processes of a Rubik's cube
from __future__ import annotations
import numpy as np

from util import stripWords, firstAndRest, Vars


class TAddress:
    """
    Holds the address of a tile, that is, face, row, column
    """
    def __init__(self, cube, face, row, column):
        self.cube = cube
        self.f = face
        self.r = row
        self.c = column

    # def mirror(self, cube: Cube):
    #     """
    #     Mirror the address of this tile respect to a plane defined by the Z and Y axes.
    #     Change the object inplace and returns a pointer to itself (useful if you want to chain method calls)
    #     :param cube: the Cube object from where to take the size
    #     :return: the changed object
    #     """
    #     if self.f == 'R':
    #         self.f = 'L'
    #     elif self.f == 'L':
    #         self.f = 'R'
    #     self.c = cube.n - 1 - self.c
    #     return self

    def clockwise(self):
        self.r, self.c = self.c, self.cube.n - self.r - 1
        return self

    def anticlockwise(self):
        self.r, self.c = self.cube.n - self.c - 1, self.r
        return self

    def swap(self):
        self.r, self.c = self.c, self.r
        return self

    def horizontalMirror(self):
        self.r = self.cube.n - self.r - 1
        return self

    def verticalMirror(self):
        self.c = self.cube.n - self.c - 1
        return self


# Directions
class Dir:
    """
    Holds some constants and methods to manage the direction of the movements in a cube
    Each face is an array with n by n tiles, numbered from 0 to n-1, (0, 0) is the top-left corner,
    the direction is determined by the row step and column step, each one could be -1, 0 or 1 and these steps
    are used to scan the face arrays
    """
    UP = 'u'
    DOWN = 'd'
    RIGHT = 'r'
    LEFT = 'l'
    NULL = '0'
    _OFFSETS = {UP: (-1, 0), DOWN: (1, 0), RIGHT: (0, 1), LEFT: (0, -1), NULL: (0, 0)}
    _DIRECTION = {v: k for k, v in _OFFSETS.items()}

    def __init__(self, dirId):
        self.id = dirId.lower()
        self.row, self.col = Dir._OFFSETS[self.id]

    def __repr__(self):
        return self.id

    def invert(self) -> Dir:
        """
        Inverts the direction of the movement LEFT <-> RIGHT or UP <-> DOWN
        Change the object inplace and returns a pointer to itself (useful if you want to chain method calls)
        :return: the changed object
        """
        self.row = -self.row
        self.col = -self.col
        self.id = Dir._DIRECTION[(self.row, self.col)]
        return self

    def swap(self) -> Dir:
        """
        Swaps the row and column steps, now you're moving through columns as you did through rows and vice versa
        Change the object inplace and returns a pointer to itself (useful if you want to chain method calls)
        :return: the changed object
        """
        self.row, self.col = self.col, self.row
        self.id = Dir._DIRECTION[(self.row, self.col)]
        return self

    def horizontal(self) -> bool:
        """
        :return: True if the direction is LEFT or RIGHT
        """
        return self.col != 0

    def vertical(self) -> bool:
        """
        :return: True if the direction is UP or DOWN
        """
        return self.row != 0


class Span:
    """
    Holds the limits (beg/end) of a sector of tiles to move or to compare
    """
    def __init__(self, cube: Cube, strSpan="", checkLimits=True):
        """
        Converts a string that represents a range of rows/columns to move into Span object
        :param cube: the Cube object from where to take the size and vars
        :param strSpan: string containing a range with the form <begin>[:<end>] where <begin> and <end> can be just
                        numbers, logic coordinates like "T" for top, "C" for center, etc. or any arithmetic operation
                        using them
        :param checkLimits: True if it's necessary to check if <begin> and <end> are between 0 and n-1
        """
        if strSpan == "":
            beg, end = 0, cube.n - 1
        elif ':' in strSpan:
            beg, end = strSpan.split(':')
            beg = eval(beg, cube.vars.vars()) - 1
            end = eval(end, cube.vars.vars()) - 1
            if beg > end:
                beg, end = end, beg
        else:
            beg = eval(strSpan, cube.vars.vars()) - 1
            end = beg
        if checkLimits:
            beg = 0 if beg < 0 else cube.n - 1 if beg >= cube.n else beg
            end = 0 if end < 0 else cube.n - 1 if end >= cube.n else end
        self.cube = cube
        self.beg = beg
        self.end = end

    def __repr__(self):
        return f"{self.beg + 1}:{self.end + 1}"

    def invert(self) -> Span:
        """
        Inverts the orientation of the span, ie 2nd and 3rd tiles from the left becomes 2nd and 3rd tiles from the right
        Change the object inplace and returns a pointer to itself (useful if you want to chain method calls)
        :return: the changed object
        """
        self.beg, self.end = (self.cube.n - 1 - self.end, self.cube.n - 1 - self.beg)
        return self

    def swap(self) -> Span:
        """
        Swaps the beginning and end of the Span
        Change the object inplace and returns a pointer to itself (useful if you want to chain method calls)
        :return: the changed object
        """
        self.beg, self.end = self.end, self.beg
        return self

    def slice(self) -> slice:
        """
        Returns a builtin Python slice object based on the properties of the Span, useful for use in
        numpy arrays or to generate range() parameters
        :return: the slice object
        """
        step = -1 if self.beg > self.end else 1
        return slice(self.beg, self.end + step if self.end or step != -1 else None, step)


class Face:
    """
    Constants to hold the one-char code name of the faces and the names of the colors of each face
    """
    FRONT = 'F'
    BACK = 'B'
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'
    FACES = FRONT + BACK + UP + DOWN + LEFT + RIGHT

    COLOR = {
        FRONT: "red",
        BACK: "orange",
        UP: "white",
        DOWN: "yellow",
        LEFT: "green",
        RIGHT: "blue"
    }


class Tile:
    """
    Holds the data of a tile
    """
    def __init__(self):
        self.id = ''
        self.color = ''

    def __repr__(self):
        return f'{self.id}.{self.color[0].upper()}'


class Connection:
    """
    Holds the connection between the faces of the cube, ie if I'm in the left face, when I go past the top edge I get to
    the top face, but if I go past the right edge, I get to the front face, and so on. Also holds info about how the
    rows and columns behave when going through the edges
    """
    def __init__(self, face, direct, invert, transpose):
        self.face = face
        self.direct = direct
        self.invert = invert
        self.transpose = transpose


class ColorRel:
    def __init__(self, cube):
        """
        Holds the relationship between the colors of the cube
        Type of relationships:
            'a' = anticlockwise
            'c' = clockwise
            'o' = opposite
        :param cube: the cube to be inspected
        """
        self._colorRel = {}
        for _ in range(4):
            colorList = [
                cube.faces[Face.UP][cube.n - 1, cube.n - 1].color,  # clockwise top right corner
                cube.faces[Face.RIGHT][0, 0].color,
                cube.faces[Face.FRONT][0, cube.n - 1].color
            ]
            self.setRelColor('c', colorList)
            colorList.reverse()
            self.setRelColor('a', colorList)  # anticlockwise same corner
            colorList = [
                cube.faces[Face.UP][cube.n - 1, 0].color,  # clockwise top left corner
                cube.faces[Face.FRONT][0, 0].color,
                cube.faces[Face.LEFT][0, cube.n - 1].color
            ]
            self.setRelColor('c', colorList)
            colorList.reverse()
            self.setRelColor('a', colorList)  # anticlockwise same corner
            cube.makeMoves('X')  # after 4 moves the cube returns to the original position
        for color in self._colorRel:
            opposite = ''
            for ccc in self._colorRel:
                if (ccc != color) and (ccc not in self._colorRel[color]['c']):
                    opposite = ccc
            self.setRelColor('o', [color, opposite])

    def setRelColor(self, rel, colorList):
        """
        Updates the dict _colorRel to build the structure that hold all the relationships
        :param rel: type of relationship ('a' = anticlockwise, 'c' = clockwise, 'o' = opposite)
        :param colorList: list of the colors that have the relationship 'rel' between them
        """
        for c in range(len(colorList)):
            d = self._colorRel
            i = c
            if colorList[i] not in d:
                d[colorList[i]] = {}
            d = d[colorList[i]]
            for _ in range(1, len(colorList)):
                if rel not in d:
                    d[rel] = {}
                d = d[rel]
                i = (i + 1) if i < len(colorList) - 1 else 0
                if colorList[i] not in d:
                    d[colorList[i]] = {}
                d = d[colorList[i]]

    def listColors(self, rel, color1, color2=None):
        """
        Returns a list of colors that have the relationship 'rel' with 'color1' or the list of colors that
        have the relationship 'rel' with color1 and color2
        :param rel: type of relationship ('a' = anticlockwise, 'c' = clockwise, 'o' = opposite)
        :param color1: the name of the 1st color
        :param color2: (optional) the name of the second color
        :return: the list of colors that have this relationship with color1 and optionally color2
        """
        d = self._colorRel
        if color1 not in d:
            return []
        d = d[color1]
        if rel not in d:
            return []
        d = d[rel]
        if color2:
            if color2 not in d:
                return []
            d = d[color2]
            if rel not in d:
                return []
            d = d[rel]
        return list(d.keys())


class Move:
    """
    Holds tha data to make a cube's move

    Attributes:

    cube: the Cube object from where to take the size and vars
    face: The base face from which the move originates.
    span: a Span object with the range of rows/columns that will be moved.
    direction: a Dir object with the direction of the move (UP, DOWN, LEFT, RIGHT).
    times: the number of times to repeat the move.
    """

    def __init__(self, cube, mov):
        """
        Converts a string 'mov' into a Move object to call the method 'oneMove'
        The string 'mov' can follow standard Rubik's notation (F, B, U, D, L, R, M, E, S, x, y, z, lowercase letters, w, ', 2)
        or be in the form <face>[.<span start>[:<span end>]].[<times>]<direction> where:

        <face> = "F", "B", "U", "D", "L", or "R"
        <span start> and <span end> = row/column numbers to move (start and end are inclusive)
            - Explicit numbers indicate rows/columns counted from the top/left
            - The numbering goes from 1 to self.n
            - 'T' or 'L' (Top/Left) indicate the 1st row/column (equivalent to 1)
            - 't' or 'l' (top/left) indicate the 2nd row/column (equivalent to 2)
            - 'B' or 'R' (Bottom/Right) indicate the last row/column
            - 'b' or 'r' (bottom/right) indicate the second-to-last row/column
            - 'c' or 'C' (Center) indicate the middle row/column
                - On odd-sized cubes, c and C are equivalent
                - On even-sized cubes, c and C represent the smaller and larger of the two central rows/columns
            - After TLtlBRbrcC, you can add or subtract a number
                e.g.: T+1 is equivalent to t, B-1 is equivalent to b, t+1 is the 3rd row
            - For symmetry purposes, T and L (as well as B and R) are equivalent and included only to clarify the movement notation.
              The direction of the movement is determined ONLY by the “direction” field.
            - The order of <span start> and <span end> is interchangeable (2:5 is equivalent to 5:2)

        <times> = number of times the move is repeated (digit, optional)
            - A multiplier can be prefixed to the direction letter, indicating how many times the move should be performed
            - 1: default, 2: the most logical to use, 3: rare (equivalent to 1 in the opposite direction), >3: ridiculous

        <direction> = "u", "d", "l", "r", "c", "a" for up, down, left, right, clockwise, and anticlockwise
            - If the direction is clockwise or anticlockwise, <span start>:<span end> is omitted/ignored

        Any move that begins with "><" is considered mirrored with respect to a plane defined by the Z and Y axes.

        :param cube: the Cube object from where to take the size and vars
        :param mov: the string with the move to perform, coded as explained above
        """
        mm = mov
        face, span, direction, times = '', Span(cube), Dir(Dir.NULL), 0

        mirror = False
        if mm[0:2] == '><':
            mirror = True  # remember that I'm in mirror mode, take this in account just before the end
            mm = mm[2:]

        if '.' in mm:  # mov is in the form <face>[.<span start>[:<span end>]].[<times>]<direction>
            face, mm = firstAndRest(mm, '.')
            face = face.upper()
            span.beg, span.end = (1, 1)  # default value
            if '.' in mm:  # there is an explicit span
                ss, mm = firstAndRest(mm, '.')
                span = Span(cube, ss)
            times = 1
            if mm[0] in '123456789':  # there is an explicit multiplier
                times, mm = int(mm[:1]), mm[1:]
            mm = mm[:1]
            if mm in 'udlrUDLR':
                direction = Dir(mm)
                mm = ''  # I don't have to process mm anymore, I have all the data to return
            else:  # mm in 'caCA' (clockwise o anticlockwise) => use a standard Rubik's movement
                mm = face + str(times) + ("'" if mm in 'aA' else "")

        if mm:  # mm is a standard Rubik's movement (F, B, U, D, L, R, M, E, S, x, y, z, lowercase letters, w, ', 2)
            face = mm[0]
            mm = mm[1:]
            if mm:
                if mm[0] in 'wW':  # w notation -> lowercase notation
                    face = face.lower()
                    mm = mm[1:]
            anti = ("'" in mm)  # anticlockwise
            mm = mm[:mm.find("'")] + mm[mm.find("'") + 1:]  # remove the ' leaving only the number if there is one
            times = (1 if not mm else int(mm))  # If there is still a number, that is the multiplier, if not, 1 is default

            span = Span(cube)
            if face in Face.FACES.upper():
                span.beg, span.end = (0, 0)
            elif face in Face.FACES.lower():
                # In cubes > 3x3, it is logical to consider the entire central block (move everything except the opposite face)
                span.beg, span.end = (0, cube.n - 2)
            elif face in 'MESmes':  # m e s (lowercase) does not make sense but for simplicity I make it equivalent to M E S
                # central block without the side faces
                span.beg, span.end = (1, cube.n - 2)
            elif face in 'XYZxyz':  # X Y Z, I make it equivalent to x y z (this is usually used in upper and lower interchangeably)
                # full range, change the orientation of the cube
                span.beg, span.end = (0, cube.n - 1)

            f, direction = '', Dir(Dir.NULL)
            if face in "FfSsZz":
                f, direction = Face.RIGHT, Dir(Dir.DOWN)
            elif face in "Bb":
                f, direction = Face.LEFT, Dir(Dir.DOWN)
            elif face in "LlMm":
                f, direction = Face.FRONT, Dir(Dir.DOWN)
            elif face in "RrXx":
                f, direction = Face.BACK, Dir(Dir.DOWN)
            elif face in "UuYy":
                f, direction = Face.FRONT, Dir(Dir.LEFT)
            elif face in "DdEe":
                f, direction = Face.FRONT, Dir(Dir.RIGHT)
                # Only in the case of looking from below, I invert the range selection
                span.invert()
            face = f
            if anti:  # Anticlockwise => reverse the direction
                direction.invert()

        if mirror:
            if face == Face.RIGHT:
                face = Face.LEFT
            elif face == Face.LEFT:
                face = Face.RIGHT
            if direction.vertical():  # UP or DOWN
                span.invert()
            elif direction.horizontal():  # LEFT or RIGHT
                direction.invert()

        self.cube = cube
        self.face = face
        self.span = span
        self.direction = direction
        self.times = times

    def __repr__(self):
        return f'{self.face}.{self.span}.{self.times if self.times != 1 else ""}{self.direction}'


class Cube:
    def __init__(self, size=3, white=False):
        """
        Holds the data structure and transformations of a regular 6 faces Rubik's cube
        :param size: each face of the cube will have (size x size) tiles
        :param white: True if it's a cube with all white tiles (useful when you're building the solving methods database)
        """
        self.n = size
        self.white = white

        self.vars = Vars('c')  # Variables to convert logic coordinates to numeric ones
        self.vars.set('T', 1)
        self.vars.set('t', 2)
        self.vars.set('L', 1)
        self.vars.set('l', 2)
        self.vars.set('B', size)
        self.vars.set('b', size - 1)
        self.vars.set('R', size)
        self.vars.set('r', size - 1)
        self.vars.set('C', (size // 2) + 1)
        self.vars.set('c', (size // 2) + (size % 2))
        self.vars.set('i', 0)
        self.vars.set('j', 0)
        self.vars.set('k', 0)

        # create the faces dict, each face is an array of tiles
        self.faces = {
            Face.FRONT: np.array([[Tile() for _ in range(self.n)] for _ in range(self.n)]),
            Face.BACK: np.array([[Tile() for _ in range(self.n)] for _ in range(self.n)]),
            Face.UP: np.array([[Tile() for _ in range(self.n)] for _ in range(self.n)]),
            Face.DOWN: np.array([[Tile() for _ in range(self.n)] for _ in range(self.n)]),
            Face.LEFT: np.array([[Tile() for _ in range(self.n)] for _ in range(self.n)]),
            Face.RIGHT: np.array([[Tile() for _ in range(self.n)] for _ in range(self.n)])
        }
        self.initTiles()

        # Connections between adjacent faces of the cube. Which one connects with which other, through which edge,
        # and if the coordinates inverts when you pass to the adjacent face
        self.conn = {
            # connect the front face with the adjacent ones
            Face.FRONT: {
                Dir.UP: Connection(face=Face.UP, direct=Dir(Dir.UP), invert=False, transpose=False),
                Dir.DOWN: Connection(face=Face.DOWN, direct=Dir(Dir.DOWN), invert=False, transpose=False),
                Dir.LEFT: Connection(face=Face.LEFT, direct=Dir(Dir.LEFT), invert=False, transpose=False),
                Dir.RIGHT: Connection(face=Face.RIGHT, direct=Dir(Dir.RIGHT), invert=False, transpose=False),
            },
            # connect the upper face with the adjacent ones
            Face.UP: {
                Dir.UP: Connection(face=Face.BACK, direct=Dir(Dir.DOWN), invert=True, transpose=False),
                Dir.DOWN: Connection(face=Face.FRONT, direct=Dir(Dir.DOWN), invert=False, transpose=False),
                Dir.LEFT: Connection(face=Face.LEFT, direct=Dir(Dir.DOWN), invert=False, transpose=True),
                Dir.RIGHT: Connection(face=Face.RIGHT, direct=Dir(Dir.DOWN), invert=True, transpose=True),
            },
            # connect the bottom face with the adjacent ones
            Face.DOWN: {
                Dir.UP: Connection(face=Face.FRONT, direct=Dir(Dir.UP), invert=False, transpose=False),
                Dir.DOWN: Connection(face=Face.BACK, direct=Dir(Dir.UP), invert=True, transpose=False),
                Dir.LEFT: Connection(face=Face.LEFT, direct=Dir(Dir.UP), invert=True, transpose=True),
                Dir.RIGHT: Connection(face=Face.RIGHT, direct=Dir(Dir.UP), invert=False, transpose=True),
            },
            # connect the back face with the adjacent ones
            Face.BACK: {
                Dir.UP: Connection(face=Face.UP, direct=Dir(Dir.DOWN), invert=True, transpose=False),
                Dir.DOWN: Connection(face=Face.DOWN, direct=Dir(Dir.UP), invert=True, transpose=False),
                Dir.LEFT: Connection(face=Face.RIGHT, direct=Dir(Dir.LEFT), invert=False, transpose=False),
                Dir.RIGHT: Connection(face=Face.LEFT, direct=Dir(Dir.RIGHT), invert=False, transpose=False),
            },
            # connect the left face with the adjacent ones
            Face.LEFT: {
                Dir.UP: Connection(face=Face.UP, direct=Dir(Dir.RIGHT), invert=False, transpose=True),
                Dir.DOWN: Connection(face=Face.DOWN, direct=Dir(Dir.RIGHT), invert=True, transpose=True),
                Dir.LEFT: Connection(face=Face.BACK, direct=Dir(Dir.LEFT), invert=False, transpose=False),
                Dir.RIGHT: Connection(face=Face.FRONT, direct=Dir(Dir.RIGHT), invert=False, transpose=False),
            },
            # connect the right face with the adjacent ones
            Face.RIGHT: {
                Dir.UP: Connection(face=Face.UP, direct=Dir(Dir.LEFT), invert=True, transpose=True),
                Dir.DOWN: Connection(face=Face.DOWN, direct=Dir(Dir.LEFT), invert=False, transpose=True),
                Dir.LEFT: Connection(face=Face.FRONT, direct=Dir(Dir.LEFT), invert=False, transpose=False),
                Dir.RIGHT: Connection(face=Face.BACK, direct=Dir(Dir.RIGHT), invert=False, transpose=False),
            },
        }

        if not self.white:
            self.colorRel = ColorRel(self)

    def initTiles(self):
        """
        Initializes all the tiles of a cube with the color that corresponds to each face
        """
        for face in self.faces:
            for r in range(self.n):
                for c in range(self.n):
                    self.faces[face][r, c].color = Face.COLOR[face] if not self.white else 'white'
                    self.faces[face][r, c].id = f'{face}.{r+1}.{c+1}'

    def makeMoves(self, sMoves, backwards=False):
        """
        Parses the moves in sMoves with the method "str2move" and make them.
        :param sMoves: string containing one or more moves separated by spaces
        :param backwards: if True, start from the end and make all the moves backwards
        """
        moves = stripWords(sMoves)
        if backwards:
            moves.reverse()
        mirror = ''
        for m in moves:
            if m == '><':
                mirror = '><' if mirror == '' else ''
                continue
            if m == '-':
                continue
            move = Move(cube=self, mov=mirror + m)
            if backwards:
                move.direction.invert()
            self.oneMove(move)

    def readWriteTiles(self, face, span: Span, direction: Dir, tiles=None, changedTiles=None):
        """
        Reads (and optionally replaces) a range of tiles from the matrix of a cube face.

        :param face: The face where the tiles to read/replace are located.
        :param span: If the direction is vertical, the range of columns; if horizontal, the range of rows to read/replace.
                     The dimension not taken as a range is read/replaced completely.
        :param direction: Direction of the movement
        :param tiles: (optional) Tiles that will replace the ones determined by the span and direction.
        :param changedTiles: (optional) If a list object is provided, adds to this list the addresses (TAddress objects)
                                of all the modified tiles.
        :return: Returns a matrix with the read tiles
        """
        if direction.horizontal():  # LEFT or RIGHT
            rows = span.slice()
            cols = slice(None, None, direction.col)
        else:  # UP or DOWN
            rows = slice(None, None, direction.row)
            cols = span.slice()
        ret = self.faces[face][rows, cols].copy()
        if tiles is not None:
            self.faces[face][rows, cols] = tiles
            if changedTiles is not None:
                changedTiles.extend(
                    TAddress(self, face, r, c) for r in range(*rows.indices(self.n)) for c in range(*cols.indices(self.n))
                )
        return ret

    def oneMove(self, move: Move, changedTiles=None):
        """
        Performs a move on the cube. The move is determined by a face, a range of rows/columns, and a direction.

        :param move: the move to perform
        :param changedTiles: (optional) If a list object is provided, adds to this list the addresses (TAddress objects)
                                of all the modified tiles.
        """
        for _ in range(move.times):
            ff, sp, dd = move.face, move.span, move.direction

            # copy the cell sector determined by 'span' and 'direction', on the different faces of the cube,
            # rotating 4 times in the given direction
            tiles = self.readWriteTiles(ff, sp, dd)
            for _ in range(4):
                conn = self.conn[ff][dd.id]
                ff, dd = conn.face, conn.direct
                if conn.invert:
                    sp.invert().swap()
                if conn.transpose:
                    tiles = tiles.T
                tiles = self.readWriteTiles(ff, sp, dd, tiles=tiles, changedTiles=changedTiles)

            # When the range includes one or both edges, rotate the side faces, clockwise or anticlockwise.
            if move.span.beg == 0 or move.span.end == 0:
                if move.direction.horizontal():  # Dir.RIGHT or Dir.LEFT
                    ff = self.conn[move.face][Dir.UP].face
                    rotDir = 1 if move.direction.id == Dir.RIGHT else 3  # 1 = anticlockwise, 3 = clockwise
                else:  # (direction == Dir.UP) or (direction == Dir.DOWN)
                    ff = self.conn[move.face][Dir.LEFT].face
                    rotDir = 1 if move.direction.id == Dir.UP else 3  # 1 = anticlockwise, 3 = clockwise
                self.faces[ff] = np.rot90(self.faces[ff], rotDir)
                if changedTiles is not None:
                    changedTiles.extend([TAddress(self, ff, r, c) for r in range(self.n) for c in range(self.n)])
            if move.span.beg == self.n - 1 or move.span.end == self.n - 1:
                if move.direction.horizontal():  # Dir.RIGHT or Dir.LEFT
                    ff = self.conn[move.face][Dir.DOWN].face
                    rotDir = 1 if move.direction.id == Dir.LEFT else 3  # 1 = anticlockwise, 3 = clockwise
                else:  # (direction == Dir.UP) or (direction == Dir.DOWN)
                    ff = self.conn[move.face][Dir.RIGHT].face
                    rotDir = 1 if move.direction.id == Dir.DOWN else 3  # 1 = anticlockwise, 3 = clockwise
                self.faces[ff] = np.rot90(self.faces[ff], rotDir)
                if changedTiles is not None:
                    changedTiles.extend([TAddress(self, ff, r, c) for r in range(self.n) for c in range(self.n)])

    def anticlockwiseFace(self, face, direction):
        """
        Returns the face that is anticlockwise to the parameter face and the given direction, ie if you're in the front
        face moving to the right direction, the anticlockwise face is the up face, but if you're moving to the left, the
        anticlockwise face is the down face
        :param face: the face where you're in
        :param direction: the direction of your current movement
        :return: the face that is anticlockwise of your face relative to your movement
        """
        if direction == Dir.RIGHT:
            return self.conn[face][Dir.UP].face
        elif direction == Dir.LEFT:
            return self.conn[face][Dir.DOWN].face
        elif direction == Dir.UP:
            return self.conn[face][Dir.LEFT].face
        elif direction == Dir.DOWN:
            return self.conn[face][Dir.RIGHT].face
        else:
            return None

    def clockwiseFace(self, face, direction):
        """
        Returns the face that is clockwise to the parameter face and the given direction, ie if you're in the front
        face moving to the right direction, the clockwise face is the down face, but if you're moving to the left, the
        clockwise face is the up face
        :param face: the face where you're in
        :param direction: the direction of your current movement
        :return: the face that is clockwise of your face relative to your movement
        """
        if direction == Dir.RIGHT:
            return self.conn[face][Dir.DOWN].face
        elif direction == Dir.LEFT:
            return self.conn[face][Dir.UP].face
        elif direction == Dir.UP:
            return self.conn[face][Dir.RIGHT].face
        elif direction == Dir.DOWN:
            return self.conn[face][Dir.LEFT].face
        else:
            return None

    def shuffle(self, qty=0):
        """
        Shuffles the cube with "qty" random moves
        :param qty: Quantity of random moves to make. Default: 20n (n = the size of the cube)
        :return: a string with the movements performed
        """
        moves = []
        if qty <= 0:
            qty = self.n * 20
        move = Move(self, 'F')
        for _ in range(qty):
            move.face = np.random.choice(list(Face.FACES))
            move.span.beg, move.span.end = (np.random.randint(self.n), np.random.randint(self.n))
            move.direction = Dir([Dir.UP, Dir.DOWN, Dir.LEFT, Dir.RIGHT][np.random.randint(4)])
            move.times = np.random.randint(1, 4)
            moves.append(str(move))
            self.oneMove(move)
        return ' '.join(moves)

