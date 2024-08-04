# funciones varias que no tienen que ver con un proyecto en particular

from PyQt5 import QtCore, QtGui
from PyQt5 import Qt


class Vars:

    def __init__(self, niveles):
        # niveles: Lista de niveles de variables (local, global, etc.). Se consultaran en el orden dado.
        #          Puede ser una lista o un string. Los niveles pueden ser cualquier cosa que pueda ser key en un
        #          diccionario
        self.niveles = niveles[:]
        self.dicts = {}
        for n in niveles:
            self.dicts[n] = {}  # guarda un dicconario para cada nivel

    def set(self, var, valor, nivel=None):
        # var: el nombre de la variable que voy a setear
        # valor: el valor que le asigno a la variable
        # nivel: debe ser un elemento de self.niveles, si no lo es, lo agrego
        if nivel is None:
            nivel = self.niveles[0]
        if nivel not in self.dicts:  # es mas rapido chequear existencia en el diccionario
            self.dicts[nivel] = {}
            self.niveles.append(nivel)
        self.dicts[nivel][var] = valor
        return valor

    def get(self, var, default=None, nivel=''):
        if nivel:
            if nivel not in self.dicts:
                return default
            if var not in self.dicts[nivel]:
                return default
            return self.dicts[nivel][var]
        else:
            for n in self.niveles:
                if var in self.dicts[n]:
                    return self.dicts[n][var]
        return default

    def clear(self, nivel=None, var=None):
        if nivel is None:
            for n in self.niveles:
                self.dicts[n] = {}
        else:
            if var is None:
                self.dicts[nivel] = {}
            else:
                self.dicts[nivel].pop(var)

    def vars(self, nivel=None):
        if nivel is None:
            nivel = self.niveles[0]
        return self.dicts[nivel]


def primerPalabra(string, separador=' '):
    string = string.strip()
    if separador in string:
        i = string.find(separador)
        pal = string[:i]
        string = string[i + 1:]
    else:
        pal, string = string, ''
    return pal.strip(), string.strip()


def palabras(string, separador=' '):
    string = string.strip()
    pals = []
    while string:
        pp, string = primerPalabra(string, separador)
        pals.append(pp)
    return pals


def rango2X( desde, hasta, inc=(0,0) ):
    # desde: tupla (fila,columna)
    # hasta: tupla (fila,columna)
    # inc: tupla (incremento fila, incremento columna)
    # devuelve una lista de tuplas (i,j) que resultan de recorrer todo el rango por filas
    # - para cada coordenada, si desde < hasta recorre esa coordenada en forma descendente
    # - el incremento por defecto para cada coordenada es 1, -1 o 0 segun se necesite
    # - si para alguna coordenada el incremento se explicita incompatible con la relacion desde-hasta
    #   se toma 1, -1 o 0
    return rangoFC((desde[0], hasta[0]), (desde[1], hasta[1]), inc)


def rangoFC(rangoFilas, rangoColumnas, inc=(0, 0)):
    # rangoFilas: tupla (desde, hasta)
    # rangoColumnas: tupla (desde, hasta)
    # inc: tupla (incremento fila, incremento columna)
    # devuelve una lista de tuplas (i,j) que resultan de recorrer todo el rango por filas
    # - para cada coordenada, si desde < hasta recorre esa coordenada en forma descendente
    # - el incremento por defecto para cada coordenada es 1, -1 o 0 segun se necesite
    # - si para alguna coordenada el incremento se explicita incompatible con la relacion desde-hasta
    #   se toma 1, -1 o 0
    iDesde, iHasta = rangoFilas
    jDesde, jHasta = rangoColumnas
    if iDesde < iHasta:
        i = 1 if not inc[0] else inc[0]
        i = i if i > 0 else -i
    elif iDesde > iHasta:
        i = -1 if not inc[0] else inc[0]
        i = i if i < 0 else -i
    else:
        i = 0
    if jDesde < jHasta:
        j = 1 if not inc[1] else inc[1]
        j = j if j > 0 else -j
    elif jDesde > jHasta:
        j = -1 if not inc[1] else inc[1]
        j = j if j < 0 else -j
    else:
        j = 0
    inc = (i, j)
    ret = []
    i = iDesde
    while i >= min(iDesde, iHasta) and i <= max(iDesde, iHasta):
        j = jDesde
        while j >= min(jDesde, jHasta) and j <= max(jDesde, jHasta):
            ret.append((i, j))
            if inc[1]:
                j = j + inc[1]
            else:
                break
        if inc[0]:
            i = i + inc[0]
        else:
            break
    return ret


def alert(texto):
    msg = Qt.QMessageBox()
    msg.setText(texto)
    msg.exec()


class Clase:
    def __init__(self):
        pass
