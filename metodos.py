import numpy as np
import copy
from pathlib import Path
import json

import cuboBasics as cb
from varios import palabras, primerPalabra, rangoFC, Clase, alert, Vars
from cuboBasics import dirArriba, dirAbajo, dirDerecha, dirIzquierda, dirNull, dirs, colores


def celdaEquiv(cubo, cara, fila, columna, posicionCubo):
    # Devuelve la cara, fila, columna donde estaría esta celda si hiciera los movimientos inversos a los de posicionCubo
    if posicionCubo == '-':
        posicionCubo = ''
    for movim in reversed(palabras(posicionCubo)):
        multip = (1 if '2' not in movim else 2)
        prima = ("'" in movim)
        movim = movim[0]
        dd, horario = dirNull, False
        if movim in 'YUD':  # asumo movimiento en sentido Y o U, luego ajusto si era D
            if cara in 'UD':  # para U o D, Y es un movimiento horario o antihorario
                horario = (cara == 'U')
                if movim != 'Y' and movim != cara:
                    multip = 0  # esa celda no se mueve
            else:  # cara in FBLR
                dd = dirIzquierda
                if (movim == 'U' and fila > 0) or (movim == 'D' and fila < cubo.l - 1):
                    multip = 0  # esa celda no se mueve
        elif movim in 'XRL':  # asumo movimiento en sentido X o R, luego ajusto si era L
            if cara in 'RL':  # para R o L, X es un movimiento horario o antihorario
                horario = (cara == 'R')
                if movim != 'X' and movim != cara:
                    multip = 0  # esa celda no se mueve
            elif cara == 'B':
                dd = dirAbajo
                if (movim == 'R' and columna > 0) or (movim == 'L' and columna < cubo.l - 1):
                    multip = 0  # esa celda no se mueve
            else:  # cara in FUD
                dd = dirArriba
                if (movim == 'L' and columna > 0) or (movim == 'R' and columna < cubo.l - 1):
                    multip = 0  # esa celda no se mueve
        elif movim in 'ZFB':  # asumo movimiento en sentido Z o F, luego ajusto si era B
            if cara in 'FB':  # para F o B, Z es un movimiento horario o antihorario
                horario = (cara == 'F')
                if movim != 'Z' and movim != cara:
                    multip = 0  # esa celda no se mueve
            elif cara == 'U':
                dd = dirDerecha
                if (movim == 'B' and fila > 0) or (movim == 'F' and fila < cubo.l - 1):
                    multip = 0  # esa celda no se mueve
            elif cara == 'D':
                dd = dirIzquierda
                if (movim == 'F' and fila > 0) or (movim == 'B' and fila < cubo.l - 1):
                    multip = 0  # esa celda no se mueve
            elif cara == 'L':
                dd = dirArriba
                if (movim == 'B' and columna > 0) or (movim == 'F' and columna < cubo.l - 1):
                    multip = 0  # esa celda no se mueve
            else:  # cara == 'R':
                dd = dirAbajo
                if (movim == 'F' and columna > 0) or (movim == 'B' and columna < cubo.l - 1):
                    multip = 0  # esa celda no se mueve
        if movim in 'DLB':  # movimientos opuestos a XYZ y URF => invierto el sentido
            horario = not horario
            dd = (-dd[0], -dd[1])
        if not prima:  # considero el movimiento opuesto => si NO es ' invierto el sentido
            horario = not horario
            dd = (-dd[0], -dd[1])
        # ahora multip veces cambio de cara, fila y columna segun indiquen dd y horario
        for _ in range(multip):
            if dd == dirNull:  # solo girar, no cambia la cara
                if horario:
                    fila, columna = columna, cubo.l - fila - 1
                else:
                    fila, columna = cubo.l - columna - 1, fila
            else:
                # pasar a la cara contigua (hacia dd) y calcular la nueva fila y columna
                conn = cubo.conn[cara][dd]
                if (dd in (dirArriba, dirAbajo)) != (conn.dir in (dirArriba, dirAbajo)):
                    fila, columna = columna, fila  # si cambio la direccion de vertical a horizontal o viceversa, intercambio filas con columnas
                if conn.dir in (dirArriba, dirAbajo):
                    if (dd[0] + dd[1]) != (
                            conn.dir[0] + conn.dir[1]):  # si cambio el sentido, de ascendente a descendente o viceversa
                        fila = cubo.l - fila - 1
                    if conn.inv:  # si se invierte la otra coordenada
                        columna = cubo.l - columna - 1
                else:  # conn.dir in (dirIzquierda,dirDerecha)
                    if (dd[0] + dd[1]) != (
                            conn.dir[0] + conn.dir[1]):  # si cambio el sentido, de izquierda a derecha o viceversa
                        columna = cubo.l - columna - 1
                    if conn.inv:  # si se invierte la otra coordenada
                        fila = cubo.l - fila - 1
                cara, dd = conn.cara, conn.dir
    return (cara, fila, columna)


def matchCelda(vars, coloresPosibles, relColores, colorCelda):
    # vars: objeto de tipo Vars, contiene los valores de las variables locales y globales definidas por el usuario
    # coloresPosibles: uno o varios colores separados por espacios, con que uno coincida se considera que hay coincidencia. Cada uno puede ser:
    #     - un color específico (white, yellow, red, orange, blue, green)
    #     - "->nombre" asigna el color de la celda a una variable llamada "nombre"
    #     - "==nombre" el color de la celda debe coincidir con el PREVIAMENTE ASIGNADO a la variable "nombre"
    #     - "!=nombre" el color de la celda debe ser distinto al PREVIAMENTE ASIGNADO a la variable "nombre"
    #     - "c=nombre1[,nombre2]" el color de la celda debe encontrarse a continuacion de los especificados 
    #       en las variables nombre1 y nombre2 en sentido horario dentro de este cubo ("c"lockwise).
    #       si se especifica un solo nombre, debe ser uno de los posibles siguientes en ese sentido (todos
    #       los demas excepto el de la cara opuesta o él mismo)
    #     - "a=nombre1[,nombre2]" idem anterior pero en sentido antihorario ("a"nticlockwise)
    #     - "o=nombre" el color de la celda debe coincidir con el correspondiente al opuesto (dentro de este cubo)
    #       al especificado en "nombre"
    # relColores: indica la relacion de colores que hay en este cubo (clockwise, anticlockwise, opuestos)
    # colorCelda: el color de la celda que quiero ver si matchea
    mCelda = False  # match si alguno de los colores posibles matchea
    for color in palabras(coloresPosibles):
        debeCoincidir = True
        if color[0:2] == '->':  # asigna a la variable el color de la celda actual
            color = vars.set(color[2:], colorCelda, 'l')
        elif color[0:2] == '=>':  # asigna a una variable global el color de la celda actual
            color = vars.set(color[2:], colorCelda, 'g')
        elif color[0:2] == '==':  # el color de la celda debe coincidir con el de la variable
            color = vars.get(color[2:], default='')
        elif color[0:2] == '!=':  # el color de la celda NO debe coincidir con el de la variable
            color = vars.get(color[2:], default='')
            debeCoincidir = False
        elif color[0:2] in 'a= c= o= a! c! o!':
            debeCoincidir = (color[1] == '=')
            c1, c2 = primerPalabra(color[2:], ',')
            c1 = vars.get(c1, default='')
            c2 = vars.get(c2, default='')
            color = relColores.listCols(color[0], c1, c2)
        if debeCoincidir == (colorCelda in color):  # si (debeCoincidir y coincide) o (no debeCoincidir y no coincide)
            mCelda = True
            break
    return mCelda


def matchCubo(cubo, vars, listaCeldas, posiciones=['-']):
    # devuelve match, posicion
    #    match = verdadero si para alguna de las posiciones equivalentes del cubo, todas las celdas de la listaCeldas matchean con la correspondiente celda del cubo
    #    posicion = string con la lista de movimientos a realizar para que el cubo quede en la posicion en que se halló el match o en la que mas cantidad de celdas matchearon
    # cubo: cubo donde estoy verificando el matching
    # vars: objeto de tipo Vars, contiene los valores de las variables locales y globales definidas por el usuario
    # listaCeldas es una lista donde cada elemento es una tupla de la forma:
    #    cara: 'FBUDLR'
    #    fila: fila
    #    columna: columna
    #    coloresPosibles: uno o varios colores separados por espacios, con que uno coincida se considera que hay coincidencia. Cada uno puede ser:
    #        - un color específico (white, yellow, red, orange, blue, green)
    #        - "->nombre" asigna el color de la celda a una variable llamada "nombre"
    #        - "==nombre" el color de la celda debe coincidir con el PREVIAMENTE ASIGNADO a la variable "nombre"
    #        - "!=nombre" el color de la celda debe ser distinto al PREVIAMENTE ASIGNADO a la variable "nombre"
    #        - "c=nombre1[,nombre2]" el color de la celda debe encontrarse a continuacion de los especificados 
    #          en las variables nombre1 y nombre2 en sentido horario dentro de este cubo ("c"lockwise).
    #          si se especifica un solo nombre, debe ser uno de los posibles siguientes en ese sentido (todos
    #          los demas excepto el de la cara opuesta o él mismo)
    #        - "a=nombre1[,nombre2]" idem anterior pero en sentido antihorario ("a"nticlockwise)
    #        - "o=nombre" el color de la celda debe coincidir con el correspondiente al opuesto (dentro de este cubo)
    #          al especificado en "nombre"
    maxMatches, maxPosicion, matchAlguna = 0, "-", False
    for posicion in posiciones:
        if posicion == '-':
            posicion = ''
        vars.clear('l')  # reseteo los colores variables locales para esta posicion
        match, cantMatches = True, 0
        for lc in listaCeldas:
            if type(lc) is tuple:
                (cara, fila, columna, coloresPosibles) = lc
                cara, fila, columna = celdaEquiv(cubo, cara, fila, columna, posicion)
                mCelda = matchCelda(vars, coloresPosibles, cubo.relColores, cubo.c[cara][fila, columna].color)
                if mCelda:
                    cantMatches = cantMatches + 1
                match = match and mCelda
            else:  # es una lista de conciciones a evaluar como 'or'
                orMatch = False
                for lcOr in lc:
                    (cara, fila, columna, coloresPosibles) = lcOr
                    cara, fila, columna = celdaEquiv(cubo, cara, fila, columna, posicion)
                    mCelda = matchCelda(vars, coloresPosibles, cubo.relColores, cubo.c[cara][fila, columna].color)
                    orMatch = orMatch or mCelda
                if orMatch:
                    cantMatches = cantMatches + 1
                match = match and orMatch
        if cantMatches > maxMatches:
            maxMatches, maxPosicion = cantMatches, posicion
        matchAlguna = matchAlguna or match
    return matchAlguna, maxPosicion


class Sol():
    # Registro conteniendo la info necesaria para mostrar/ejecutar la resolucion del cubo
    #   - nivel: Profundidad del arbol de metodos recorrida hasta aqui (para poder mostrar indentados los metodos)
    #   - tipo: Tipo de renglon en la ejecucion, valores posibles:
    #           'Met' titulo de un metodo
    #           'Pos' movimientos para posicionar antes de ejecutar el algoritmo
    #           'Alg' algoritmo
    #   - texto: Id del metodo o movimientos del posicionamiento o algoritmo
    #   - hizo: Verdadero si este metodo se aplico, falso si solo se invoco pero no se utilizo
    #   - metodo: Metodo aplicado (objeto)
    #   - mirror: Si se aplico el metodo espejado o no
    #   - vars: Copia de los valores que tenían las variables en este momento de la ejecución (sobre todo me interesan i,j,k)
    def __init__(self, nivel, tipo, texto, hizo, metodo, mirror, vars):
        self.nivel = nivel
        self.tipo = tipo
        self.texto = texto
        self.hizo = hizo
        self.metodo = metodo
        self.mirror = mirror
        self.vars = copy.deepcopy(vars)


def cantMovim(soluc):
    c = 0
    for s in soluc:
        if s.tipo in 'Alg/Pos':
            c = c + len(palabras(s.texto))
    return c


def ejecutarMetodo(cubo, met, solucion, nivel=0):
    # nivel: Para poder mostrar indentados los metodos y sub metodos que se van utilizando.
    # cubo: Cubo que se va a resolver (se modifica durante la ejecucion del metodo)
    # solucion: Lista de los metodos utilizados en la ejecucion. Cada elemento de la lista es un objeto de tipo Sol
    # met: objeto de la clase Metodo, con los siguientes campos:
    #     id: string descriptivo del metodo (para mostrar cuando arrancan los algoritmos correspondientes a este metodo)
    #     minLado: tamaño minimo que tiene que tener el cubo para ejecutar este metodo
    #     modo: 'Repeat', 'Once', 'Twice' , '<n> Times', 'Best Match'
    #     subMetodos: [idSubMetodo1, idSubMetodo2, idSubMetodo3, .... ]
    #     until1st: '-', 'Failure', 'Success'
    #     listaCondiciones: [cond1, cond2, cond3, .... ] # por claridad solo especificar subMetodos o listaCondiciones pero no ambas...
    #     mirror: buscar o no la posicion en espejo para las condiciones
    #     posiciones: lista de posiciones del cubo en que se buscan las condiciones
    #     algoritmo: string
    if cubo.l < met.minLado:
        solucion.append(Sol(nivel, 'Met', met.id, False, met, False, cubo.vars))
        return (False, True)
    # la opcion 'repeat' es en realidad 6(l^2) veces, para no entrar en un loop infinito si hay un error en el metodo
    cantVeces = 6 * (cubo.l ** 2) if met.modo.upper() == 'REPEAT' else 0
    cantVeces = 1 if met.modo.upper() in 'ONCE / BEST MATCH' else cantVeces
    cantVeces = 2 if met.modo.upper() == 'TWICE' else cantVeces
    if 'TIMES' in met.modo.upper():
        cantVeces = int(palabras(met.modo)[0])
    bestMatch = (met.modo.upper() == 'BEST MATCH')
    if met.rangoI:
        ddeI, htaI = cubo.str2rango(met.rangoI, checkRangoCero=False)
        cubo.vars.set('i', ddeI)
    if met.rangoJ:
        ddeJ, htaJ = cubo.str2rango(met.rangoJ, checkRangoCero=False)
        cubo.vars.set('j', ddeJ)
    if met.rangoK:
        ddeK, htaK = cubo.str2rango(met.rangoK, checkRangoCero=False)
        cubo.vars.set('k', ddeK)
    iSol = len(solucion)
    solucion.append(Sol(nivel, 'Met', met.id, False, met, False, cubo.vars))
    hizoAlgo, success = False, False
    seguir, cant = True, 0
    while seguir and (cant < cantVeces):
        if len(solucion) > 20000:  # solo para debug de algunos metodos
            print('OVERFLOW !!!!')
            print(
                'metodo: {0} len(soluc): {1}, cant: {2}, cantVeces: {3}'.format(met.id, len(solucion), cant, cantVeces))
            solucion.append(Sol(nivel + 1, 'Pos', 'X2 X2 X2 X2', True, met, False, cubo.vars))
            break
        seguir = False
        for idSubMetodo in met.subMetodos:
            (hizo, success) = ejecutarMetodo(cubo, met.metodo(idSubMetodo), solucion, nivel + 1)
            hizoAlgo = hizoAlgo or hizo
            seguir = seguir or hizo
            if success and met.until1st.upper() == 'SUCCESS':
                break
            if not success and met.until1st.upper() == 'FAILURE':
                break
        listaCeldas = cond2ListaCeldas(cubo, cubo.vars, met.listaCondiciones)
        hizo = False
        if len(listaCeldas) > 0:
            match, posicion = matchCubo(cubo, met.vars, listaCeldas, met.posiciones)
            success = success or match
            if match or bestMatch:
                algoritmo = met.algoritmo
                algoritmo = algoritmo.replace('i', str(cubo.vars.get('i', 'i')))
                algoritmo = algoritmo.replace('j', str(cubo.vars.get('j', 'j')))
                algoritmo = algoritmo.replace('k', str(cubo.vars.get('k', 'k')))
                cubo.mover(posicion + ' ' + algoritmo)
                hizo = (posicion != '' or algoritmo != '')
                if hizo:
                    if posicion != '':
                        solucion.append(Sol(nivel + 1, 'Pos', posicion, hizo, met, False, cubo.vars))
                    if algoritmo != '':
                        solucion.append(Sol(nivel + 1, 'Alg', algoritmo, hizo, met, False, cubo.vars))
                hizoAlgo = hizoAlgo or hizo
                seguir = seguir or hizo
        if not hizo and met.mirror and len(
                listaCeldas) > 0:  # si no se hizo movimientos y lo especifica el metodo, pruebo con las condiciones espejadas
            for c in range(len(listaCeldas)):
                if type(listaCeldas[c]) is tuple:
                    listaCeldas[c] = mirrorCelda(cubo, listaCeldas[c])
                elif type(listaCeldas[c]) is list:
                    for cc in range(len(listaCeldas[c])):
                        listaCeldas[c][cc] = mirrorCelda(cubo, listaCeldas[c][cc])
            match, posicion = matchCubo(cubo, met.vars, listaCeldas, met.posiciones)
            success = success or match
            if match or bestMatch:
                algoritmo = met.algoritmo
                algoritmo = algoritmo.replace('i', str(cubo.vars.get('i', 'i')))
                algoritmo = algoritmo.replace('j', str(cubo.vars.get('j', 'j')))
                algoritmo = algoritmo.replace('k', str(cubo.vars.get('k', 'k')))
                cubo.mover(posicion + ' >< ' + algoritmo)  # los movimientos que siguen a un '><' se ejecutan en espejo
                hizo = (posicion != '' or algoritmo != '')
                if hizo:
                    if posicion != '':
                        solucion.append(Sol(nivel + 1, 'Pos', posicion, hizo, met, True, cubo.vars))
                    if algoritmo != '':
                        solucion.append(
                            Sol(nivel + 1, 'Alg', '>< {0} ><'.format(algoritmo), hizo, met, True, cubo.vars))
                hizoAlgo = hizoAlgo or hizo
                seguir = seguir or hizo
        cant = cant + 1
        if not seguir or (
                cant >= cantVeces):  # si terminó la ejecución del metodo, veo si tiene iteraciones y recomienzo
            proxIter = True
            if met.rangoK:
                if cubo.vars.get('k') == htaK:
                    cubo.vars.set('k', ddeK)
                    proxIter = True
                else:
                    cubo.vars.set('k', cubo.vars.get('k') + 1)
                    proxIter = False
            if met.rangoJ and proxIter:
                if cubo.vars.get('j') == htaJ:
                    cubo.vars.set('j', ddeJ)
                    proxIter = True
                else:
                    cubo.vars.set('j', cubo.vars.get('j') + 1)
                    proxIter = False
            if met.rangoI and proxIter:
                if cubo.vars.get('i') == htaI:
                    cubo.vars.set('i', ddeI)
                    proxIter = True
                else:
                    cubo.vars.set('i', cubo.vars.get('i') + 1)
                    proxIter = False
            if not proxIter:
                seguir, cant = True, 0
    solucion[iSol].hizo = hizoAlgo
    return (hizoAlgo, success)


def cond2ListaCeldas(cubo, vars, listaCond):  # devuelve listaCeldas
    # listaCond es una lista de strings tipo 'cond' que puede tener sublistas con strings tipo cond
    #   las condiciones que se encuentran en la lista principal se evaluan como 'and', las condiciones que
    #   se encuentren en las sublistas se evaluan como 'or' (solo se permiten dos niveles, lista y sublista)
    # - cond es un string de la forma <cara>.<rango filas>.<rango columnas>.colores
    #     cara: id de la cara
    #     rangos de fila y columna: especificados con la sintaxis de str2movim
    #     colores: uno o varios colores segun especificacion de matchCubo (aqui no se procesan, solo se copian a la lista a devolver)
    # - listaCeldas es una lista donde cada elemento es una celda individual representada por una tupla de la forma:
    #    cara: 'FBUDLR'
    #    fila: fila (convertida al rango 0 ... self.l-1)
    #    columna: columna (convertida al rango 0 ... self.l-1)
    #    coloresPosibles: uno o varios colores separados por espacios, con que uno coincida se considera que hay coincidencia. Cada uno puede ser:
    #        - un color específico (white, yellow, red, orange, blue, green)
    #        - "->nombre" asigna el color de la celda a una variable llamada "nombre"
    #        - "==nombre" el color de la celda debe coincidir con el PREVIAMENTE ASIGNADO a la variable "nombre"
    #        - "!=nombre" el color de la celda debe ser distinto al PREVIAMENTE ASIGNADO a la variable "nombre"
    listaCeldas = []
    for cond in listaCond:
        if cond[0:2].upper() == 'OR':
            listaCeldas.append(cond2ListaCeldas(cubo, vars, palabras(cond[2:], ',')))
        else:
            if not cond:
                continue
            cara, rangoFilas, rangoColumnas, colores = palabras(cond, '.')

            rangoFilas = rangoFilas.replace('i', str(vars.get('i', 'i')))
            rangoFilas = rangoFilas.replace('j', str(vars.get('j', 'j')))
            rangoFilas = rangoFilas.replace('k', str(vars.get('k', 'k')))
            rangoColumnas = rangoColumnas.replace('i', str(vars.get('i', 'i')))
            rangoColumnas = rangoColumnas.replace('j', str(vars.get('j', 'j')))
            rangoColumnas = rangoColumnas.replace('k', str(vars.get('k', 'k')))

            rangoFilas = cubo.str2rango(rangoFilas)
            rangoColumnas = cubo.str2rango(rangoColumnas)

            for f, c in rangoFC(rangoFilas, rangoColumnas):
                listaCeldas.append((cara, f, c, colores))
    return listaCeldas


def mirrorCelda(cubo, celda):
    (cara, fila, columna, color) = celda
    if cara == 'R':
        cara = 'L'
    elif cara == 'L':
        cara = 'R'
    columna = cubo.l - 1 - columna
    return (cara, fila, columna, color)


class Metodos:
    class Metodo:
        def __init__(self, metodos, met, id):
            self.metodos = metodos
            self.met = met
            self.vars = metodos.vars

            self.id = id
            self.modo = self.met['modo'] if 'modo' in self.met else 'Once'
            self.minLado = self.met['minLado'] if 'minLado' in self.met else 3
            self.rangoI = self.met['rangoI'] if 'rangoI' in self.met else ''
            self.rangoJ = self.met['rangoJ'] if 'rangoJ' in self.met else ''
            self.rangoK = self.met['rangoK'] if 'rangoK' in self.met else ''
            self.subMetodos = self.met['subMetodos'] if 'subMetodos' in self.met else []
            self.until1st = self.met['until1st'] if 'until1st' in self.met else '-'
            self.listaCondiciones = self.met['listaCondiciones'] if 'listaCondiciones' in self.met else []
            self.mirror = self.met['mirror'] if 'mirror' in self.met else False
            self.posiciones = self.met['posiciones'] if 'posiciones' in self.met else []
            self.algoritmo = self.met['algoritmo'] if 'algoritmo' in self.met else ''
            self.comment = self.met['comment'] if 'comment' in self.met else ''
            self.important = self.met['important'] if 'important' in self.met else False

        def metodo(self, id):
            return self.metodos.metodo(id)

        def exist(self, id):
            return self.metodos.exist(id)

        def setModo(self, modo):
            self.metodos.modif = self.metodos.modif or (modo != self.modo)
            self.metodos.metDict[self.id]['modo'] = modo
            self.modo = modo

        def setMinLado(self, minLado):
            self.metodos.modif = self.metodos.modif or (minLado != self.minLado)
            self.metodos.metDict[self.id]['minLado'] = minLado
            self.minLado = minLado

        def setRangoI(self, rangoI):
            self.metodos.modif = self.metodos.modif or (rangoI != self.rangoI)
            self.metodos.metDict[self.id]['rangoI'] = rangoI
            self.rangoI = rangoI

        def setRangoJ(self, rangoJ):
            self.metodos.modif = self.metodos.modif or (rangoJ != self.rangoJ)
            self.metodos.metDict[self.id]['rangoJ'] = rangoJ
            self.rangoJ = rangoJ

        def setRangoK(self, rangoK):
            self.metodos.modif = self.metodos.modif or (rangoK != self.rangoK)
            self.metodos.metDict[self.id]['rangoK'] = rangoK
            self.rangoK = rangoK

        def setSubMetodos(self, subMetodos):
            self.metodos.modif = self.metodos.modif or (subMetodos != self.subMetodos)
            self.metodos.metDict[self.id]['subMetodos'] = subMetodos
            self.subMetodos = subMetodos

        def setUntil1st(self, until1st):
            self.metodos.modif = self.metodos.modif or (until1st != self.until1st)
            self.metodos.metDict[self.id]['until1st'] = until1st
            self.until1st = until1st

        def setListaCondiciones(self, listaCondiciones):
            self.metodos.modif = self.metodos.modif or (listaCondiciones != self.listaCondiciones)
            self.metodos.metDict[self.id]['listaCondiciones'] = listaCondiciones
            self.listaCondiciones = listaCondiciones

        def setMirror(self, mirror):
            self.metodos.modif = self.metodos.modif or (mirror != self.mirror)
            self.metodos.metDict[self.id]['mirror'] = mirror
            self.mirror = mirror

        def setPosiciones(self, posiciones):
            self.metodos.modif = self.metodos.modif or (posiciones != self.posiciones)
            self.metodos.metDict[self.id]['posiciones'] = posiciones
            self.posiciones = posiciones

        def setAlgoritmo(self, algoritmo):
            self.metodos.modif = self.metodos.modif or (algoritmo != self.algoritmo)
            self.metodos.metDict[self.id]['algoritmo'] = algoritmo
            self.algoritmo = algoritmo

        def setComment(self, comment):
            self.metodos.modif = self.metodos.modif or (comment != self.comment)
            self.metodos.metDict[self.id]['comment'] = comment
            self.comment = comment

        def setImportant(self, important):
            self.metodos.modif = self.metodos.modif or (important != self.important)
            self.metodos.metDict[self.id]['important'] = important
            self.important = important

        def incluyeA(self, idSubMetodo):  # True si idSubMetodo es submetodo (o sub-sub-metodo, etc) de este metodo.
            if self.id == idSubMetodo:
                return True
            else:
                ret = False
                for subM in self.subMetodos:
                    ret = ret or self.metodo(subM).incluyeA(idSubMetodo)
                    if ret:
                        break
                return ret

        def referidoPor(
                self):  # deuelve una lista de metodos que refieren DIRECTAMENTE a este. Si es un topLevel devuelve []
            ret = []
            for metId in self.metodos.listaMetodos():
                if self.id in self.metodo(metId).subMetodos:
                    ret.append(metId)
            return ret

    def __init__(self, archivo='metodos.json'):

        from archivoMetodos import \
            metodosHard  # mantengo un 'archivo' de metodos hardcodeado por si se borra el archivo metodos.json
        self.metodosHard = metodosHard
        self.archivo = archivo
        self.loadFromFile()
        self.vars = Vars('lg')

    def exist(self, id):
        return id in self.metDict

    def metodo(self, id):
        if self.exist(id):
            return self.Metodo(self, self.metDict[id], id)
        return False

    def topLevel(self):  # devuelve una lista de los idMetodo que NO son submetodo de ningun otro
        lista = copy.copy(self.metDict)
        for id in self.metDict:
            for subM in self.metodo(id).subMetodos:
                if subM in lista:
                    del lista[subM]
        ret = list(lista.keys())
        ret.sort()
        return ret

    def listaMetodos(self):
        ret = list(self.metDict.keys())
        ret.sort()
        return ret

    def listaMetodosYSubMetodos(self, id):
        if not self.exist(id):
            return []
        ret = [id]
        m = self.metodo(id)
        for subM in m.subMetodos:
            ret.extend(self.listaMetodosYSubMetodos(subM))
        return ret

    def new(self, id):
        if self.exist(id):
            return
        self.metDict[id] = {}
        self.metDict[id]['modo'] = 'Once'
        self.metDict[id]['minLado'] = 3
        self.metDict[id]['rangoI'] = ''
        self.metDict[id]['rangoJ'] = ''
        self.metDict[id]['rangoK'] = ''
        self.metDict[id]['subMetodos'] = []
        self.metDict[id]['until1st'] = '-'
        self.metDict[id]['listaCondiciones'] = []
        self.metDict[id]['mirror'] = False
        self.metDict[id]['posiciones'] = []
        self.metDict[id]['algoritmo'] = ''
        self.metDict[id]['comment'] = ''
        self.metDict[id]['important'] = False

    def rename(self, old, new):
        if self.exist(new) or not self.exist(old):
            return
        self.metDict[new] = self.metDict.pop(old)  # renombro el metodo
        for idMet in self.metDict:  # cambio los metodos donde se lo referencia
            m = self.metodo(idMet)
            if old in m.subMetodos:
                m.setSubMetodos([new if subM == old else subM for subM in m.subMetodos])

    def copy(self, id, txt, recursivo):
        txt = txt.strip()
        newId = txt if not recursivo else txt + ' ' + id
        if self.exist(newId) or not self.exist(id):
            return
        met = self.metodo(id)
        self.new(newId)
        newMet = self.metodo(newId)
        newMet.setModo(met.modo)
        newMet.setMinLado(met.minLado)
        newMet.setRangoI(met.rangoI)
        newMet.setRangoJ(met.rangoJ)
        newMet.setRangoK(met.rangoK)
        newMet.setSubMetodos(met.subMetodos[:])
        newMet.setUntil1st(met.until1st)
        newMet.setListaCondiciones(met.listaCondiciones[:])
        newMet.setMirror(met.mirror)
        newMet.setPosiciones(met.posiciones[:])
        newMet.setAlgoritmo(met.algoritmo)
        newMet.setComment(met.comment)
        newMet.setImportant(met.important)
        if recursivo:
            for i, subMet in enumerate(newMet.subMetodos):
                self.copy(subMet, txt, recursivo)
                newMet.subMetodos[i] = txt + ' ' + subMet

    def delete(self, id, recursivo):
        if recursivo:
            lista = self.listaMetodosYSubMetodos(id)
        else:
            lista = [id]
        for m in lista:
            if m in self.metDict:  # vuelvo a prguntar porque en 'lista' puede haber elementos repetidos
                self.metDict.pop(m)
        for m in self.metDict:
            met = self.metodo(m)
            for i, subM in enumerate(met.subMetodos):
                if subM in lista:
                    met.subMetodos.pop(i)

    def saveToFile(self):
        if self.archivo[-5:] != '.json':
            self.archivo += '.json'
        with open(self.archivo, 'w') as outfile:
            json.dump(self.metDict, outfile, sort_keys=False, indent=4)
        self.modif = False

    def loadFromFile(self):
        p = Path('.')
        files = [file.name for file in p.glob('*.json')]
        if self.archivo in files:
            with open(self.archivo) as json_file:
                self.metDict = json.load(json_file)
            self.modif = False
        else:
            self.metDict = copy.deepcopy(self.metodosHard)
            self.modif = True
        return
