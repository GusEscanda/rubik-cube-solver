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
            for level in self.levels:
                if var in self.dicts[level]:
                    return self.dicts[level][var]
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
    """
    Splits a string in two parts using a separator
    :param string: string to be split
    :param sep: separator, the string will be split at the first appearance of sep
    :return: tuple (the first part of the string until the 1st appearance of sep, the rest of the string)
    """
    words = stripWords(string, sep)
    first, rest = '', ''
    if len(words) > 0:
        first = words[0]
        if len(words) > 1:
            rest = sep.join(words[1:])
    return first, rest


def stripWords(string, sep=' '):
    """
    Returns a list of words, each of them without leading nor trailing blanks, using a separator
    :param string: the string to be split
    :param sep: the separator
    :return: the list of striped chunks of the string
    """
    return [w.strip() for w in string.split(sep) if w.strip()]


def rangeRC(rowInterval, columnInterval, step=(0, 0)):
    """
    Returns an iterable of tuples (row, column) with all the values in the rows interval and columns interval using
    independent steps for rows and columns, the step for each dimension is set according to the relationship between
    the initial and final value of it
    :param rowInterval: tuple (init, finish) values of the rows. If init > finish, the step will be negative
    :param columnInterval: tuple (init, finish) values of the columns. If init > finish, the step will be negative
    :param step: tuple (rows step, columns step), the default for each one is 1, -1 or 0 based on the relationship
                 of init and finish
    :return: An iterable of all the pairs (row, column)
    """
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
