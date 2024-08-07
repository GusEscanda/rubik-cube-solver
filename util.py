# funciones varias que no tienen que ver con un proyecto en particular

from PyQt5 import QtCore, QtGui
from PyQt5 import Qt


class Vars:

    def __init__(self, levels):
        """
        Container that holds key:value pairs or vars (variables), organized in levels
        :param levels: list of levels to hold the vars (ie 'local', 'global', 'level_A', 'level_B', etc.) or a
                       string, in this case each char is a level (ie 'LG' as for local, global)
        """
        self.levels = levels[:]
        self.dicts = {level: {} for level in self.levels}

    def set(self, var, value, level=None):
        """
        Set the value of an existing or a new variable in a specified level
        :param var: Name of the variable
        :param value: Value to be set
        :param level: Level that holds the var, if level=None the first level will be used, if level doesn't exist create it.
        :return: The value just set
        """
        if level is None:
            level = self.levels[0]
        if level not in self.dicts:
            self.dicts[level] = {}
            self.levels.append(level)
        self.dicts[level][var] = value
        return value

    def get(self, var, default=None, level=None):
        """
        Get the value of a variable.
        :param var: Name of the variable
        :param default: Value to be returned if the variable doesn't exist
        :param level: Level that holds the variable, if not specified, search for it in the different levels, in order
        :return: The value of the first occurrence of var across the different levels or the default value
        """
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
        """
        Erase a single var, a complete level or all the levels
        :param level: The level to erase, if None erases all variables in all levels
        :param var: The name of the variable to erase, if None erases all variables in the specified level
        """
        if level is None:
            self.dicts = {level: {} for level in self.levels}
        else:
            if var is None:
                self.dicts[level] = {}
            else:
                self.dicts[level].pop(var)

    def vars(self, level=None):
        """
        Returns a dict containing the vars of a specified level
        :param level: The level that holds the vars to be returned, if None, the 1st level will be used
        :return: A dict containing the vars of the specified level
        """
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
