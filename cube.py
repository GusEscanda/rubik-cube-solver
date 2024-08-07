# Empiezo a jugar con las estructuras de datos y procesos basicos de un cubo Rubik...

import numpy as np
from util import stripWords, firstAndRest, Clase, Vars

UP = (-1, 0)  # ( incremento en la fila, incremento en la columna )
DOWN = (1, 0)
RIGHT = (0, 1)
LEFT = (0, -1)
NULL = (0, 0)
DIRS = {'u': UP, 'd': DOWN, 'r': RIGHT, 'l': LEFT, '0': NULL}
COLORS = {"F": "red", "B": "orange", "U": "white", "D": "yellow", "L": "green", "R": "blue"}


class Cube:
    class ColorRel:
        def __init__(self, cubo):
            # crea un diccionario que tiene todas las relaciones entre los COLORS de este cubo
            #      'a' = anticlockwise
            #      'c' = clockwise
            #      'o' = opuesto
            self._colorRel = {}
            for _ in range(4):
                lcol = [cubo.c['U'][cubo.l - 1, cubo.l - 1].color,  # clockwise esquina superior derecha
                        cubo.c['R'][0, 0].color,
                        cubo.c['F'][0, cubo.l - 1].color
                        ]
                self.setRelColor('c', lcol)
                lcol.reverse()
                self.setRelColor('a', lcol)  # anticlockwise misma esquina
                lcol = [cubo.c['U'][cubo.l - 1, 0].color,  # clockwise esquina superior izquierda
                        cubo.c['F'][0, 0].color,
                        cubo.c['L'][0, cubo.l - 1].color
                        ]
                self.setRelColor('c', lcol)
                lcol.reverse()
                self.setRelColor('a', lcol)  # anticlockwise misma esquina
                cubo.mover('X')  # luego de 4 movimientos el cubo queda igual que al principio
            for color in self._colorRel:
                for ccc in self._colorRel:
                    if (ccc != color) and (ccc not in self._colorRel[color]['c']):
                        opuesto = ccc
                self.setRelColor('o', [color, opuesto])

        def setRelColor(self, rel, listaColores):
            # colorRel: diccionario indicando para cada color su relacion con los otros en este cubo
            # rel: relacion entre los COLORS de la lista.
            #      'a' = anticlockwise
            #      'c' = clockwise
            #      'o' = opuesto
            # listaColores: lista de COLORS que tienen la relacion rel entre si.
            for c in range(len(listaColores)):
                d = self._colorRel
                i = c
                if listaColores[i] not in d:
                    d[listaColores[i]] = {}
                d = d[listaColores[i]]
                for _ in range(1, len(listaColores)):
                    if rel not in d:
                        d[rel] = {}
                    d = d[rel]
                    i = (i + 1) if i < len(listaColores) - 1 else 0
                    if listaColores[i] not in d:
                        d[listaColores[i]] = {}
                    d = d[listaColores[i]]

        def listCols(self, rel, color1, color2=False):
            # devuelve una lista con el/los COLORS que tienen la relacion rel con los COLORS color1 y color2
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

    class Connection:
        def __init__(self, cara, dir, inv):
            self.cara = cara
            self.dir = dir
            self.inv = inv

    def __init__(self, tamanio=3, white=False):

        self.l = tamanio  # cada cara tendra l x l celdas
        self.white = white  # True si es un cubo con todas las caras blancas (util para la carga de la base de datos de metodos de armado)
        self.vars = Vars('c')  # Variables para conversion de coordenadas
        self.vars.set('T', 1)
        self.vars.set('t', 2)
        self.vars.set('L', 1)
        self.vars.set('l', 2)
        self.vars.set('B', tamanio)
        self.vars.set('b', tamanio - 1)
        self.vars.set('R', tamanio)
        self.vars.set('r', tamanio - 1)
        self.vars.set('C', (tamanio // 2) + 1)
        self.vars.set('c', (tamanio // 2) + (tamanio % 2))
        self.vars.set('i', 0)
        self.vars.set('j', 0)
        self.vars.set('k', 0)

        # crear las 6 caras
        self.c = {}  # Caras: diccionario de matrices de lxl cada celda es una clase generica que se
        #        inicializa en inicCeldas con la info que se necesite (color, etc)
        self.c['F'] = np.array([[Clase() for c in range(self.l)] for r in range(self.l)])  # Front
        self.c['B'] = np.array([[Clase() for c in range(self.l)] for r in range(self.l)])  # Back
        self.c['U'] = np.array([[Clase() for c in range(self.l)] for r in range(self.l)])  # Up
        self.c['D'] = np.array([[Clase() for c in range(self.l)] for r in range(self.l)])  # Down
        self.c['L'] = np.array([[Clase() for c in range(self.l)] for r in range(self.l)])  # Left
        self.c['R'] = np.array([[Clase() for c in range(self.l)] for r in range(self.l)])  # Right

        # llenar las celdas (para otro tipo de cubo, con info distina en las celdas, escribir otro metodo de llenado)
        self.inicCeldas()

        # conexiones entre las caras (que cara conecta con cual en cada uno de sus lados y si las coordenadas se invierten al pasar a la cara contigua
        self.conn = {'F': {}, 'B': {}, 'U': {}, 'D': {}, 'L': {}, 'R': {}}
        # conectar la cara frontal con las adyacentes 
        self.conn['F'][UP] = self.Connection(cara='U', dir=UP, inv=False)
        self.conn['F'][DOWN] = self.Connection(cara='D', dir=DOWN, inv=False)
        self.conn['F'][LEFT] = self.Connection(cara='L', dir=LEFT, inv=False)
        self.conn['F'][RIGHT] = self.Connection(cara='R', dir=RIGHT, inv=False)
        # conectar la cara de arriba con las adyacentes 
        self.conn['U'][UP] = self.Connection(cara='B', dir=DOWN, inv=True)
        self.conn['U'][DOWN] = self.Connection(cara='F', dir=DOWN, inv=False)
        self.conn['U'][LEFT] = self.Connection(cara='L', dir=DOWN, inv=False)
        self.conn['U'][RIGHT] = self.Connection(cara='R', dir=DOWN, inv=True)
        # conectar la cara de abajo con las adyacentes 
        self.conn['D'][UP] = self.Connection(cara='F', dir=UP, inv=False)
        self.conn['D'][DOWN] = self.Connection(cara='B', dir=UP, inv=True)
        self.conn['D'][LEFT] = self.Connection(cara='L', dir=UP, inv=True)
        self.conn['D'][RIGHT] = self.Connection(cara='R', dir=UP, inv=False)
        # conectar la cara de atras con las adyacentes 
        self.conn['B'][UP] = self.Connection(cara='U', dir=DOWN, inv=True)
        self.conn['B'][DOWN] = self.Connection(cara='D', dir=UP, inv=True)
        self.conn['B'][LEFT] = self.Connection(cara='R', dir=LEFT, inv=False)
        self.conn['B'][RIGHT] = self.Connection(cara='L', dir=RIGHT, inv=False)
        # conectar la cara izquierda con las adyacentes 
        self.conn['L'][UP] = self.Connection(cara='U', dir=RIGHT, inv=False)
        self.conn['L'][DOWN] = self.Connection(cara='D', dir=RIGHT, inv=True)
        self.conn['L'][LEFT] = self.Connection(cara='B', dir=LEFT, inv=False)
        self.conn['L'][RIGHT] = self.Connection(cara='F', dir=RIGHT, inv=False)
        # conectar la cara derecha con las adyacentes 
        self.conn['R'][UP] = self.Connection(cara='U', dir=LEFT, inv=True)
        self.conn['R'][DOWN] = self.Connection(cara='D', dir=LEFT, inv=False)
        self.conn['R'][LEFT] = self.Connection(cara='F', dir=LEFT, inv=False)
        self.conn['R'][RIGHT] = self.Connection(cara='B', dir=RIGHT, inv=False)

        if not self.white:
            self.colorRel = self.ColorRel(self)
        return

    def inicCeldas(self):
        for cara in ('FBUDLR'):
            for f in range(self.l):
                for c in range(self.l):
                    self.c[cara][f, c].color = COLORS[cara] if not self.white else 'white'
                    self.c[cara][f, c].id = cara + ('000' + str(f + 1))[-3:] + ('000' + str(c + 1))[-3:]

    def str2coord(self, sCoord, checkRangoCero=True):
        c = eval(sCoord, self.vars.vars())
        if checkRangoCero:
            c = c - 1  # resto 1 para que esté expresado entre 0 y (self.l-1)
            c = max(0, min(self.l - 1, c))  # para que no pinche si la coordenada quedó fuera de rango
        return c

    def str2rango(self, sRango, checkRangoCero=True):
        desde, hasta = firstAndRest(sRango, ':')
        hasta = hasta if hasta else desde
        desde = self.str2coord(desde, checkRangoCero)
        hasta = self.str2coord(hasta, checkRangoCero)
        if desde > hasta:
            desde, hasta = hasta, desde
        return desde, hasta

    def str2movim(self, mov):
        # convierte mov a una tupla (idCara, rango, direc, multip) para llamar multip veces al metodo unMovimiento
        # mov puede tener la notacion estandar de rubik (F,B,U,D,L,R,M,E,S,x,y,z,minusculas,w,',2)
        # o bien ser de la forma <idCara>[.<rango desde>[:<rango hasta>]].<direccion> donde:
        # <idCara> = "F", "B", "U", "D", "L" o "R"
        # <rango desde> y <rango hasta> = numero de fila/columna a mover (desde y hasta son inclusive)
        #     - numeros explicitos indican una fila/columna se cuenta desde la izquierda/arriba
        #     - la numeracion va desde 1 a self.l 
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
        #       SOLO por el campo “direc”.
        #     - El orden de <rango desde> y <rango hasta> es indistinto (2:5 es equivalente a 5:2)
        # <direccion> = "u", "d", "l", "r", "c", "a" para up, down, left, right, clockwise y anticlockwise
        #     - si la direccion es clockwise o anticlockwise <rango desde>:<rango hasta> se omite / ignora
        #     - se puede anteponer a la letra de direccion un digito multiplicador, 
        #          el movimiento se realizara esa cantidad de veces 
        #          1: default,    2: el mas logico de usar,    3: raro,    >3: ridiculo
        # cualquier movimiento que comience con '><' se considera espejado respecto a un plano definido por los
        # ejes Z e Y
        mm = mov
        idCara, direc, rango, multip = '', NULL, (0, 0), 0

        espejo = False
        if mm[0:2] == '><':
            espejo = True  # si está en espejo, proceso normalmente y solo al final considero esa situación
            mm = mm[2:]

        if '.' in mm:  # mov : <idCara>[.<rango desde>[:<rango hasta>]].<direccion>
            idCara, mm = firstAndRest(mm, '.')
            idCara = idCara.upper()
            rango = (1, 1)  # solo para que tenga algun valor en caso de no especificarse
            if '.' in mm:  # hay un rango especificado
                rr, mm = firstAndRest(mm, '.')
                rango = self.str2rango(rr)
            multip = 1
            if mm[0] in '123456789':  # hay un multiplicador especificado
                multip, mm = int(mm[:1]), mm[1:]
            mm = mm[:1]
            if mm in 'udlrUDLR':
                direc = DIRS[mm.lower()]
                mm = ''  # ya no debo procesar mas a mm, tengo todos los datos para devolver
            else:  # mm in 'caCA' (clockwise o anticlockwise) => simulo un movimiento tipo "Rubik estandar"
                mm = idCara + str(multip) + ("'" if mm in 'aA' else "")

        if mm:  # continúo procesando, mm es un movimiento tipo estandar de Rubik (F,B,U,D,L,R,M,E,S,x,y,z,minusculas,w,',2)
            idCara = mm[0]
            mm = mm[1:]
            if mm:
                if mm[0] in 'wW':  # notacion w -> notacion lowercase
                    idCara = idCara.lower()
                    mm = mm[1:]
            anti = ("'" in mm)  # movimiento antihorario
            mm = mm[:mm.find("'")] + mm[mm.find("'") + 1:]  # saca el ' dejando solo el numero si lo hubiere
            multip = (1 if not mm else int(mm))  # si todavía hay un numero, ese es el multiplicador, si no es 1

            rango = (0, 0)
            if idCara in 'FBLRUD':
                rango = (0, 0)
            elif idCara in 'fblrud':
                # en cubos > 3x3, lo coherente es considerar el bloque central completo (mueve todo menos la cara opuesta)
                rango = (0, self.l - 2)
            elif idCara in 'MESmes':  # m e s (minuscula) no tiene sentido pero por simplicidad lo hago equivalente a M E S
                # bloque central sin las caras laterales
                rango = (1, self.l - 2)
            elif idCara in 'XYZxyz':  # X Y Z lo hago equivalente a x y z (esto si se suele usar en upper y lower indistintamente)
                # rango completo, cambia la orientacion del cubo
                rango = (0, self.l - 1)

            cara, direc = '', ''
            if idCara in "FfSsZz":
                cara, direc = 'R', DOWN
            elif idCara in "Bb":
                cara, direc = 'L', DOWN
            elif idCara in "LlMm":
                cara, direc = 'F', DOWN
            elif idCara in "RrXx":
                cara, direc = 'B', DOWN
            elif idCara in "UuYy":
                cara, direc = 'F', LEFT
            elif idCara in "DdEe":
                cara, direc = 'F', RIGHT
                rango = (self.l - 1 - rango[1],
                         self.l - 1 - rango[0])  # solo en el caso de mirar desde abajo, invierto la seleccion del rango
            idCara = cara
            if anti:  # era antihorario => invierto la direccion
                direc = (-direc[0], -direc[1])

        if espejo:
            if idCara == 'R':
                idCara = 'L'
            elif idCara == 'L':
                idCara = 'R'
            if direc == UP or direc == DOWN:
                rango = (self.l - 1 - rango[1], self.l - 1 - rango[0])
            elif direc == LEFT or direc == RIGHT:
                direc = (-direc[0], -direc[1])

        return idCara, rango, direc, multip

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
            idCara, rango, direc, multip = self.str2movim(espejo + mov)
            if haciaAtras:
                direc = (-direc[0], -direc[1])
            self.unMovimiento(idCara, rango, direc, multip, celdasMovidas)
            if animacion:
                connCara = self.conn[idCara]
                if (direc == RIGHT) or (direc == LEFT):
                    caraAnticlockwise = connCara[UP].cara if direc == RIGHT else connCara[DOWN].cara
                else:  # (direc == UP) or (direc == DOWN)
                    caraAnticlockwise = connCara[LEFT].cara if direc == UP else connCara[RIGHT].cara
        return celdasMovidas, caraAnticlockwise

    def readWriteCeldas(self, cara, rango, direc, set=False, celdas=[], celdasMovidas=False):
        # - Lee (y eventualmente reemplaza) un rango de celdas de la matriz de una cara del cubo
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
        if direc == RIGHT:
            f, c = rango[0], 0
            rf, rc = rinv, 0
        elif direc == LEFT:
            f, c = rango[0], self.l - 1
            rf, rc = rinv, 0
        elif direc == DOWN:
            f, c = 0, rango[0]
            rf, rc = 0, rinv
        elif direc == UP:
            f, c = self.l - 1, rango[0]
            rf, rc = 0, rinv
        ret = []
        while (0 <= f < self.l) and (0 <= c < self.l):
            r = []
            for xx in range(abs(rango[1] - rango[0]) + 1):
                r.append(self.c[cara][f + xx * rf, c + xx * rc])
            ret.append(r)
            if set:
                for xx in range(abs(rango[1] - rango[0]) + 1):
                    self.c[cara][f + xx * rf, c + xx * rc] = celdas[len(ret) - 1, xx]
                if type(celdasMovidas) == list:
                    for xx in range(abs(rango[1] - rango[0]) + 1):
                        celdasMovidas.append((cara, f + xx * rf, c + xx * rc))
            f, c = f + direc[0], c + direc[1]
        return np.array(ret)

    def unMovimiento(self, idCara, rango, direc, multip=1, celdasMovidas=False):
        for _ in range(multip):
            # Hace un movimiento del cubo (solo hace movimientos para direccciones 'udlr')
            cara, rr, dd = idCara, rango, direc
            # copiar el sector de celdas dado por rango y direc, en las distintas caras del cubo, rotando 4 veces en direccion direc
            celdas = self.readWriteCeldas(cara, rr, dd)
            for _ in range(4):
                conn = self.conn[cara][dd]
                cara, dd = conn.cara, conn.dir
                if conn.inv:
                    rr = (self.l - rr[0] - 1, self.l - rr[1] - 1)
                celdas = self.readWriteCeldas(cara, rr, dd, set=True, celdas=celdas, celdasMovidas=celdasMovidas)
            # cuando el rango incluye uno o ambos bordes rotar la(s) cara(s) lateral(es), en sentido horario o antihorario
            if min(rango) == 0:
                if (direc == RIGHT) or (direc == LEFT):
                    cara = self.conn[idCara][UP].cara
                    dirRotacion = 1 if direc == RIGHT else 3  # 1 = antihorario, 3 = horario
                else:  # (direc == UP) or (direc == DOWN)
                    cara = self.conn[idCara][LEFT].cara
                    dirRotacion = 1 if direc == UP else 3  # 1 = antihorario, 3 = horario
                self.c[cara] = np.rot90(self.c[cara], dirRotacion)
                if type(celdasMovidas) == list:
                    for f in range(self.l):
                        for c in range(self.l):
                            celdasMovidas.append((cara, f, c))
            if max(rango) == self.l - 1:
                if (direc == RIGHT) or (direc == LEFT):
                    cara = self.conn[idCara][DOWN].cara
                    dirRotacion = 1 if direc == LEFT else 3  # 1 = antihorario, 3 = horario
                else:  # (direc == UP) or (direc == DOWN)
                    cara = self.conn[idCara][RIGHT].cara
                    dirRotacion = 1 if direc == DOWN else 3  # 1 = antihorario, 3 = horario
                self.c[cara] = np.rot90(self.c[cara], dirRotacion)
                if type(celdasMovidas) == list:
                    for f in range(self.l):
                        for c in range(self.l):
                            celdasMovidas.append((cara, f, c))

    def vecina(self, cara, coord, direc):
        '''Devuelve el contenido de la celda vecina en la cara vecina'''
        cxnVecina = self.conn[cara][direc]
        caraVecina = cxnVecina.cara
        xx = {False: coord, True: self.l - coord - 1}[cxnVecina.inv]
        return {DOWN: self.c[caraVecina][0, xx],
                UP: self.c[caraVecina][-1, xx],
                RIGHT: self.c[caraVecina][xx, 0],
                LEFT: self.c[caraVecina][xx, -1]
                }[cxnVecina.dir]

    def mezclar(self, cantMovim=0):
        ret = ''
        if cantMovim <= 0:
            cantMovim = self.l * 20
        for _ in range(cantMovim):
            cara = np.random.choice(['F', 'B', 'U', 'D', 'L', 'R'])
            rrr = (np.random.randint(self.l), np.random.randint(self.l))
            rrr = (min(rrr), max(rrr))
            direc = np.random.choice(['u', 'd', 'l', 'r'])
            multip = np.random.randint(1, 4)
            ret = ret + cara + '.' + str(rrr[0] + 1) + ':' + str(rrr[1] + 1) + '.' + str(multip) + direc + ' '
            self.unMovimiento(cara, rrr, DIRS[direc], multip)
        return ret


def __controlPiezas(cubo):
    piezas = {}
    for cara in 'FBUDLR':
        for x in range(1, cubo.l - 1):
            piezas[cubo.c[cara][0, x].id] = cubo.vecina(cara, x, UP).id
        for x in range(1, cubo.l - 1):
            piezas[cubo.c[cara][-1, x].id] = cubo.vecina(cara, x, DOWN).id
        for x in range(1, cubo.l - 1):
            piezas[cubo.c[cara][x, 0].id] = cubo.vecina(cara, x, LEFT).id
        for x in range(1, cubo.l - 1):
            piezas[cubo.c[cara][x, -1].id] = cubo.vecina(cara, x, RIGHT).id
        piezas[cubo.c[cara][0, 0].id + 'H'] = cubo.vecina(cara, 0, LEFT).id
        piezas[cubo.c[cara][0, 0].id + 'A'] = cubo.vecina(cara, 0, UP).id
        piezas[cubo.c[cara][0, -1].id + 'H'] = cubo.vecina(cara, cubo.l - 1, UP).id
        piezas[cubo.c[cara][0, -1].id + 'A'] = cubo.vecina(cara, 0, RIGHT).id
        piezas[cubo.c[cara][-1, 0].id + 'H'] = cubo.vecina(cara, 0, DOWN).id
        piezas[cubo.c[cara][-1, 0].id + 'A'] = cubo.vecina(cara, cubo.l - 1, LEFT).id
        piezas[cubo.c[cara][-1, -1].id + 'H'] = cubo.vecina(cara, cubo.l - 1, RIGHT).id
        piezas[cubo.c[cara][-1, -1].id + 'A'] = cubo.vecina(cara, cubo.l - 1, DOWN).id
    return piezas


def test():
    cubo = Cube(8)

    for cara in 'FBUDLR':
        print(cara)
        for i in range(cubo.l):
            for j in range(cubo.l):
                print(cubo.c[cara][i, j].id, end=' ')
            print()
    print()

    print('piezas:')
    piezas = __controlPiezas(cubo)
    print(piezas)

    print()
    print('Hacer movimientos')
    movim = input("Movimiento(s) : ")
    while movim:
        cubo.mover(movim)
        for cara in 'FBUDLR':
            print('Cara :', cara)
            for i in range(cubo.l):
                for j in range(cubo.l):
                    print(cubo.c[cara][i, j].id, end=' ')
                print()
            print()
        movim = input("Movimiento(s) : ")

    print()
    cant = input('Cant. random movim. : ')
    if not cant:
        cant = 0
    for _ in range(int(cant)):
        print(cubo.mezclar(1))
        if piezas != __controlPiezas(cubo):
            break

    for cara in 'FBUDLR':
        print('Cara :', cara)
        for i in range(cubo.l):
            for j in range(cubo.l):
                print(cubo.c[cara][i, j].id, end=' ')
            print()
        print()

    print('control piezas...')
    piezas2 = __controlPiezas(cubo)
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
