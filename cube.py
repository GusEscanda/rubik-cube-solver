# Basic data structures and processes of a Rubik's cube

import numpy as np
from util import stripWords, firstAndRest, Clase, Vars


# Directions
class Dir:
    UP = (-1, 0)  # ( row offset, column offset )
    DOWN = (1, 0)
    RIGHT = (0, 1)
    LEFT = (0, -1)
    NULL = (0, 0)
    _OFFSETS = {'u': UP, 'd': DOWN, 'r': RIGHT, 'l': LEFT, '0': NULL}
    _DIRECTION = {v: k for k, v in _OFFSETS.items()}

    @staticmethod
    def offset(direction):
        return Dir._OFFSETS[direction.lower()]

    @staticmethod
    def dir(offset):
        return Dir._DIRECTION[offset]


# Faces of the cube
class Face:
    FRONT = 'F'
    BACK = 'B'
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'
    FACES = FRONT + BACK + UP + DOWN + LEFT + RIGHT


COLORS = {
    Face.FRONT: "red",
    Face.BACK: "orange",
    Face.UP: "white",
    Face.DOWN: "yellow",
    Face.LEFT: "green",
    Face.RIGHT: "blue"
}


class Tile:
    def __init__(self):
        self.id = ''
        self.color = ''


class Connection:
    def __init__(self, face, direct, invert):
        self.face = face
        self.direct = direct
        self.invert = invert


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
            cube.mover('X')  # after 4 moves the cube returns to the original position
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

    def listCols(self, rel, color1, color2=None):
        """
        Returns a list of colors that have the relationship 'rel' with 'color1' or the list of colors that have the relationship 'rel' with color1 and color2
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


class Cube:
    def __init__(self, size=3, white=False):

        self.n = size  # each face will have n*n tiles
        self.white = white  # True if it's a cube with all white tiles (useful when you're building the solving methods database)

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
                Dir.UP: Connection(face=Face.UP, direct=Dir.UP, invert=False),
                Dir.DOWN: Connection(face=Face.DOWN, direct=Dir.DOWN, invert=False),
                Dir.LEFT: Connection(face=Face.LEFT, direct=Dir.LEFT, invert=False),
                Dir.RIGHT: Connection(face=Face.RIGHT, direct=Dir.RIGHT, invert=False),
            },
            # connect the upper face with the adjacent ones
            Face.UP: {
                Dir.UP: Connection(face=Face.BACK, direct=Dir.DOWN, invert=True),
                Dir.DOWN: Connection(face=Face.FRONT, direct=Dir.DOWN, invert=False),
                Dir.LEFT: Connection(face=Face.LEFT, direct=Dir.DOWN, invert=False),
                Dir.RIGHT: Connection(face=Face.RIGHT, direct=Dir.DOWN, invert=True),
            },
            # connect the bottom face with the adjacent ones
            Face.DOWN: {
                Dir.UP: Connection(face=Face.FRONT, direct=Dir.UP, invert=False),
                Dir.DOWN: Connection(face=Face.BACK, direct=Dir.UP, invert=True),
                Dir.LEFT: Connection(face=Face.LEFT, direct=Dir.UP, invert=True),
                Dir.RIGHT: Connection(face=Face.RIGHT, direct=Dir.UP, invert=False),
            },
            # connect the back face with the adjacent ones
            Face.BACK: {
                Dir.UP: Connection(face=Face.UP, direct=Dir.DOWN, invert=True),
                Dir.DOWN: Connection(face=Face.DOWN, direct=Dir.UP, invert=True),
                Dir.LEFT: Connection(face=Face.RIGHT, direct=Dir.LEFT, invert=False),
                Dir.RIGHT: Connection(face=Face.LEFT, direct=Dir.RIGHT, invert=False),
            },
            # connect the left face with the adjacent ones
            Face.LEFT: {
                Dir.UP: Connection(face=Face.UP, direct=Dir.RIGHT, invert=False),
                Dir.DOWN: Connection(face=Face.DOWN, direct=Dir.RIGHT, invert=True),
                Dir.LEFT: Connection(face=Face.BACK, direct=Dir.LEFT, invert=False),
                Dir.RIGHT: Connection(face=Face.FRONT, direct=Dir.RIGHT, invert=False),
            },
            # connect the right face with the adjacent ones
            Face.RIGHT: {
                Dir.UP: Connection(face=Face.UP, direct=Dir.LEFT, invert=True),
                Dir.DOWN: Connection(face=Face.DOWN, direct=Dir.LEFT, invert=False),
                Dir.LEFT: Connection(face=Face.FRONT, direct=Dir.LEFT, invert=False),
                Dir.RIGHT: Connection(face=Face.BACK, direct=Dir.RIGHT, invert=False),
            },
        }

        if not self.white:
            self.colorRel = ColorRel(self)

    def initTiles(self):
        for face in self.faces:
            for r in range(self.n):
                for c in range(self.n):
                    self.faces[face][r, c].color = COLORS[face] if not self.white else 'white'
                    self.faces[face][r, c].id = face + ('000' + str(r + 1))[-3:] + ('000' + str(c + 1))[-3:]

    def str2coord(self, sCoord, checkLimits=True):
        coord = eval(sCoord, self.vars.vars()) - 1  # resto 1 para que esté expresado entre 0 y (self.n-1)
        if checkLimits:
            coord = max(0, min(self.n - 1, coord))  # para que no pinche si la coordenada quedó fuera de rango
        return coord

    def str2span(self, sRange, checkLimits=True):
        beg, end = firstAndRest(sRange, ':')
        end = end if end else beg
        beg = self.str2coord(beg, checkLimits)
        end = self.str2coord(end, checkLimits)
        if beg > end:
            beg, end = end, beg
        return beg, end

    def str2move(self, mov):
        # convierte mov a una tupla (faceId, rango, direction, multi) para llamar multi veces al metodo unMovimiento
        # mov puede tener la notacion estandar de rubik (F,B,U,D,L,R,M,E,S,x,y,z,minusculas,w,',2)
        # o bien ser de la forma <faceId>[.<rango desde>[:<rango hasta>]].[<multi>]<direccion> donde:
        # <faceId> = "F", "B", "U", "D", "L" o "R"
        # <rango desde> y <rango hasta> = numero de fila/columna a mover (desde y hasta son inclusive)
        #     - numeros explicitos indican una fila/columna se cuenta desde la izquierda/arriba
        #     - la numeracion va desde 1 a self.n
        #     - 'T' o 'L' (Top/Left) indican la 1ra fla/columna (son equivalentes a 1)
        #     - 't' o 'l' (top/left) indican la 2da fla/columna (son equivalentes a 2)
        #     - 'B' o 'R' (Bottom/Right) indican la última fla/columna
        #     - 'b' o 'r' (bottom/right) indican la penúltima fla/columna
        #     - 'c' o 'C' (Center) indican la fla/columna central
        #          en cubos impares c y C son equivalentes
        #          en cubos pares c y C son la coordenada menor y mayor de las 2 centrales
        #     - Luego de TLtlBRbrcC puede haber un numero sumando o restando
        #          ej: T+1 es equivalente a t, B-1 es equivalente a b, t+1 es la 3er fila
        #     - Por cuestiones de simetría T y L (tambien B y R) son equivalentes, se incluyen solo
        #       para dar claridad a la escritura de movimientos. La direccion del movimiento esta dada
        #       SOLO por el campo “direction”.
        #     - El orden de <rango desde> y <rango hasta> es indistinto (2:5 es equivalente a 5:2)
        # <multi> = cantidad de veces que se repite el movimiento (digito, optativo)
        #     - se puede anteponer a la letra de direccion un digito multiplicador, el movimiento se realizara esa
        #       cantidad de veces
        #     - 1: default, 2: el mas logico de usar, 3: raro (equivalente a 1 hacia el lado contrario), >3: ridiculo
        # <direccion> = "u", "d", "l", "r", "c", "a" para up, down, left, right, clockwise y anticlockwise
        #     - si la direccion es clockwise o anticlockwise <rango desde>:<rango hasta> se omite / ignora
        # cualquier movimiento que comience con '><' se considera espejado respecto a un plano definido por los
        # ejes Z e Y
        mm = mov
        faceId, span, direction, multi = '', (0, 0), Dir.NULL, 0

        mirror = False
        if mm[0:2] == '><':
            mirror = True  # si está en mirror, proceso normalmente y solo al final considero esa situación
            mm = mm[2:]

        if '.' in mm:  # mov : <faceId>[.<rango desde>[:<rango hasta>]].[multi]<direccion>
            faceId, mm = firstAndRest(mm, '.')
            faceId = faceId.upper()
            span = (1, 1)  # solo para que tenga algun valor en caso de no especificarse
            if '.' in mm:  # hay un rango especificado
                span, mm = firstAndRest(mm, '.')
                span = self.str2span(span)
            multi = 1
            if mm[0] in '123456789':  # hay un multiplicador especificado
                multi, mm = int(mm[:1]), mm[1:]
            mm = mm[:1]
            if mm in 'udlrUDLR':
                direction = Dir.offset(mm)
                mm = ''  # ya no debo procesar mas a mm, tengo todos los datos para devolver
            else:  # mm in 'caCA' (clockwise o anticlockwise) => simulo un movimiento tipo "Rubik estandar"
                mm = faceId + str(multi) + ("'" if mm in 'aA' else "")

        if mm:  # continúo procesando, mm es un movimiento tipo estandar de Rubik (F,B,U,D,L,R,M,E,S,x,y,z,minusculas,w,',2)
            faceId = mm[0]
            mm = mm[1:]
            if mm:
                if mm[0] in 'wW':  # notacion w -> notacion lowercase
                    faceId = faceId.lower()
                    mm = mm[1:]
            anti = ("'" in mm)  # movimiento antihorario
            mm = mm[:mm.find("'")] + mm[mm.find("'") + 1:]  # saca el ' dejando solo el numero si lo hubiere
            multi = (1 if not mm else int(mm))  # si todavía hay un numero, ese es el multiplicador, si no es 1

            span = (0, 0)
            if faceId in Face.FACES.upper():
                span = (0, 0)
            elif faceId in Face.FACES.lower():
                # en cubos > 3x3, lo coherente es considerar el bloque central completo (mueve todo menos la cara opuesta)
                span = (0, self.n - 2)
            elif faceId in 'MESmes':  # m e s (minuscula) no tiene sentido pero por simplicidad lo hago equivalente a M E S
                # bloque central sin las caras laterales
                span = (1, self.n - 2)
            elif faceId in 'XYZxyz':  # X Y Z lo hago equivalente a x y z (esto si se suele usar en upper y lower indistintamente)
                # rango completo, cambia la orientacion del cube
                span = (0, self.n - 1)

            face, direction = '', ''
            if faceId in "FfSsZz":
                face, direction = Face.RIGHT, Dir.DOWN
            elif faceId in "Bb":
                face, direction = Face.LEFT, Dir.DOWN
            elif faceId in "LlMm":
                face, direction = Face.FRONT, Dir.DOWN
            elif faceId in "RrXx":
                face, direction = Face.BACK, Dir.DOWN
            elif faceId in "UuYy":
                face, direction = Face.FRONT, Dir.LEFT
            elif faceId in "DdEe":
                face, direction = Face.FRONT, Dir.RIGHT
                # solo en el caso de mirar desde abajo, invierto la seleccion del rango
                span = (self.n - 1 - span[1], self.n - 1 - span[0])
            faceId = face
            if anti:  # era antihorario => invierto la direccion
                direction = (-direction[0], -direction[1])

        if mirror:
            if faceId == Face.RIGHT:
                faceId = Face.LEFT
            elif faceId == Face.LEFT:
                faceId = Face.RIGHT
            if direction == Dir.UP or direction == Dir.DOWN:
                span = (self.n - 1 - span[1], self.n - 1 - span[0])
            elif direction == Dir.LEFT or direction == Dir.RIGHT:
                direction = (-direction[0], -direction[1])

        return faceId, span, direction, multi

    def mover(self, movimientos, animacion=False, haciaAtras=False):
        # - movimientos: string con uno o varios movimientos separados por espacios.
        # - interpreta estos movimientos con la funcion str2movim y los ejecuta
        # - animacion: si es True, devuelve los datos necesarios para animar el movimiento
        #         para animar se debe llamar con movimientos individuales (el llamado lo hace el modulo de animacion)
        if animacion:
            celdasMovidas = []
            caraAnticlockwise = ''
        else:
            celdasMovidas = False
            caraAnticlockwise = ''
        movs = stripWords(movimientos)
        if haciaAtras:
            movs.reverse()
        espejo = ''
        for mov in movs:
            if mov == '><':
                espejo = '><' if espejo == '' else ''
                continue
            if mov == '-':
                continue
            idCara, rango, direc, multip = self.str2move(espejo + mov)
            if haciaAtras:
                direc = (-direc[0], -direc[1])
            self.unMovimiento(idCara, rango, direc, multip, celdasMovidas)
            if animacion:
                connCara = self.conn[idCara]
                if (direc == Dir.RIGHT) or (direc == Dir.LEFT):
                    caraAnticlockwise = connCara[Dir.UP].face if direc == Dir.RIGHT else connCara[Dir.DOWN].face
                else:  # (direc == Dir.UP) or (direc == Dir.DOWN)
                    caraAnticlockwise = connCara[Dir.LEFT].face if direc == Dir.UP else connCara[Dir.RIGHT].face
        return celdasMovidas, caraAnticlockwise

    def readWriteCeldas(self, face, rango, direc, set=False, celdas=[], celdasMovidas=False):
        # - Lee (y eventualmente reemplaza) un rango de celdas de la matriz de una face del cube
        # - rango: es una tupla (desde,hasta) ordenada, es decir que si esta en orden inverso, las celdas se leeran tambien en orden inverso
        # - direc: es la direccion del movimiento, si es arriba o abajo, el rango es de columnas (se toman entonces todas las filas)
        #          si direc es derecha o izquierda el rango es de filas y se toman todas las columnas
        # - set: indica si se graban en el lugar de las celdas leidas, las de la lista celdas
        # - celdas: (solo si quiero grabar), son las celdas que reemplazaran a las leidas
        # - celdasMovidas: si se pasa como parametro un objeto tipo lista, se agrega a esa lista la direccion (cara, fila, columna) de las celdas
        #                  que se estan moviendo. Para uso de los modulos graficos (por si quiero mostrar las celdas en movimiento)
        # - Devuelve una matriz con el contenido de las celdas del rango especificado.
        rinv = 1
        if rango[0] > rango[1]:
            rinv = -1
        if direc == Dir.RIGHT:
            r, c = rango[0], 0
            rr, rc = rinv, 0
        elif direc == Dir.LEFT:
            r, c = rango[0], self.n - 1
            rr, rc = rinv, 0
        elif direc == Dir.DOWN:
            r, c = 0, rango[0]
            rr, rc = 0, rinv
        elif direc == Dir.UP:
            r, c = self.n - 1, rango[0]
            rr, rc = 0, rinv
        ret = []
        while (0 <= r < self.n) and (0 <= c < self.n):
            rrr = []
            for xx in range(abs(rango[1] - rango[0]) + 1):
                rrr.append(self.faces[face][r + xx * rr, c + xx * rc])
            ret.append(rrr)
            if set:
                for xx in range(abs(rango[1] - rango[0]) + 1):
                    self.faces[face][r + xx * rr, c + xx * rc] = celdas[len(ret) - 1, xx]
                if type(celdasMovidas) == list:
                    for xx in range(abs(rango[1] - rango[0]) + 1):
                        celdasMovidas.append((face, r + xx * rr, c + xx * rc))
            r, c = r + direc[0], c + direc[1]
        return np.array(ret)

    def unMovimiento(self, idCara, rango, direc, multip=1, celdasMovidas=False):
        for _ in range(multip):
            # Hace un movimiento del cube (solo hace movimientos para direccciones 'udlr')
            face, rr, dd = idCara, rango, direc
            # copiar el sector de celdas dado por rango y direc, en las distintas caras del cube, rotando 4 veces en direccion direc
            celdas = self.readWriteCeldas(face, rr, dd)
            for _ in range(4):
                conn = self.conn[face][dd]
                face, dd = conn.face, conn.direct
                if conn.invert:
                    rr = (self.n - rr[0] - 1, self.n - rr[1] - 1)
                celdas = self.readWriteCeldas(face, rr, dd, set=True, celdas=celdas, celdasMovidas=celdasMovidas)
            # cuando el rango incluye uno o ambos bordes rotar la(s) face(s) lateral(es), en sentido horario o antihorario
            if min(rango) == 0:
                if (direc == Dir.RIGHT) or (direc == Dir.LEFT):
                    face = self.conn[idCara][Dir.UP].face
                    dirRotacion = 1 if direc == Dir.RIGHT else 3  # 1 = antihorario, 3 = horario
                else:  # (direc == Dir.UP) or (direc == Dir.DOWN)
                    face = self.conn[idCara][Dir.LEFT].face
                    dirRotacion = 1 if direc == Dir.UP else 3  # 1 = antihorario, 3 = horario
                self.faces[face] = np.rot90(self.faces[face], dirRotacion)
                if type(celdasMovidas) == list:
                    for r in range(self.n):
                        for c in range(self.n):
                            celdasMovidas.append((face, r, c))
            if max(rango) == self.n - 1:
                if (direc == Dir.RIGHT) or (direc == Dir.LEFT):
                    face = self.conn[idCara][Dir.DOWN].face
                    dirRotacion = 1 if direc == Dir.LEFT else 3  # 1 = antihorario, 3 = horario
                else:  # (direc == Dir.UP) or (direc == Dir.DOWN)
                    face = self.conn[idCara][Dir.RIGHT].face
                    dirRotacion = 1 if direc == Dir.DOWN else 3  # 1 = antihorario, 3 = horario
                self.faces[face] = np.rot90(self.faces[face], dirRotacion)
                if type(celdasMovidas) == list:
                    for r in range(self.n):
                        for c in range(self.n):
                            celdasMovidas.append((face, r, c))

    def vecina(self, face, coord, direc):
        '''Devuelve el contenido de la celda vecina en la face vecina'''
        cxnVecina = self.conn[face][direc]
        caraVecina = cxnVecina.face
        xx = {False: coord, True: self.n - coord - 1}[cxnVecina.invert]
        return {Dir.DOWN: self.faces[caraVecina][0, xx],
                Dir.UP: self.faces[caraVecina][-1, xx],
                Dir.RIGHT: self.faces[caraVecina][xx, 0],
                Dir.LEFT: self.faces[caraVecina][xx, -1]
                }[cxnVecina.direct]

    def shuffle(self, qty=0):
        moves = []
        if qty <= 0:
            qty = self.n * 20
        for _ in range(qty):
            face = np.random.choice(list(Face.FACES))
            rrr = (np.random.randint(self.n), np.random.randint(self.n))
            rrr = (min(rrr), max(rrr))
            direction = [Dir.UP, Dir.DOWN, Dir.LEFT, Dir.RIGHT][np.random.randint(4)]
            multi = np.random.randint(1, 4)
            moves.append(f'{face}.{str(rrr[0] + 1)}:{str(rrr[1] + 1)}.{str(multi)}{direction}')
            self.unMovimiento(face, rrr, direction, multi)
        return ' '.join(moves)


def __controlPiezas(cube):
    piezas = {}
    for face in Face.FACES:
        for x in range(1, cube.n - 1):
            piezas[cube.faces[face][0, x].id] = cube.vecina(face, x, Dir.UP).id
        for x in range(1, cube.n - 1):
            piezas[cube.faces[face][-1, x].id] = cube.vecina(face, x, Dir.DOWN).id
        for x in range(1, cube.n - 1):
            piezas[cube.faces[face][x, 0].id] = cube.vecina(face, x, Dir.LEFT).id
        for x in range(1, cube.n - 1):
            piezas[cube.faces[face][x, -1].id] = cube.vecina(face, x, Dir.RIGHT).id
        piezas[cube.faces[face][0, 0].id + 'H'] = cube.vecina(face, 0, Dir.LEFT).id
        piezas[cube.faces[face][0, 0].id + 'A'] = cube.vecina(face, 0, Dir.UP).id
        piezas[cube.faces[face][0, -1].id + 'H'] = cube.vecina(face, cube.n - 1, Dir.UP).id
        piezas[cube.faces[face][0, -1].id + 'A'] = cube.vecina(face, 0, Dir.RIGHT).id
        piezas[cube.faces[face][-1, 0].id + 'H'] = cube.vecina(face, 0, Dir.DOWN).id
        piezas[cube.faces[face][-1, 0].id + 'A'] = cube.vecina(face, cube.n - 1, Dir.LEFT).id
        piezas[cube.faces[face][-1, -1].id + 'H'] = cube.vecina(face, cube.n - 1, Dir.RIGHT).id
        piezas[cube.faces[face][-1, -1].id + 'A'] = cube.vecina(face, cube.n - 1, Dir.DOWN).id
    return piezas


def test():
    cube = Cube(8)

    for face in Face.FACES:
        print(face)
        for i in range(cube.n):
            for j in range(cube.n):
                print(cube.faces[face][i, j].id, end=' ')
            print()
    print()

    print('piezas:')
    piezas = __controlPiezas(cube)
    print(piezas)

    print()
    print('Hacer movimientos')
    movim = input("Movimiento(s) : ")
    while movim:
        cube.mover(movim)
        for face in Face.FACES:
            print('Cara :', face)
            for i in range(cube.n):
                for j in range(cube.n):
                    print(cube.faces[face][i, j].id, end=' ')
                print()
            print()
        movim = input("Movimiento(s) : ")

    print()
    cant = input('Cant. random movim. : ')
    if not cant:
        cant = 0
    for _ in range(int(cant)):
        print(cube.shuffle(1))
        if piezas != __controlPiezas(cube):
            break

    for face in Face.FACES:
        print('Cara :', face)
        for i in range(cube.n):
            for j in range(cube.n):
                print(cube.faces[face][i, j].id, end=' ')
            print()
        print()

    print('control piezas...')
    piezas2 = __controlPiezas(cube)
    print()
    if piezas == piezas2:
        print('Las piezas se mantuvieron coherentes!!!')
        print()
    else:
        print('Algo anduvo mal...')
        print()
        for x in piezas:
            if piezas[x] != piezas2[x]:
                print('original', x, ':', piezas[x])
                print('ahora   ', x, ':', piezas2[x])
                print()


if __name__ == '__main__':
    test()
