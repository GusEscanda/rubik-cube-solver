# funciones varias que no tienen que ver con un proyecto en particular

from PyQt5 import QtCore, QtGui
from PyQt5 import Qt


class Vars:

    def __init__(self, levels):
        # levels: Lista de levels de variables (local, global, etc.). Se consultaran en el orden dado.
        #          Puede ser una lista o un string. Los levels pueden ser cualquier cosa que pueda ser key en un
        #          diccionario
        self.levels = levels[:]
        self.dicts = {}
        for n in levels:
            self.dicts[n] = {}  # guarda un dicconario para cada level

    def set(self, var, valor, level=None):
        # var: el nombre de la variable que voy a setear
        # valor: el valor que le asigno a la variable
        # level: debe ser un elemento de self.levels, si no lo es, lo agrego
        if level is None:
            level = self.levels[0]
        if level not in self.dicts:  # es mas rapido chequear existencia en el diccionario
            self.dicts[level] = {}
            self.levels.append(level)
        self.dicts[level][var] = valor
        return valor

    def get(self, var, default=None, level=''):
        if level:
            if level not in self.dicts:
                return default
            if var not in self.dicts[level]:
                return default
            return self.dicts[level][var]
        else:
            for n in self.levels:
                if var in self.dicts[n]:
                    return self.dicts[n][var]
        return default

    def clear(self, level=None, var=None):
        if level is None:
            for n in self.levels:
                self.dicts[n] = {}
        else:
            if var is None:
                self.dicts[level] = {}
            else:
                self.dicts[level].pop(var)

    def vars(self, level=None):
        if level is None:
            level = self.levels[0]
        return self.dicts[level]


def firstAndRest(string, sep=' '):
    words = stripWords(string, sep)
    first, rest = '', ''
    if len(words) > 0:
        first = words[0]
        if len(words) > 1:
            rest = sep.join(words[1:])
    return first, rest


def stripWords(string, sep=' '):
    return [w.strip() for w in string.split(sep) if w.strip()]


def rango2X(desde, hasta, inc=(0, 0)):
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
    while min(iDesde, iHasta) <= i <= max(iDesde, iHasta):
        j = jDesde
        while min(jDesde, jHasta) <= j <= max(jDesde, jHasta):
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


class Clase:
    def __init__(self):
        pass
