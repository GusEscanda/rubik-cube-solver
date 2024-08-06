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


def rangeRC(rowInterval, columnInterval, step=(0, 0)):
    # rowInterval: tupla (init, finish)
    # columnInterval: tupla (init, finish)
    # step: tupla (incremento fila, incremento columna)
    # devuelve un iterable de tuplas (r,c) que resultan de recorrer todo el rango por filas
    # - para cada coordenada, si init > finish recorre esa coordenada en forma descendente
    # - el incremento por defecto para cada coordenada es 1, -1 o 0 segun se necesite
    def safe_step(init, finish, s):
        if init < finish:
            return 1 if not s else abs(s)
        elif init > finish:
            return -1 if not s else -abs(s)
        else:
            return 0

    rInit, rFinish = rowInterval
    cInit, cFinish = columnInterval
    rStep, cStep = safe_step(rInit, rFinish, step[0]), safe_step(cInit, cFinish, step[1])

    r = rInit
    while min(rInit, rFinish) <= r <= max(rInit, rFinish):
        c = cInit
        while min(cInit, cFinish) <= c <= max(cInit, cFinish):
            yield r, c
            if cStep:
                c += cStep
            else:
                break
        if rStep:
            r += rStep
        else:
            break


class Clase:
    def __init__(self):
        pass
