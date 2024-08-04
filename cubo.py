# https://stackoverflow.com/questions/48105646/embedding-vtk-object-in-pyqt5-window
# https://vtk.org/Wiki/VTK/Examples/Python/Widgets/EmbedPyQt
# https://wiki.python.org/moin/PyQt/Tutorials

import copy
import datetime
import sys
import time
from collections import deque
from pathlib import Path
import numpy as np

# VTK
import vtk
from vtk import vtkPolyDataMapper, vtkNamedColors
from vtk import vtkRenderer, vtkActor, vtkRegularPolygonSource, vtkCubeSource
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# Qt GUI
from PyQt5 import Qt
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication

# cube
from cuboBasics import Cube
import metodos as met
from util import Clase, palabras, primerPalabra, alert, Vars
from gallery import Gallery

colores = {"F": "red", "B": "orange", "U": "white", "D": "yellow", "L": "green", "R": "blue"}


class CubeVtk(Cube):

    def __init__(self, renderer, size=3, white=False):

        super().__init__(size, white)

        self.renderer = renderer
        # atributos que definen la estetica de representacion en pantalla
        self.gap = 0
        self.innerColor = Qt.QColor('black')
        self.backgroundColor = Qt.QColor('white')
        self.camPosition = (1.0, 1.0, 2.0)
        # inicialicacion de los actores que representaran al cubo
        self.inicActores()

    def inicCoefUbicacion(self):
        self.FC2xyz = {}  # coeficientes para transformar [f,c] en [x,y,z]. [x,y,z] = [f,c,1] . FC2xyz
        self.angulo = {}  # angulos que hay que rotar la celda (en x, y, z) segun su orientacion
        self.FCCube = {}  # ajuste de coordenadas para los cubitos
        lim = self.l / 2
        dsp = lim - 0.5
        self.FC2xyz["F"] = np.array([[0, -1, 0],  # fila
                                     [1, 0, 0],  # columna
                                     [-dsp, dsp, lim]  # desplazamioento
                                     ])
        self.FCCube["F"] = np.array([-dsp, dsp, dsp])
        self.angulo["F"] = (0.0, 0.0, 45.0)  # plano XY

        self.FC2xyz["B"] = np.array([[0, -1, 0],  # fila
                                     [-1, 0, 0],  # columna
                                     [dsp, dsp, -lim]  # desplazamioento
                                     ])
        self.FCCube["B"] = np.array([dsp, dsp, -dsp])
        self.angulo["B"] = (0.0, 0.0, 45.0)  # plano XY

        self.FC2xyz["U"] = np.array([[0, 0, 1],  # fila
                                     [1, 0, 0],  # columna
                                     [-dsp, lim, -dsp]  # desplazamioento
                                     ])
        self.FCCube["U"] = np.array([-dsp, dsp, -dsp])
        self.angulo["U"] = (45.0, 90.0, 90.0)  # plano XZ

        self.FC2xyz["D"] = np.array([[0, 0, -1],  # fila
                                     [1, 0, 0],  # columna
                                     [-dsp, -lim, dsp]  # desplazamioento
                                     ])
        self.FCCube["D"] = np.array([-dsp, -dsp, dsp])
        self.angulo["D"] = (45.0, 90.0, 90.0)  # plano XZ

        self.FC2xyz["L"] = np.array([[0, -1, 0],  # fila
                                     [0, 0, 1],  # columna
                                     [-lim, dsp, -dsp]  # desplazamioento
                                     ])
        self.FCCube["L"] = np.array([-dsp, dsp, -dsp])
        self.angulo["L"] = (45.0, 90.0, 0.0)  # plano YZ

        self.FC2xyz["R"] = np.array([[0, -1, 0],  # fila
                                     [0, 0, -1],  # columna
                                     [lim, dsp, dsp]  # desplazamioento
                                     ])
        self.FCCube["R"] = np.array([dsp, dsp, dsp])
        self.angulo["R"] = (45.0, 90.0, 0.0)  # plano YZ

    def inicActores(self):  # crea e inicializa un actor y un assembly por cada celda del cubo
        # Crear el source para un cuadrado
        cuad = vtkRegularPolygonSource()
        cuad.SetNumberOfSides(4)
        cuad.SetRadius(1.0)
        # Cear el source de los cubitos
        cube = vtkCubeSource()
        cube.SetXLength(1.0)
        cube.SetYLength(1.0)
        cube.SetZLength(1.0)
        # Crear el mapper del cuadrado y los cubos y conectarlos con su source
        mappCuad = vtkPolyDataMapper()
        mappCuad.SetInputConnection(cuad.GetOutputPort())
        mappCube = vtkPolyDataMapper()
        mappCube.SetInputConnection(cube.GetOutputPort())
        self.inicCoefUbicacion()
        for cara in ('FBUDLR'):
            for f in range(self.l):
                for c in range(self.l):
                    self.c[cara][f, c].actor = vtkActor()
                    self.c[cara][f, c].actor.SetMapper(mappCuad)
                    self.c[cara][f, c].interior = vtkActor()
                    self.c[cara][f, c].interior.SetMapper(mappCube)
                    self.c[cara][f, c].ass = vtk.vtkAssembly()
                    self.c[cara][f, c].ass.AddPart(self.c[cara][f, c].actor)
                    self.c[cara][f, c].ass.AddPart(self.c[cara][f, c].interior)
                    self.c[cara][
                        f, c].otros = []  # lista de otros actores que quiera que se muevan junto con esta celda
                    self.renderer.AddActor(self.c[cara][f, c].ass)

        self.refreshStyleCeldas()
        self.refreshActores()

    def refreshActores(
            self):  # refresca la posicion de las celdas para que coincidan con la cara,fila,columna donde estan ubicadas
        mid = (self.l - 1) / 2
        for cara, f, c in [(cara, f, c) for cara in 'FBUDLR' for f in range(self.l) for c in range(self.l)]:
            self.c[cara][f, c].actor.GetProperty().SetColor(vtkNamedColors().GetColor3d(self.c[cara][f, c].color))
            self.c[cara][f, c].actor.SetOrientation(self.angulo[cara])
            self.c[cara][f, c].actor.SetPosition(np.dot([f, c, 1], self.FC2xyz[cara]))
            self.c[cara][f, c].interior.SetPosition(
                np.dot([f, c, 0], 0.98 * self.FC2xyz[cara]) + self.FCCube[cara])
            for i in range(len(self.c[cara][f, c].otros) // 2):
                (desp, act) = self.c[cara][f, c].otros[2 * i]  # symbol
                act.SetOrientation(self.angulo[cara])
                pos = np.dot([f, c, 1], self.FC2xyz[cara])  # posicion de esa celda
                pos = pos + np.dot([mid, mid, 1], self.FC2xyz[cara]) * (i + 1) * desp  # + desplazamiento
                act.SetPosition(pos)
                (despT, act) = self.c[cara][f, c].otros[2 * i + 1]  # text
                act.SetOrientation(self.angulo[cara])
                pos = np.dot([f, c, 1], self.FC2xyz[cara])  # posicion de esa celda
                pos = pos + np.dot([mid, mid, 1], self.FC2xyz[cara]) * (
                        (i + 1) * desp + despT)  # + desplazamiento
                act.SetPosition(pos)
            self.c[cara][f, c].ass.SetOrientation(0, 0, 0)
        self.renderer.GetRenderWindow().Render()

    def refreshStyleCeldas(self):  # refresca el estilo del cubo (color del interior y gap de las "calcomanias")
        escInt = 0.98
        escala = np.cos(np.pi / 4) * (1 - self.gap)
        for cara in ('FBUDLR'):
            for f in range(self.l):
                for c in range(self.l):
                    self.c[cara][f, c].actor.SetScale(escala, escala, escala)
                    self.c[cara][f, c].interior.SetScale(escInt, escInt, escInt)
                    self.c[cara][f, c].interior.GetProperty().SetColor(qColor2RGB(self.innerColor))
                    self.c[cara][f, c].interior.GetProperty().SetOpacity(self.innerColor.alphaF())
        self.renderer.GetRenderWindow().Render()

    def resetCamara(self):
        self.renderer.GetActiveCamera().SetFocalPoint(0, 0, 0)
        self.renderer.GetActiveCamera().SetPosition(0, 0, 50)
        self.renderer.GetActiveCamera().ComputeViewPlaneNormal()
        self.renderer.GetActiveCamera().SetViewUp(0, 1, 0)
        self.renderer.GetActiveCamera().OrthogonalizeViewUp()
        self.renderer.GetActiveCamera().Azimuth(self.camPosition[0])
        self.renderer.GetActiveCamera().Elevation(self.camPosition[1])
        self.renderer.ResetCamera()
        self.renderer.GetActiveCamera().Zoom(self.camPosition[2])
        self.renderer.GetRenderWindow().Render()

    def cambioTamanio(self, newTamanio):
        if self.l != newTamanio:
            super().__init__(newTamanio, self.white)
            self.renderer.RemoveAllViewProps()
            self.inicActores()
            self.resetCamara()

    def setStyle(self, gap, innerColor, backgroundColor, camPosition):
        cambiarActores = False
        if self.gap != gap:
            self.gap = gap
            cambiarActores = True
        if self.innerColor != innerColor:
            self.innerColor = innerColor
            cambiarActores = True
        if cambiarActores:
            self.refreshStyleCeldas()
        if self.camPosition != camPosition:
            self.camPosition = camPosition
            self.resetCamara()
        self.backgroundColor = backgroundColor
        self.renderer.SetBackground(qColor2RGB(self.backgroundColor))
        self.renderer.GetRenderWindow().Render()


def qColor2RGB(qc):
    return (qc.redF(), qc.greenF(), qc.blueF())


class MainWindow(Qt.QMainWindow):
    class Anim:
        def __init__(self, parent, cuboAnim, frameRate):
            self.parent = parent
            self.cuboAnim = cuboAnim
            self.frameRate = frameRate
            self.waterMark = 0  # para calcular el grado de avance
            self.inc = 0
            self.mostrarMovim = True
            self.jobs = deque()

        class Job:
            def __init__(self, movim):
                self.movim = movim
                self.listaActores = []
                self.rotar = 0
                self.vector = []
                self.avance = 0

        def callBack(self, caller, timerEvent):
            if len(self.jobs) == 0:
                return

            if not self.mostrarMovim:
                if self.jobs[0].avance > 0:
                    self.jobs.popleft()  # no hago endJob para no perder tiempo en actualizar la pantalla
                    if len(self.jobs) == 0:  # si era el ultimo trabajo, hago endAllJobs para actualizar la imagen del cubo y la progressBar
                        self.endAllJobs()
                        return

            # procesar el jobs[0]
            if self.jobs[0].avance == 0:  # inicializo el job
                if 'Actualiza' in self.jobs[0].movim:
                    self.parent.actualizaCurrentRowSoluc(int(palabras(self.jobs[0].movim, '-')[1]))
                    self.endJob()
                    return
                celdasMovidas, caraAnticlockwise = self.cuboAnim.mover(self.jobs[0].movim, self.mostrarMovim)
                if self.mostrarMovim:
                    self.jobs[0].listaActores = [
                        self.cuboAnim.c[cara][f, c].ass for (cara, f, c) in celdasMovidas]
                    l = self.cuboAnim.l
                    self.jobs[0].vector = np.dot([(l - 1) / 2, (l - 1) / 2, 1], self.cuboAnim.FC2xyz[caraAnticlockwise])
                    self.jobs[0].rotar = 90  # si el giro es multiple los actores estan multip veces => siempre 90
                else:
                    self.jobs.popleft()  # no hago endJob para no actualizar la pantalla en cada movimiento
                    self.parent.animProgressBar.setValue(self.waterMark - len(self.jobs))
                    if len(self.jobs) == 0:  # al tarminar TODOS los movimientos hago endAllobs para actualizar la imagen del cubo y la progressBar
                        self.endAllJobs()
                    return
            inc = self.inc  # grados a rotar en este ciclo.
            # TODO: calcularlo en funcion de la carga de trabajo (acelerar si hay mucho)
            inc = 1 if int(inc) < 1 else int(inc)  # ajuste luego del calculo
            inc = min(inc, self.jobs[0].rotar - self.jobs[0].avance)  # para no pasarse de la rotacion pedida!!
            for act in self.jobs[0].listaActores:
                act.RotateWXYZ(inc, self.jobs[0].vector[0], self.jobs[0].vector[1], self.jobs[0].vector[2])
            self.cuboAnim.renderer.GetRenderWindow().Render()
            self.jobs[0].avance += inc
            if self.jobs[0].avance == self.jobs[0].rotar:
                self.endJob()

        def addJobs(self, movimientos):
            espejo = ''
            for mov in palabras(movimientos, ' '):
                if mov == '><':
                    espejo = '><' if espejo == '' else ''
                    continue
                if mov == '-':
                    continue
                self.jobs.append(self.Job(espejo + mov))
            if len(self.jobs) > self.waterMark:
                self.waterMark = len(self.jobs)
                self.parent.animProgressBar.setRange(0, self.waterMark)

        def endJob(self):
            self.cuboAnim.refreshActores()
            self.jobs.popleft()
            self.parent.animProgressBar.setValue(self.waterMark - len(self.jobs))
            if len(self.jobs) == 0:  # Si este era el ultimo actualizo por ultima vez el cubo y la progressBar
                self.endAllJobs()

        def endAllJobs(self):
            self.jobs.clear()
            self.waterMark = 0
            self.parent.animProgressBar.setRange(0, 1)
            self.parent.animProgressBar.setValue(0)
            self.cuboAnim.refreshActores()

    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent)

        self.setWindowTitle("Cube NxN")
        QApplication.setStyle(Qt.QStyleFactory.create("Windows"))

        # self.left = 30
        # self.top = 50
        # self.width = 1000
        # self.height = 600

        self.presets = {}
        self.presetIter = 0

        # self.edit = False

        self.frame = Qt.QFrame()
        self.mainLayout = Qt.QGridLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

        self.renderer = vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        self.cubo = CubeVtk(self.renderer)
        self.metodos = met.Metodos()
        self.anim = self.Anim(parent=self, cuboAnim=self.cubo, frameRate=100)
        self.editTestVars = Vars('c')

        self.crearStyleWidgets()
        self.crearCuboWidgets()
        self.crearMovimWidgets()

        self.crearArbolMetodosWidgets()

        self.crearShowSolutionWidgets()
        self.crearAnimWidgets()
        self.crearEditMetodoWidgets()

        self.setStyle()  # setea la estetica del cubo segun los valores iniciales de la GUI
        self.cambioTamanio()  # setea el tamanio del cubo segun el valor inicial de la GUI
        self.renderer.ResetCamera()
        self.cubo.resetCamara()

        self.gallery = Gallery()
        self.hints = {}

        self.mainLayout.addWidget(self.vtkWidget, 0, 0, 20, 1)
        self.mainLayout.addWidget(self.cuboWidgets, 0, 1, 2, 1)
        self.mainLayout.addWidget(self.styleWidgets, 0, 2, 2, 2)
        self.mainLayout.addWidget(self.arbolMetodosWidgets, 2, 1, 15, 3)
        self.mainLayout.addWidget(self.movimWidgets, 17, 1, 1, 3)
        self.mainLayout.addWidget(self.showSolutionWidgets, 2, 1, 16, 3)
        self.mainLayout.addWidget(self.editMetodoWidgets, 0, 1, 18, 3)
        self.mainLayout.addWidget(self.animWidgets, 18, 1, 2, 3)
        self.mainLayout.columnStretch(0)

        self.showSolutionWidgets.hide()
        self.editMetodoWidgets.hide()

        self.frame.setLayout(self.mainLayout)
        self.setCentralWidget(self.frame)

        self.showMaximized()
        self.show()
        self.cubo.resetCamara()

        self.iren.Initialize()
        self.iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.iren.CreateRepeatingTimer(int(1000 / self.anim.frameRate))
        self.iren.RemoveObservers('KeyPressEvent')
        self.iren.AddObserver('KeyPressEvent', self.keyPressObserver)
        self.iren.AddObserver("TimerEvent", self.anim.callBack)
        self.iren.Start()

    def keyPressObserver(self, obj, ev):
        if obj.GetKeySym() in 'space':
            self.cubo.resetCamara()

    def crearStyleWidgets(self):
        self.styleWidgets = Qt.QGroupBox("Style")

        self.separacion = Qt.QSpinBox(self)
        self.separacion.setRange(0, 90)
        self.separacion.setSingleStep(5)
        self.separacion.setSuffix("%")
        self.separacion.setValue(20)
        self.separacion.valueChanged.connect(self.setStyle)
        separacionLabel = Qt.QLabel("&Separacion:")
        separacionLabel.setBuddy(self.separacion)

        self.camPositionAzim = Qt.QDoubleSpinBox(self)
        self.camPositionAzim.setRange(0.0, 40.0)
        self.camPositionAzim.setSingleStep(1)
        self.camPositionAzim.setDecimals(0)
        self.camPositionAzim.setSuffix("\N{degree sign}")
        self.camPositionAzim.setValue(30)
        self.camPositionAzim.setFixedWidth(55)
        self.camPositionAzim.valueChanged.connect(self.setStyle)
        self.camPositionElev = Qt.QDoubleSpinBox(self)
        self.camPositionElev.setRange(0.0, 80.0)
        self.camPositionElev.setSingleStep(1)
        self.camPositionElev.setDecimals(0)
        self.camPositionElev.setSuffix("\N{degree sign}")
        self.camPositionElev.setFixedWidth(55)
        self.camPositionElev.setValue(30)
        self.camPositionElev.valueChanged.connect(self.setStyle)
        self.camPositionZoom = Qt.QDoubleSpinBox(self)
        self.camPositionZoom.setRange(0.2, 10.0)
        self.camPositionZoom.setSingleStep(0.1)
        self.camPositionZoom.setDecimals(1)
        self.camPositionZoom.setSuffix(" X")
        self.camPositionZoom.setFixedWidth(55)
        self.camPositionZoom.setValue(1.0)
        self.camPositionZoom.valueChanged.connect(self.setStyle)
        camPositionLabel = Qt.QLabel("Pos.Cam:")
        camPositionLabel.setFixedWidth(60)
        camPositionAzimLabel = Qt.QLabel("&Azim")
        camPositionAzimLabel.setBuddy(self.camPositionAzim)
        camPositionAzimLabel.setFixedWidth(25)
        camPositionElevLabel = Qt.QLabel("&Elev")
        camPositionElevLabel.setBuddy(self.camPositionElev)
        camPositionElevLabel.setFixedWidth(25)
        camPositionZoomLabel = Qt.QLabel("&Zoom")
        camPositionZoomLabel.setBuddy(self.camPositionZoom)
        camPositionZoomLabel.setFixedWidth(25)

        self.botonResetCamara = Qt.QPushButton('Reset &Camara', self)
        self.botonResetCamara.clicked.connect(self.clickResetCamara)

        self.innerColor = Qt.QColor('black')
        self.innerColor.setAlpha(20)
        self.botonColorInt = Qt.QPushButton()
        self.botonColorInt.setStyleSheet("background-color: " + self.innerColor.name())
        self.botonColorInt.setFixedWidth(20)
        self.botonColorInt.clicked.connect(self.elegirColorInterior)
        innerColorLabel = Qt.QLabel("Color Interior:")
        innerColorLabel.setBuddy(self.botonColorInt)

        self.backgroundColor = Qt.QColor('white')
        self.botonColorFon = Qt.QPushButton()
        self.botonColorFon.setStyleSheet("background-color: " + self.backgroundColor.name())
        self.botonColorFon.setFixedWidth(20)
        self.botonColorFon.clicked.connect(self.elegirColorFondo)
        backgroundColorLabel = Qt.QLabel("Color Fondo:")
        backgroundColorLabel.setBuddy(self.botonColorFon)

        layout = Qt.QVBoxLayout()
        lay = Qt.QHBoxLayout()
        lay.addWidget(camPositionLabel)
        lay.addWidget(camPositionAzimLabel)
        lay.addWidget(self.camPositionAzim)
        lay.stretch(1)
        lay.addWidget(camPositionElevLabel)
        lay.addWidget(self.camPositionElev)
        lay.stretch(1)
        lay.addWidget(camPositionZoomLabel)
        lay.addWidget(self.camPositionZoom)
        lay.stretch(1)
        lay.addWidget(self.botonResetCamara)
        layout.addLayout(lay)
        lay = Qt.QHBoxLayout()
        lay.addWidget(backgroundColorLabel)
        lay.addWidget(self.botonColorFon)
        lay.addWidget(innerColorLabel)
        lay.addWidget(self.botonColorInt)
        lay.addWidget(separacionLabel)
        lay.addWidget(self.separacion)
        lay.addStretch(1)
        layout.addLayout(lay)
        self.styleWidgets.setLayout(layout)

    def crearAnimWidgets(self):
        self.animWidgets = Qt.QGroupBox("Animacion")

        self.dialAnimacion = Qt.QDial()
        self.dialAnimacion.setValue(30)
        self.dialAnimacion.setMinimum(1)
        self.dialAnimacion.setMaximum(90)
        self.dialAnimacion.setSingleStep(1)
        self.dialAnimacion.setNotchesVisible(True)
        self.dialAnimacion.valueChanged.connect(self.setAnimInc)

        self.showMovimCheckBox = Qt.QCheckBox("On / Off")
        self.showMovimCheckBox.setChecked(True)
        self.showMovimCheckBox.stateChanged.connect(self.setAnimInc)

        self.animProgressBar = Qt.QProgressBar()
        self.animProgressBar.setRange(0, 10000)
        self.animProgressBar.setValue(0)

        layout = Qt.QGridLayout()
        layout.addWidget(self.showMovimCheckBox, 0, 0)
        layout.addWidget(self.animProgressBar, 1, 0)
        layout.addWidget(self.dialAnimacion, 0, 1, 2, 1)
        self.animWidgets.setLayout(layout)

    def crearCuboWidgets(self):
        self.cuboWidgets = Qt.QGroupBox("Cube")

        self.tamanio = Qt.QSpinBox(self)
        self.tamanio.setRange(3, 20)
        self.tamanio.setSingleStep(1)
        self.tamanio.setValue(3)
        self.tamanio.valueChanged.connect(self.cambioTamanio)
        tamanioLabel = Qt.QLabel("&Tamaño:")
        tamanioLabel.setBuddy(self.tamanio)

        self.botonReset = Qt.QPushButton('&Reset', self)
        self.botonReset.clicked.connect(self.clickBotonReset)

        self.botonMezclar = Qt.QPushButton('&Mezclar', self)
        self.botonMezclar.clicked.connect(self.clickBotonMezclar)

        self.preset = Qt.QComboBox(self)
        self.preset.addItems([str(i + 1) + ": <Empty>" for i in range(9)])

        self.savePreset = Qt.QPushButton("&Save")
        self.savePreset.clicked.connect(self.clickSavePreset)

        self.loadPreset = Qt.QPushButton("&Load")
        self.loadPreset.clicked.connect(self.clickLoadPreset)

        layout = Qt.QGridLayout()
        layout.addWidget(tamanioLabel, 0, 0)
        layout.addWidget(self.tamanio, 0, 1)
        layout.addWidget(self.botonReset, 0, 2)
        layout.addWidget(self.botonMezclar, 0, 3)
        layout.addWidget(self.preset, 1, 0, 1, 2)
        layout.addWidget(self.savePreset, 1, 2)
        layout.addWidget(self.loadPreset, 1, 3)
        self.cuboWidgets.setLayout(layout)

    def crearMovimWidgets(self):
        self.movimWidgets = Qt.QGroupBox("Movimiento")

        self.movimientos = Qt.QLineEdit()
        self.movimientos.returnPressed.connect(self.clickHacerMovim)

        self.botonHacerMovim = Qt.QPushButton("&Mover")
        self.botonHacerMovim.clicked.connect(self.clickHacerMovim)

        layout = Qt.QHBoxLayout()
        layout.addWidget(self.movimientos)
        layout.addWidget(self.botonHacerMovim)
        self.movimWidgets.setLayout(layout)

    def crearArbolMetodosWidgets(self):
        self.arbolMetodosWidgets = Qt.QGroupBox("Metodos")

        self.arbolMetodos = Qt.QTreeWidget()
        self.arbolMetodos.setColumnCount(1)
        self.arbolMetodos.setHeaderLabel('Metodos')
        self.addItemsArbolMetodos()
        self.mezcladoPrevio = Qt.QSpinBox(self)
        self.mezcladoPrevio.setRange(0, 5000)
        self.mezcladoPrevio.setSingleStep(10)
        self.mezcladoPrevio.valueChanged.connect(self.changeMezcladoPrevio)
        self.mezcladoPrevio.setValue(0)
        mezcladoPrevioLabel = Qt.QLabel("Mezclado Previo : ")
        mezcladoPrevioLabel.setBuddy(self.mezcladoPrevio)

        self.botonEjecutarMetodo = Qt.QPushButton("&Ejecutar")
        self.botonEjecutarMetodo.clicked.connect(self.ejecutarMetodo)

        self.botonMostrarEjecucion = Qt.QPushButton("&Mostrar Ejecucion")
        self.botonMostrarEjecucion.clicked.connect(self.mostrarEjecucion)

        self.botonEditarMetodo = Qt.QPushButton("Editar Metodo")
        self.botonEditarMetodo.clicked.connect(self.editarMetodoStart)

        layout = Qt.QVBoxLayout()
        layout.addWidget(self.arbolMetodos)
        lay = Qt.QHBoxLayout()
        lay.addWidget(mezcladoPrevioLabel)
        lay.addWidget(self.mezcladoPrevio)
        lay.addWidget(self.botonEjecutarMetodo)
        lay.addWidget(self.botonMostrarEjecucion)
        lay.addStretch(1)
        lay.addWidget(self.botonEditarMetodo)
        layout.addLayout(lay)
        self.arbolMetodosWidgets.setLayout(layout)

    def addItemsArbolMetodos(self, selectMetodo=''):
        seleccionar = None
        for idMetodo in self.metodos.topLevel():
            topLevel = Qt.QTreeWidgetItem(['Met : ' + idMetodo])
            if seleccionar == None and (idMetodo == selectMetodo or selectMetodo == ''):
                seleccionar = topLevel
            self.arbolMetodos.addTopLevelItem(topLevel)
            subItemSelec = self.addSubitemsArbolMetodos(topLevel, self.metodos.metodo(idMetodo), selectMetodo)
            if seleccionar == None and subItemSelec != None:
                seleccionar = subItemSelec
        if seleccionar != None:
            self.arbolMetodos.setCurrentItem(seleccionar)

    def addSubitemsArbolMetodos(self, parent, met, selectMetodo=''):
        retSi = None
        for subM in met.subMetodos:
            si = Qt.QTreeWidgetItem(parent, ['Met : ' + subM])
            if retSi == None and (subM == selectMetodo or selectMetodo == ''):
                retSi = si
            ssi = self.addSubitemsArbolMetodos(si, met.metodo(subM), selectMetodo)
            if retSi == None and ssi != None:
                retSi = ssi
        if len(met.posiciones) > 0:
            si = Qt.QTreeWidgetItem(parent, ['Posiciones'])
            for pos in met.posiciones:
                Qt.QTreeWidgetItem(si, ['Pos : ' + pos])
        if met.algoritmo:
            Qt.QTreeWidgetItem(parent, ['Alg : ' + met.algoritmo])
        return retSi

    def crearEditMetodoWidgets(self):
        self.loading = True
        self.editMetodoWidgets = Qt.QGroupBox("Editar Metodo")

        self.editFinButton = Qt.QPushButton('Fin')
        self.editFinButton.clicked.connect(self.editarMetodoFin)
        self.editArchivoMetodos = Qt.QComboBox()
        self.editArchivoMetodos.addItems(self.archivosPuntoMet())
        self.editArchivoMetodos.setEditable(True)
        self.editArchivoMetodos.setCurrentText('metodos.json')
        self.editArchivoMetodos.lineEdit().editingFinished.connect(self.cambioNombreArch)
        self.editArchivoModificado = Qt.QLabel(' ')
        self.botonLoadArchivoMetodos = Qt.QPushButton('Load')
        self.botonLoadArchivoMetodos.clicked.connect(self.loadArchivoMetodos)
        self.botonSaveArchivoMetodos = Qt.QPushButton('Save')
        self.botonSaveArchivoMetodos.clicked.connect(self.saveArchivoMetodos)

        self.editMetodoAnterior = Qt.QPushButton('<')
        self.editMetodoAnterior.setMaximumWidth(20)
        self.editMetodoAnterior.clicked.connect(self.editMetodoAnteriorClicked)
        self.editMetodoSuperior = Qt.QPushButton('^')
        self.editMetodoSuperior.setMaximumWidth(20)
        self.editMetodoSuperior.clicked.connect(self.editMetodoSuperiorClicked)
        self.editMetodoCDRecursivo = Qt.QCheckBox()
        self.editMetodoCDRecursivo.setChecked(False)
        self.editMetodoCopy = Qt.QPushButton('Copy')
        self.editMetodoCopy.setMaximumWidth(40)
        self.editMetodoCopy.clicked.connect(self.editMetodoCopiar)
        self.editMetodoDelete = Qt.QPushButton('Del')
        self.editMetodoDelete.setMaximumWidth(40)
        self.editMetodoDelete.clicked.connect(self.editMetodoBorrar)

        self.editMetodoId = Qt.QComboBox()
        self.editMetodoId.addItems(['<New>'] + self.metodos.listaMetodos())
        self.editMetodoId.setEditable(True)
        self.editMetodoId.activated.connect(self.editMetodoIdChange)
        self.editMetodoId.lineEdit().editingFinished.connect(self.editMetodoIdChange)

        self.editTimes = Qt.QSpinBox(self)
        self.editTimes.setRange(0, 5000)
        self.editTimes.setSingleStep(1)
        self.editTimes.valueChanged.connect(lambda: self.changeEditModo('times'))
        self.editModo = Qt.QComboBox()
        self.editModo.addItems(['Once', 'Twice', 'Repeat', 'Best Match', 'times'])
        self.editModo.currentTextChanged.connect(lambda: self.changeEditModo('modo'))
        self.editRangoI = Qt.QLineEdit()
        self.editRangoI.editingFinished.connect(
            lambda: self.simpleValueChanged(self.metodoEditando.setRangoI, self.editRangoI.text()))
        self.editRangoI.setMaximumWidth(70)
        self.editRangoJ = Qt.QLineEdit()
        self.editRangoJ.editingFinished.connect(
            lambda: self.simpleValueChanged(self.metodoEditando.setRangoJ, self.editRangoJ.text()))
        self.editRangoJ.setMaximumWidth(70)
        self.editRangoK = Qt.QLineEdit()
        self.editRangoK.editingFinished.connect(
            lambda: self.simpleValueChanged(self.metodoEditando.setRangoK, self.editRangoK.text()))
        self.editRangoK.setMaximumWidth(70)
        self.editMinLado = Qt.QSpinBox(self)
        self.editMinLado.setRange(3, 20)
        self.editMinLado.setSingleStep(1)
        self.editMinLado.valueChanged.connect(
            lambda: self.simpleValueChanged(self.metodoEditando.setMinLado, self.editMinLado.value()))
        self.editComment = Qt.QTextEdit()
        self.editComment.textChanged.connect(
            lambda: self.simpleValueChanged(self.metodoEditando.setComment, self.editComment.toPlainText()))
        self.editComment.setMaximumHeight(45)
        self.editImportant = Qt.QCheckBox()
        self.editImportant.stateChanged.connect(
            lambda: self.simpleValueChanged(self.metodoEditando.setImportant, self.editImportant.isChecked()))
        self.editUntil1st = Qt.QComboBox()
        self.editUntil1st.addItems(['-', 'Success', 'Failure'])
        self.editUntil1st.currentTextChanged.connect(self.changeEditUntil1st)
        self.editSubMetodos = Qt.QTableWidget()
        self.editSubMetodos.setColumnCount(4)
        self.editSubMetodos.verticalHeader().hide()
        self.editSubMetodos.horizontalHeader().hide()
        self.editSubMetodos.setColumnWidth(0, 500)
        self.editSubMetodos.setColumnWidth(1, 40)
        self.editSubMetodos.setColumnWidth(2, 40)
        self.editSubMetodos.setColumnWidth(3, 40)
        self.editCondiciones = Qt.QTableWidget()
        self.editCondiciones.setColumnCount(4)
        self.editCondiciones.verticalHeader().hide()
        self.editCondiciones.horizontalHeader().hide()
        self.editCondiciones.cellChanged.connect(
            lambda: self.changeGenericList(self.editCondiciones, self.metodoEditando.listaCondiciones, 'cond'))
        self.editCondiciones.setColumnWidth(0, 160)
        self.editCondiciones.setColumnWidth(1, 160)
        self.editCondiciones.setColumnWidth(2, 160)
        self.editCondiciones.setColumnWidth(3, 160)
        self.editPosiciones = Qt.QTableWidget()
        self.editPosiciones.setColumnCount(4)
        self.editPosiciones.verticalHeader().hide()
        self.editPosiciones.horizontalHeader().hide()
        self.editPosiciones.cellChanged.connect(
            lambda: self.changeGenericList(self.editPosiciones, self.metodoEditando.posiciones, 'posic'))
        self.editPosiciones.currentCellChanged.connect(self.editRefreshHints)
        self.editPosiciones.setColumnWidth(0, 100)
        self.editPosiciones.setColumnWidth(1, 100)
        self.editPosiciones.setColumnWidth(2, 100)
        self.editPosiciones.setColumnWidth(3, 100)
        self.editMirror = Qt.QCheckBox('Mirror')
        self.editMirror.stateChanged.connect(self.changeEditMirror)
        self.editAlgoritmo = Qt.QLineEdit()
        self.editAlgoritmo.editingFinished.connect(
            lambda: self.simpleValueChanged(self.metodoEditando.setAlgoritmo, self.editAlgoritmo.text()))

        editPosicAll = ["-", "", "", "",
                        "X", "X'", "", "",
                        "Y", "Y'", "", "",
                        "Z", "Z'", "", "",
                        "Y2", "X2", "Z2", "",
                        "X Y", "X Y'", "X Y2", "",
                        "Z Y", "Z Y'", "Z Y2", "",
                        "X' Y", "X' Y'", "X' Y2", "",
                        "Z' Y", "Z' Y'", "Z' Y2", "",
                        "X2 Y", "X2 Y'"
                        ]  # 24 posiciones posibles para buscar (c/u obtenida con la menor cantidad de movimiento posible)
        editPosicAllX = ["-", "X", "X'", "X2"]
        editPosicAllY = ["-", "Y", "Y'", "Y2"]
        editPosicAllZ = ["-", "Z", "Z'", "Z2"]
        self.editPosicCopiadas = []
        self.editPosicAllButton = Qt.QPushButton('Insert All')
        self.editPosicAllButton.setMaximumWidth(120)
        self.editPosicAllButton.clicked.connect(lambda x: self.editInsertPosic(editPosicAll))
        self.editPosicAllXButton = Qt.QPushButton('Insert All X')
        self.editPosicAllXButton.setMaximumWidth(120)
        self.editPosicAllXButton.clicked.connect(lambda x: self.editInsertPosic(editPosicAllX))
        self.editPosicAllYButton = Qt.QPushButton('Insert All Y')
        self.editPosicAllYButton.setMaximumWidth(120)
        self.editPosicAllYButton.clicked.connect(lambda x: self.editInsertPosic(editPosicAllY))
        self.editPosicAllZButton = Qt.QPushButton('Insert All Z')
        self.editPosicAllZButton.setMaximumWidth(120)
        self.editPosicAllZButton.clicked.connect(lambda x: self.editInsertPosic(editPosicAllZ))
        self.editPosicCopyButton = Qt.QPushButton('Copy All')
        self.editPosicCopyButton.setMaximumWidth(120)
        self.editPosicCopyButton.clicked.connect(self.editCopyPosic)
        self.editPosicPasteButton = Qt.QPushButton('Insert copied')
        self.editPosicPasteButton.setMaximumWidth(120)
        self.editPosicPasteButton.clicked.connect(lambda x: self.editInsertPosic(self.editPosicCopiadas))
        self.editDeleteAllButton = Qt.QPushButton('Delete All')
        self.editDeleteAllButton.setMaximumWidth(120)
        self.editDeleteAllButton.clicked.connect(self.editDeleteAllPosics)

        self.editTestTamanio = Qt.QSpinBox(self)
        self.editTestTamanio.setRange(3, 20)
        self.editTestTamanio.setSingleStep(1)
        self.editTestTamanio.valueChanged.connect(self.changeTestTamanio)
        self.editTestPosicion = Qt.QPushButton('Posicion')
        self.editTestPosicion.setMaximumWidth(60)
        self.editTestPosicion.setDisabled(True)
        self.editTestPosicion.clicked.connect(lambda x: self.editTestMovim('pos'))
        self.editTestAlgoritmo = Qt.QPushButton('Algoritmo')
        self.editTestAlgoritmo.setMaximumWidth(60)
        self.editTestAlgoritmo.setDisabled(True)
        self.editTestAlgoritmo.clicked.connect(lambda x: self.editTestMovim('alg'))
        self.editTestMirror = Qt.QCheckBox()
        self.editTestMirror.setChecked(False)
        self.editTestMirror.stateChanged.connect(self.editRefreshHints)
        self.editTestI = Qt.QSpinBox(self)
        self.editTestI.setRange(0, 20)
        self.editTestI.setSingleStep(1)
        self.editTestI.setValue(0)
        self.editTestI.valueChanged.connect(self.editRefreshHints)
        self.editTestJ = Qt.QSpinBox(self)
        self.editTestJ.setRange(0, 20)
        self.editTestJ.setSingleStep(1)
        self.editTestJ.setValue(0)
        self.editTestJ.valueChanged.connect(self.editRefreshHints)
        self.editTestK = Qt.QSpinBox(self)
        self.editTestK.setRange(0, 20)
        self.editTestK.setSingleStep(1)
        self.editTestK.setValue(0)
        self.editTestK.valueChanged.connect(self.editRefreshHints)

        layout = Qt.QVBoxLayout()
        lay = Qt.QHBoxLayout()
        lay.addWidget(self.editMetodoAnterior)
        lay.addWidget(self.editMetodoSuperior)
        lay.addWidget(Qt.QLabel("Recursivo:"))
        lay.addWidget(self.editMetodoCDRecursivo)
        lay.addWidget(self.editMetodoCopy)
        lay.addWidget(self.editMetodoDelete)
        lay.addWidget(self.editMetodoId)
        lay.addStretch(1)
        lay.addWidget(Qt.QLabel("Min.Lado:"))
        lay.addWidget(self.editMinLado)
        lay.addWidget(Qt.QLabel("Important:"))
        lay.addWidget(self.editImportant)
        layout.addLayout(lay)
        layout.addWidget(self.editComment)
        lay = Qt.QHBoxLayout()
        lay.addWidget(Qt.QLabel("Modo:"))
        lay.addWidget(self.editTimes)
        lay.addWidget(self.editModo)
        lay.addStretch(5)
        lay.addWidget(Qt.QLabel("Iteraciones"))
        lay.addStretch(1)
        lay.addWidget(Qt.QLabel("i"))
        lay.addWidget(self.editRangoI)
        lay.addStretch(1)
        lay.addWidget(Qt.QLabel("j"))
        lay.addWidget(self.editRangoJ)
        lay.addStretch(1)
        lay.addWidget(Qt.QLabel("k"))
        lay.addWidget(self.editRangoK)
        layout.addLayout(lay)
        self.editMetodoTabs = Qt.QTabWidget()
        tab1 = Qt.QWidget()
        layT1 = Qt.QVBoxLayout()
        lay = Qt.QHBoxLayout()
        lay.addWidget(Qt.QLabel("Until 1st:"))
        lay.addWidget(self.editUntil1st)
        lay.addStretch(1)
        layT1.addLayout(lay)
        layT1.addWidget(self.editSubMetodos)
        tab1.setLayout(layT1)
        self.editMetodoTabs.addTab(tab1, 'SubMetodos')
        tab2 = Qt.QWidget()
        layT2 = Qt.QGridLayout()
        layT2.addWidget(self.editCondiciones, 0, 0, 4, 5)
        layT2.addWidget(self.editPosiciones, 4, 0, 8, 4)
        lay = Qt.QVBoxLayout()
        lay.addWidget(self.editPosicAllButton)
        lay.addSpacing(15)
        lay.addWidget(self.editPosicAllXButton)
        lay.addWidget(self.editPosicAllYButton)
        lay.addWidget(self.editPosicAllZButton)
        lay.addSpacing(15)
        lay.addWidget(self.editPosicCopyButton)
        lay.addWidget(self.editPosicPasteButton)
        lay.addWidget(self.editDeleteAllButton)
        layT2.addLayout(lay, 4, 4, 8, 1)
        lay = Qt.QHBoxLayout()
        lay.addWidget(self.editMirror)
        lay.addStretch(1)
        lay.addWidget(Qt.QLabel("Algoritmo:"))
        lay.addWidget(self.editAlgoritmo)
        layT2.addLayout(lay, 12, 0, 1, 5)
        lay = Qt.QHBoxLayout()
        lay.addStretch(1)
        lay.addWidget(Qt.QLabel("Test:   "))
        lay.addWidget(Qt.QLabel("Tamaño"))
        lay.addWidget(self.editTestTamanio)
        lay.addWidget(Qt.QLabel("Mirror"))
        lay.addWidget(self.editTestMirror)
        lay.addWidget(Qt.QLabel("i"))
        lay.addWidget(self.editTestI)
        lay.addWidget(Qt.QLabel("j"))
        lay.addWidget(self.editTestJ)
        lay.addWidget(Qt.QLabel("k"))
        lay.addWidget(self.editTestK)
        lay.addWidget(self.editTestPosicion)
        lay.addWidget(self.editTestAlgoritmo)
        layT2.addLayout(lay, 13, 0, 1, 5)
        tab2.setLayout(layT2)
        self.editMetodoTabs.addTab(tab2, 'Condiciones / Posiciones / Algoritmo')
        layout.addWidget(self.editMetodoTabs)
        lay = Qt.QHBoxLayout()
        lay.addStretch(1)
        lay.addWidget(self.editArchivoMetodos)
        lay.addWidget(self.editArchivoModificado)
        lay.addWidget(Qt.QLabel('  '))
        lay.addWidget(self.botonLoadArchivoMetodos)
        lay.addWidget(self.botonSaveArchivoMetodos)
        lay.addWidget(self.editFinButton)
        layout.addLayout(lay)
        self.editMetodoWidgets.setLayout(layout)

    def editMetodoCopiar(self):
        recursivo = self.editMetodoCDRecursivo.isChecked()
        if recursivo:
            msg = "Prefijo a agregar a todos los metodos y submetodos:"
        else:
            msg = "Nombre del nuevo metodo:" + ' ' * 40
        text, ok = Qt.QInputDialog().getText(self, "Copiar metodo(s)", msg)
        self.editMetodoCDRecursivo.setChecked(False)
        text = text.strip()
        if not ok or not text:
            return
        if not recursivo and self.metodos.exist(text):
            alert('Metodo existente')
            return
        id = self.metodoEditando.id
        self.metodos.copy(id, text, recursivo)
        self.metodos.modif = True
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')
        id = text if not recursivo else text + ' ' + id
        self.editMetodoId.clear()
        self.editMetodoId.addItems(['<New>'] + self.metodos.listaMetodos())
        self.editMetodoId.setCurrentText(id)
        self.editLoadMetodo(id)

    def editMetodoBorrar(self):
        recursivo = self.editMetodoCDRecursivo.isChecked()
        id = self.metodoEditando.id
        if recursivo:
            msg = "Se borrará el metodo \n"
            msg = msg + " " * 4 + id + "\n"
            msg = msg + "mas todos los submetodos, sub submetodos, \n"
            msg = msg + "y todas sus referencias."
        else:
            msg = "Se borrará el metodo \n"
            msg = msg + " " * 4 + id + "\n"
            msg = msg + "y todas sus referencias."
        self.editMetodoCDRecursivo.setChecked(False)
        buttonReply = Qt.QMessageBox.question(self, 'Cube', msg, Qt.QMessageBox.Yes | Qt.QMessageBox.No,
                                              Qt.QMessageBox.No)
        if buttonReply == Qt.QMessageBox.No:
            return
        self.metodos.delete(id, recursivo)
        for i, m in enumerate(self.listaEditados):
            if not self.metodos.exist(m):
                self.listaEditados.pop(i)
        if len(self.listaEditados) > 0:
            id = self.listaEditados.pop()
        else:
            if len(self.metodos.topLevel()) > 0:
                id = self.metodos.topLevel()[0]
            else:
                id = 'New Method'
                self.metodos.new(id)
        self.metodos.modif = True
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')
        self.editMetodoId.clear()
        self.editMetodoId.addItems(['<New>'] + self.metodos.listaMetodos())
        self.editMetodoId.setCurrentText(id)
        self.editLoadMetodo(id)

    def editMetodoAnteriorClicked(self):
        if len(self.listaEditados) <= 1:
            return
        id = self.listaEditados.pop()
        id = self.listaEditados.pop()
        self.editMetodoId.setCurrentText(id)
        self.editLoadMetodo(id)

    def editMetodoSuperiorClicked(self):
        sup = self.metodoEditando.referidoPor()
        if len(sup) == 0:  # si es un topLevel, no puedo subir mas...
            return
        # si venía navegando desde algun superior de este metodo: voy a ese superior en particular (y no lo agrego a la pila de editados)
        if len(self.listaEditados) >= 2:
            if self.listaEditados[-2] in sup:
                self.editMetodoAnteriorClicked()
                return
        # si no: voy al 1ro de la lista (sup[0])
        self.editMetodoId.setCurrentText(sup[0])
        self.editLoadMetodo(sup[0])

    def editCopyPosic(self):
        self.editPosicCopiadas = copy.copy(self.metodoEditando.posiciones)

    def editInsertPosic(self, posics):
        if len(posics) == 0:
            return
        colCount = self.editPosiciones.columnCount()
        row = self.editPosiciones.currentRow()
        col = self.editPosiciones.currentColumn()
        if row < 0 or col < 0:
            i = len(self.metodoEditando.posiciones)  # inserto al final
        else:
            i = row * colCount + col
        while i > len(self.metodoEditando.posiciones):
            self.metodoEditando.posiciones.append('')
        for pos in posics:
            self.metodoEditando.posiciones.insert(i, pos)
            i += 1
        self.editPosiciones.clearContents()
        self.editPosiciones.setRowCount((len(self.metodoEditando.posiciones) - 1) // 4 + 2)
        for i, pos in enumerate(self.metodoEditando.posiciones):
            self.editPosiciones.setItem(i // 4, i % 4, Qt.QTableWidgetItem(pos))
            self.editPosiciones.resizeRowToContents(i // 4)
        self.editPosiciones.resizeRowToContents(self.editPosiciones.rowCount() - 1)
        self.editPosiciones.setCurrentCell(row, col)
        self.metodos.modif = True
        self.editArchivoModificado.setText('*')

    def editDeleteAllPosics(self):
        self.metodoEditando.setPosiciones([])
        self.editPosiciones.clearContents()
        self.editPosiciones.setRowCount(1)
        self.editPosiciones.setCurrentCell(0, 0)
        self.metodos.modif = True
        self.editArchivoModificado.setText('*')

    def changeEditMirror(self):
        self.metodoEditando.setMirror(self.editMirror.isChecked())
        self.editArchivoModificado.setText('*')
        self.metodoEditando.movim = True
        self.editTestMirror.setDisabled(not self.metodoEditando.mirror)
        self.editTestMirror.setChecked(False)

    def changeTestTamanio(self):
        self.metodoEditCubo.cambioTamanio(self.editTestTamanio.value())
        self.editRefreshHints()

    def editTestMovim(self, tipo):
        row = self.editPosiciones.currentRow()
        col = self.editPosiciones.currentColumn()
        if self.editPosiciones.currentItem() is None:
            return
        colCount = self.editPosiciones.columnCount()
        i = row * colCount + col
        if i >= len(self.metodoEditando.posiciones):
            return
        if not self.metodoEditando.posiciones[i]:
            return
        pos = self.metodoEditando.posiciones[i]
        alg = ('>< ' if self.editTestMirror.isChecked() else '') + self.metodoEditando.algoritmo
        alg = alg.replace('i', str(self.editTestI.value()))
        alg = alg.replace('j', str(self.editTestJ.value()))
        alg = alg.replace('k', str(self.editTestK.value()))
        if tipo == 'pos':
            self.anim.addJobs(pos)
            self.editTestPosicion.setDisabled(True)
            self.editTestAlgoritmo.setDisabled(False)
        elif tipo == 'alg':
            self.anim.addJobs(alg)
            self.editTestAlgoritmo.setDisabled(True)

    def editRefreshHints(self):
        self.clearHints(self.metodoEditCubo)
        row = self.editPosiciones.currentRow()
        col = self.editPosiciones.currentColumn()
        if self.editPosiciones.currentItem() is None:
            return
        colCount = self.editPosiciones.columnCount()
        i = row * colCount + col
        if i >= len(self.metodoEditando.posiciones):
            return
        if not self.metodoEditando.posiciones[i]:
            return
        pos = self.metodoEditando.posiciones[i]
        mirror = self.editTestMirror.isChecked()
        self.editTestVars.set('i', self.editTestI.value())
        self.editTestVars.set('j', self.editTestJ.value())
        self.editTestVars.set('k', self.editTestK.value())
        self.showHints(self.metodoEditCubo, self.metodoEditando, self.editTestVars, pos, mirror, mostrarTextoCond=True)
        self.editTestAlgoritmo.setDisabled(pos != '-')
        self.editTestPosicion.setDisabled(pos == '-')

    def simpleValueChanged(self, setMethod, value):
        setMethod(value)
        self.editArchivoModificado.setText('*')
        self.metodos.modif = True

    def archivosPuntoMet(self):
        p = Path('.')
        ret = [file.name for file in p.glob('*.json')]
        if 'metodos.json' not in ret:
            ret.append('metodos.json')
        return ret

    def cambioNombreArch(self):
        if not self.editArchivoMetodos.currentText():
            return
        if self.metodos.archivo != self.editArchivoMetodos.currentText():
            self.metodos.archivo = self.editArchivoMetodos.currentText()
            self.metodos.modif = True
            self.editArchivoModificado.setText('*')

    def loadArchivoMetodos(self):
        id = self.metodoEditando.id
        buttonReply = Qt.QMessageBox.Yes
        if self.metodos.modif:
            buttonReply = Qt.QMessageBox.question(self, 'Cube', "Discard changes?",
                                                  Qt.QMessageBox.Yes | Qt.QMessageBox.No, Qt.QMessageBox.No)
        if buttonReply == Qt.QMessageBox.No:
            return
        self.metodos.loadFromFile()
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')
        if not self.metodos.exist(id):
            id = self.metodos.topLevel()[0]
        self.editMetodoId.clear()
        self.editMetodoId.addItems(['<New>'] + self.metodos.listaMetodos())
        self.editMetodoId.setCurrentText(id)
        self.listaEditados = []
        self.editLoadMetodo(id)

    def saveArchivoMetodos(self):
        if self.metodoEditando.id == '<New>':
            if len(self.listaEditados) > 1:
                id = self.listaEditados.pop()
                id = self.listaEditados.pop()
            else:
                id = self.metodos.topLevel()[0]
            self.editMetodoId.clear()
            self.editMetodoId.addItems(['<New>'] + self.metodos.listaMetodos())
            self.editMetodoId.setCurrentText(id)
            self.editLoadMetodo(id)
        self.metodos.saveToFile()
        self.editArchivoMetodos.clear()
        self.editArchivoMetodos.addItems(self.archivosPuntoMet())
        self.editArchivoMetodos.setCurrentText(self.metodos.archivo)
        self.editArchivoModificado.setText(' ')
        self.metodos.modif = False

    def textCell(self, tab, r, c):
        it = tab.item(r, c)
        return '' if it is None else it.text()

    def changeGenericList(self, tabWidget, lista, tipo):
        row = tabWidget.currentRow()
        col = tabWidget.currentColumn()
        if tabWidget.currentItem() is None:
            return
        text = tabWidget.currentItem().text()
        colCount = tabWidget.columnCount()
        i = row * colCount + col
        while i >= len(lista):
            lista.append('')
        if lista[i] != text:
            lista[i] = text
            self.metodos.modif = True
            self.editArchivoModificado.setText('*')
        rowText = ''
        for c in range(colCount):
            rowText = rowText + self.textCell(tabWidget, row, c)
        if row == tabWidget.rowCount() - 1 and rowText != '':
            tabWidget.setRowCount(tabWidget.rowCount() + 1)
            tabWidget.resizeRowToContents(tabWidget.rowCount() - 1)
        elif row < tabWidget.rowCount() - 1 and rowText == '':
            tabWidget.removeRow(row)
            for _ in range(colCount):
                if row * colCount < len(lista):
                    lista.pop(row * colCount)

    @pyqtSlot()
    def editMetodoIdChange(self):
        new = self.editMetodoId.currentText()
        old = self.metodoEditando.id
        if new == '':
            self.editMetodoId.setCurrentText(self.metodoEditando.id)
            return
        if new == old:
            return
        if new == '<New>':
            self.metodos.new(new)
            self.listaEditados.pop()
            self.metodos.modif = True
        elif not self.metodos.exist(new):
            self.metodos.rename(old, new)
            self.listaEditados = [new if mm == old else mm for mm in
                                  self.listaEditados]  # renombro tambien en listaEditados
            self.listaEditados.pop()
            self.metodos.modif = True
            self.editMetodoId.clear()
            self.editMetodoId.addItems(['<New>'] + self.metodos.listaMetodos())
            self.editMetodoId.setCurrentText(new)
        self.editLoadMetodo(new)
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')

    def editLoadMetodo(self, id):
        self.loading = True
        if id != '<New>':  # si me muevo del metodo nuevo antes de darle un nombre ditinto de <New>, borro ese registro temporal, asumo que no quiero agregar un metodo nuevo
            self.metodos.delete('<New>', recursivo=False)
            for i, m in enumerate(self.listaEditados):
                if not self.metodos.exist(m):
                    self.listaEditados.pop(i)
        self.listaEditados.append(id)
        modif = self.metodos.modif  # guardo el estado de metodos.modif para restituirlo al finalizar
        self.metodoEditando = self.metodos.metodo(id)

        if 'times' in self.metodoEditando.modo:
            self.editModo.setCurrentText('times')
            self.editTimes.setValue(int(primerPalabra(self.metodoEditando.modo)[0]))
        else:
            self.editModo.setCurrentText(self.metodoEditando.modo)
            self.changeEditModo('modo')
        self.editMinLado.setValue(self.metodoEditando.minLado)
        if self.editTestTamanio.value() < self.metodoEditando.minLado:
            self.editTestTamanio.setValue(self.metodoEditando.minLado)
        self.editRangoI.setText(self.metodoEditando.rangoI)
        self.editRangoJ.setText(self.metodoEditando.rangoJ)
        self.editRangoK.setText(self.metodoEditando.rangoK)
        self.editComment.setText(self.metodoEditando.comment)
        self.editImportant.setChecked(self.metodoEditando.important)
        self.editUntil1st.setCurrentText(self.metodoEditando.until1st)

        self.editSubMetodos.clearContents()  # Me volvio loco un error que solo pasaba presionando a repeticion rapida el boton de follow, solo lo solucione con esto...
        self.editSubMetodos.setRowCount(0)
        for subM in self.metodoEditando.subMetodos:
            self.editSubMetodoInsertWidgetsRow(self.metodos.listaMetodos(), subM, -1)
        self.editSubMetodoInsertWidgetsRow(['<New SubMetodo>'] + self.metodos.listaMetodos(), '<New SubMetodo>', -1)
        self.editCondiciones.clearContents()
        self.editCondiciones.setRowCount((len(self.metodoEditando.listaCondiciones) - 1) // 4 + 2)
        for i, cond in enumerate(self.metodoEditando.listaCondiciones):
            self.editCondiciones.setItem(i // 4, i % 4, Qt.QTableWidgetItem(cond))
            self.editCondiciones.resizeRowToContents(i // 4)
        self.editCondiciones.resizeRowToContents(self.editCondiciones.rowCount() - 1)
        self.editPosiciones.clearContents()
        self.editPosiciones.setRowCount((len(self.metodoEditando.posiciones) - 1) // 4 + 2)
        for i, pos in enumerate(self.metodoEditando.posiciones):
            self.editPosiciones.setItem(i // 4, i % 4, Qt.QTableWidgetItem(pos))
            self.editPosiciones.resizeRowToContents(i // 4)
        self.editPosiciones.resizeRowToContents(self.editPosiciones.rowCount() - 1)
        self.editPosiciones.setCurrentCell(0, 0)
        self.editMirror.setChecked(self.metodoEditando.mirror)
        self.editTestMirror.setDisabled(not self.metodoEditando.mirror)
        self.editTestMirror.setChecked(False)
        self.editAlgoritmo.setText(self.metodoEditando.algoritmo)
        self.editAlgoritmo.setMinimumWidth(500)
        if len(self.metodoEditando.listaCondiciones) > 0:
            self.editMetodoTabs.setCurrentIndex(1)
        else:
            self.editMetodoTabs.setCurrentIndex(0)
        self.metodos.modif = modif  # restituyo el estado de metodos.modif
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')
        self.loading = False

    def editSubMetodoInsertWidgetsRow(self, lista, item, rowNum):
        if rowNum == -1:
            rowNum = self.editSubMetodos.rowCount()
        cBox = Qt.QComboBox()
        cBox.addItems(lista)
        cBox.setCurrentText(item)
        cBox.setEditable(True)
        cBox.lineEdit().editingFinished.connect(self.editChangeSubMetodo)
        cBox.activated.connect(self.editChangeSubMetodo)
        bIns = Qt.QPushButton('+')
        bIns.setMaximumWidth(40)
        bIns.clicked.connect(self.editSubMetodoInsertRow)
        bDel = Qt.QPushButton('-')
        bDel.setMaximumWidth(40)
        bDel.clicked.connect(self.editSubMetodoDeleteRow)
        bEdit = Qt.QPushButton('>')  # ...
        bEdit.setMaximumWidth(40)
        bEdit.clicked.connect(self.editSubMetodoFollow)
        self.editSubMetodos.insertRow(rowNum)
        self.editSubMetodos.setCellWidget(rowNum, 0, cBox)
        self.editSubMetodos.setCellWidget(rowNum, 1, bIns)
        self.editSubMetodos.setCellWidget(rowNum, 2, bDel)
        self.editSubMetodos.setCellWidget(rowNum, 3, bEdit)
        self.editSubMetodos.resizeRowToContents(rowNum)

    @pyqtSlot()
    def editSubMetodoFollow(self):
        row = self.editSubMetodos.indexAt(self.sender().pos()).row()
        text = self.editSubMetodos.cellWidget(row, 0).currentText()
        if row == len(self.metodoEditando.subMetodos):
            return
        self.editMetodoId.setCurrentText(text)
        self.editLoadMetodo(text)
        return

    @pyqtSlot()
    def editChangeSubMetodo(self):
        id = self.metodoEditando.id
        if 'QLineEdit' in str(type(self.sender())):
            row = self.editSubMetodos.indexAt(self.sender().parent().pos()).row()
            new = self.sender().text()
        else:  # es QComboBox
            row = self.editSubMetodos.indexAt(self.sender().pos()).row()
            new = self.sender().currentText()
        old = '' if row >= len(self.metodoEditando.subMetodos) else self.metodoEditando.subMetodos[row]
        if new == '':
            self.editLoadMetodo(id)
            return
        if old == new or new == '<New SubMetodo>':
            return
        if self.metodos.exist(new):  # Cambio un subMetodo por otro (o agrego, si estaba en la ultima fila)
            if self.metodos.metodo(new).incluyeA(id):  # si hay referencia circular, repongo el texto original
                alert('Referencia circular, un metodo no puede ser submetodo de si mismo')
                if row < len(self.metodoEditando.subMetodos):
                    self.editSubMetodos.cellWidget(row, 0).setCurrentText(old)
                else:
                    self.editSubMetodos.cellWidget(row, 0).setCurrentText('<New SubMetodo>')
            else:  # cambio o agrego el submetodo
                if row < len(self.metodoEditando.subMetodos):
                    self.metodoEditando.subMetodos[row] = new
                else:
                    self.metodoEditando.subMetodos.append(new)
                    self.editSubMetodoInsertWidgetsRow(['<New SubMetodo>'] + self.metodos.listaMetodos(),
                                                       '<New SubMetodo>', -1)
                self.metodos.modif = True
                self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')
        else:  # renombro ese submetodo y todas sus referencias
            if row < len(
                    self.metodoEditando.subMetodos):  # renombrar el submetodo apuntado por 'row' para que ahora se llame 'new'
                self.metodos.rename(old, new)
                self.listaEditados = [new if mm == old else mm for mm in
                                      self.listaEditados]  # renombro tambien en listaEditados
            else:  # si es la ultima fila, agregar un metodo nuevo vacio
                self.metodos.new(new)
                self.metodoEditando.subMetodos.append(new)
                self.editSubMetodoInsertWidgetsRow(['<New SubMetodo>'] + self.metodos.listaMetodos(), '<New SubMetodo>',
                                                   -1)
            self.editMetodoId.clear()
            self.editMetodoId.addItems(['<New>'] + self.metodos.listaMetodos())
            self.editMetodoId.setCurrentText(id)
            self.listaEditados.pop()
            self.editLoadMetodo(id)
            self.metodos.modif = True
            self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')

    @pyqtSlot()
    def editSubMetodoInsertRow(self):
        row = self.editSubMetodos.indexAt(self.sender().pos()).row()
        if row == self.editSubMetodos.rowCount() - 1:  # no insertar en la ultima fila
            return
        text = self.editSubMetodos.cellWidget(row, 0).currentText()
        self.editSubMetodoInsertWidgetsRow(self.metodos.listaMetodos(), text, row)
        self.metodoEditando.subMetodos.insert(row, text)
        self.metodos.modif = True
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')

    @pyqtSlot()
    def editSubMetodoDeleteRow(self):
        row = self.editSubMetodos.indexAt(self.sender().pos()).row()
        if row == self.editSubMetodos.rowCount() - 1:  # no eliminar la ultima fila (la que es para agregar al final)
            return
        self.editSubMetodos.removeRow(row)
        self.metodoEditando.subMetodos.pop(row)
        self.metodos.modif = True
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')

    def editarMetodoStart(self):
        texto = self.arbolMetodos.currentItem().text(0)
        if texto[0:6] != 'Met : ':
            return
        self.renderer.RemoveAllViewProps()
        self.metodoEditCubo = CubeVtk(self.renderer, self.cubo.l, white=True)
        self.metodoEditCubo.setStyle(self.separacion.value() / 100,
                                     self.innerColor,
                                     self.backgroundColor,
                                     (self.camPositionAzim.value(),
                                      self.camPositionElev.value(),
                                      self.camPositionZoom.value()
                                      )
                                     )
        self.listaEditados = []
        self.anim.cuboAnim = self.metodoEditCubo
        self.editMetodoId.clear()
        self.editMetodoId.addItems(['<New>'] + self.metodos.listaMetodos())
        self.editMetodoId.setCurrentText(texto[6:])
        self.editLoadMetodo(texto[6:])
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')
        self.editMetodoWidgets.show()
        self.arbolMetodosWidgets.hide()
        self.movimWidgets.hide()
        self.cuboWidgets.hide()
        self.styleWidgets.hide()

    @pyqtSlot()
    def changeEditModo(self, cambio):
        if not self.editModo.currentText():
            return
        n, m, r = self.editTimes.value(), self.editModo.currentText(), 6 * (self.cubo.l ** 2)
        if cambio == 'times':
            if n == 0 and m not in 'Best Match/Repeat':
                self.editModo.setCurrentText('Best Match')
                self.editTimes.setValue(0)
            elif n == 1 and m != 'Once':
                self.editModo.setCurrentText('Once')
                self.editTimes.setValue(1)
            elif n == 2 and m != 'Twice':
                self.editModo.setCurrentText('Twice')
                self.editTimes.setValue(2)
            elif n > 2 and n < r and m != 'times':
                self.editModo.setCurrentText('times')
            elif n >= r and m != 'Repeat':
                self.editModo.setCurrentText('Repeat')
                self.editTimes.setValue(0)
        else:  # cambio == 'modo'
            if m == 'times':
                if n < 3 or n > r:
                    self.editTimes.setValue(4)
            elif m in 'Best Match/Repeat' and n != 0:
                self.editTimes.setValue(0)
            elif m in 'Once/Twice' and n != {'Once': 1, 'Twice': 2}[m]:
                self.editTimes.setValue({'Once': 1, 'Twice': 2}[m])
        if m == 'times':
            self.metodoEditando.setModo(str(n) + ' times')
        else:
            self.metodoEditando.setModo(m)
        self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')

    @pyqtSlot()
    def changeEditUntil1st(self):
        if self.editUntil1st.currentText():
            self.metodoEditando.setUntil1st(self.editUntil1st.currentText())
            self.editArchivoModificado.setText('*' if self.metodos.modif else ' ')

    @pyqtSlot()
    def editarMetodoFin(self):
        if self.metodoEditando.id == '<New>':
            self.metodos.delete('<New>', recursivo=True)
        self.editMetodoWidgets.hide()
        self.renderer.RemoveAllViewProps()
        self.cubo.inicActores()
        self.anim.cuboAnim = self.cubo
        self.arbolMetodosWidgets.show()
        self.arbolMetodos.clear()
        self.addItemsArbolMetodos(self.metodoEditando.id)
        self.movimWidgets.show()
        self.cuboWidgets.show()
        self.styleWidgets.show()

    @pyqtSlot()
    def changeMezcladoPrevio(self):
        if self.mezcladoPrevio.value() == 0:
            self.botonMostrarEjecucion.setDisabled(False)
        else:
            self.botonMostrarEjecucion.setDisabled(True)

    def crearShowSolutionWidgets(self):
        self.showSolutionWidgets = Qt.QGroupBox("Solucion")

        self.soluc = []

        self.listaSolucWidget = Qt.QTableWidget()
        self.listaSolucWidget.setColumnCount(2)
        self.listaSolucWidget.verticalHeader().hide()
        self.listaSolucWidget.horizontalHeader().hide()
        self.listaSolucWidget.currentCellChanged.connect(self.setExplicacionMetodo)

        self.explicacionMetodo = Qt.QTextEdit()
        self.explicacionMetodo.setReadOnly(True)

        self.solucShowUnused = Qt.QCheckBox('Unused')
        self.solucShowUnused.setChecked(False)
        self.solucShowUnused.stateChanged.connect(self.solucShowUnusedOnOff)
        self.solucShowHints = Qt.QCheckBox('Hints')
        self.solucShowHints.setChecked(False)
        self.solucShowHints.stateChanged.connect(self.solucShowHintsOnOff)
        self.solucFinButton = Qt.QPushButton('Fin')
        self.solucFinButton.clicked.connect(self.solucFin)
        self.solucBBackButton = Qt.QPushButton('|<')
        self.solucBBackButton.clicked.connect(lambda: self.solucPlayBackwards(3))
        self.solucBackButton = Qt.QPushButton('<')
        self.solucBackButton.clicked.connect(lambda: self.solucPlayBackwards(1))
        self.solucPlayButton = Qt.QPushButton('>')
        self.solucPlayButton.clicked.connect(lambda: self.solucPlay(1))
        self.solucPPlayButton = Qt.QPushButton('>>')
        self.solucPPlayButton.clicked.connect(lambda: self.solucPlay(2))
        self.solucPPPlayButton = Qt.QPushButton('>|')
        self.solucPPPlayButton.clicked.connect(lambda: self.solucPlay(3))

        layout = Qt.QGridLayout()
        layout.addWidget(self.listaSolucWidget, 0, 0, 12, 1)
        layout.addWidget(self.explicacionMetodo, 12, 0, 3, 1)
        lay = Qt.QHBoxLayout()
        lay.addWidget(self.solucShowUnused)
        lay.addWidget(self.solucShowHints)
        lay.addWidget(self.solucBBackButton)
        lay.addWidget(self.solucBackButton)
        lay.addWidget(self.solucPlayButton)
        lay.addWidget(self.solucPPlayButton)
        lay.addWidget(self.solucPPPlayButton)
        lay.addWidget(self.solucFinButton)
        layout.addLayout(lay, 15, 0, 1, 1)
        self.showSolutionWidgets.setLayout(layout)

    @pyqtSlot()
    def solucShowHintsOnOff(self):
        #        self.solucPPlayButton.setDisabled( self.solucShowHints.isChecked() )
        self.solucPPPlayButton.setDisabled(self.solucShowHints.isChecked())
        if self.solucShowHints.isChecked():
            if self.solucRow < len(self.soluc):
                self.actualizaCurrentRowSoluc(self.solucRow)
        else:
            self.clearHints(self.cubo)

    @pyqtSlot()
    def setExplicacionMetodo(self):
        row = self.listaSolucWidget.currentRow()
        if row < len(self.soluc):
            self.explicacionMetodo.setText(self.soluc[row].metodo.comment)

    def cargaSolucion(self):
        # Retoco la lista self.soluc para que no haya 2 renglones ejecutables (Alg o Pos) seguidos. 
        # Esto ultimo necesario para ver bien los hints.
        anteriorEjecutable = False
        row = 0
        while row < len(self.soluc):
            s = self.soluc[row]
            if s.tipo in 'Alg/Pos':
                if anteriorEjecutable:
                    self.soluc.insert(row, met.Sol(s.nivel, '...', '', s.hizo, s.metodo, False, self.cubo.vars))
                    row += 1
                anteriorEjecutable = True
            else:
                anteriorEjecutable = False
            row += 1
        # cargo la lista al widget de visualizacion
        self.listaSolucWidget.clear()
        self.listaSolucWidget.setRowCount(len(self.soluc) + 1)
        for row in range(len(self.soluc)):
            s = self.soluc[row]
            self.listaSolucWidget.setItem(row, 0, Qt.QTableWidgetItem(' '))
            self.listaSolucWidget.setItem(row, 1, Qt.QTableWidgetItem(
                '        ' * s.nivel +
                ('  ' if s.hizo else '( ') +
                s.tipo + ' : ' + s.texto +
                ('  ' if s.hizo else ' )')
            ))
        self.listaSolucWidget.setItem(len(self.soluc), 0, Qt.QTableWidgetItem(' '))
        self.listaSolucWidget.setItem(len(self.soluc), 1, Qt.QTableWidgetItem('< End >'))
        self.solucShowUnusedOnOff()
        for row in range(len(self.soluc) + 1):
            self.listaSolucWidget.setCurrentCell(row, 0)
            self.listaSolucWidget.currentItem().setFlags(
                self.listaSolucWidget.currentItem().flags() & ~QtCore.Qt.ItemIsEditable)
            self.listaSolucWidget.setCurrentCell(row, 1)
            self.listaSolucWidget.currentItem().setFlags(
                self.listaSolucWidget.currentItem().flags() & ~QtCore.Qt.ItemIsEditable)
        self.solucRow = 0
        self.listaSolucWidget.setCurrentCell(0, 0)
        self.listaSolucWidget.currentItem().setText('>')
        self.listaSolucWidget.setCurrentCell(0, 1)
        # es increible pero no me funciono ningun otro metodo para que la columna tenga un ancho razonable...
        self.listaSolucWidget.insertRow(len(self.soluc) + 1)
        self.listaSolucWidget.setItem(len(self.soluc) + 1, 1, Qt.QTableWidgetItem('X' * 50))
        self.listaSolucWidget.setItem(len(self.soluc) + 1, 0, Qt.QTableWidgetItem('>'))
        self.listaSolucWidget.resizeColumnToContents(0)
        self.listaSolucWidget.resizeColumnToContents(1)
        self.listaSolucWidget.setRowHidden(len(self.soluc) + 1, True)
        for row in range(len(self.soluc) + 1):
            self.listaSolucWidget.resizeRowToContents(row)

    def actualizaCurrentRowSoluc(self, row):
        self.listaSolucWidget.setCurrentCell(self.solucRow, 0)
        self.listaSolucWidget.currentItem().setText(' ')
        self.solucRow = row
        self.listaSolucWidget.setCurrentCell(row, 0)
        self.listaSolucWidget.currentItem().setText('>')
        self.listaSolucWidget.setCurrentCell(row, 1)
        if row < len(self.soluc):
            if self.solucShowHints.isChecked():
                if self.soluc[row].tipo in 'Alg/Pos':
                    self.clearHints(self.cubo)
                    posic = self.soluc[row].texto if self.soluc[row].tipo == 'Pos' else ''
                    self.showHints(
                        self.cubo,
                        self.soluc[row].metodo,
                        self.soluc[row].vars,
                        posic,
                        self.soluc[row].mirror,
                        mostrarTextoCond=False
                    )
        if len(self.anim.jobs) == 1:  # este es el ultimo job de la lista
            self.disableWhenPlaying(False)

    def listaCeldas2listaHints(self, cubo, listaCeldas, mirror, posic):
        ret = []
        for lc in listaCeldas:
            if type(lc) is tuple:
                if mirror:
                    lc = met.mirrorCelda(cubo, lc)
                (cara, fila, columna, coloresPosibles) = lc
                (cara, fila, columna) = met.celdaEquiv(cubo, cara, fila, columna, posic)
                for color in palabras(coloresPosibles):
                    if ',' in color:  # es una funcion de 2 parametros (a=, c=, a! o c!)
                        c0 = color[0:2]
                        c1, c2 = primerPalabra(color[2:], ',')
                        ret.append((cara, fila, columna, c0 + c1))
                        ret.append((cara, fila, columna, c0 + c2))
                    else:
                        ret.append((cara, fila, columna, color))
            else:  # es una sublista (or)
                for lcOr in lc:
                    if mirror:
                        lcOr = met.mirrorCelda(cubo, lcOr)
                    (cara, fila, columna, coloresPosibles) = lcOr
                    (cara, fila, columna) = met.celdaEquiv(cubo, cara, fila, columna, posic)
                    for color in palabras(coloresPosibles):
                        if ',' in color:  # es una funcion de 2 parametros (a=, c=, a! o c!)
                            c0 = color[0:2]
                            c1, c2 = primerPalabra(color[2:], ',')
                            ret.append((cara, fila, columna, c0 + c1))
                            ret.append((cara, fila, columna, c0 + c2))
                        else:
                            ret.append((cara, fila, columna, color))
        return ret

    def showHints(self, cubo, metodo, vars, posic, mirror, mostrarTextoCond):
        listaCeldas = met.cond2ListaCeldas(cubo, vars, metodo.listaCondiciones)
        listaHints = self.listaCeldas2listaHints(cubo, listaCeldas, mirror, posic)
        for h in listaHints:
            cara, fila, columna, color = h
            (addOn, colName) = ((color[0:2], color[2:]) if color[1] in '> = !' else ('==', color))
            act1 = self.gallery.actor(colName)
            if mostrarTextoCond:
                act2 = self.gallery.actorT(addOn)
            else:
                act2 = self.gallery.actor(addOn)
            cubo.c[cara][fila, columna].ass.AddPart(act1)
            cubo.c[cara][fila, columna].otros.append((0.1, act1))  # ( desplazamiento, actor )
            cubo.c[cara][fila, columna].ass.AddPart(act2)
            cubo.c[cara][fila, columna].otros.append((0.035, act2))  # ( desplazamiento, actor )
        cubo.refreshActores()

    def clearHints(self, cubo):
        for cara in 'UDFBLR':
            for f in range(cubo.l):
                for c in range(cubo.l):
                    for (_, act) in cubo.c[cara][f, c].otros:
                        cubo.c[cara][f, c].ass.RemovePart(act)
                    cubo.c[cara][f, c].otros = []
        cubo.renderer.GetRenderWindow().Render()

    @pyqtSlot()
    def solucShowUnusedOnOff(self):
        for i in range(len(self.soluc)):
            self.listaSolucWidget.setRowHidden(i, not self.soluc[i].hizo and not self.solucShowUnused.isChecked())

    @pyqtSlot()
    def solucPlayBackwards(self, tipoDetencion):
        # tipoDetencion : 1 = vuelve atras un renglon
        #                 2 = no creo que vaya a usar esta opcion... si la necesito la programo...
        #                 3 = vuelve atras hasta el principio
        if self.solucRow == 0:
            return
        self.clearHints(self.cubo)
        self.listaSolucWidget.setFocus()
        row = self.proxSolucRowHizo(self.solucRow, -1)
        s = self.soluc[row]
        if s.tipo in 'Alg/Pos':
            self.cubo.mover(s.texto, animacion=False, haciaAtras=True)
        while row > 0 and tipoDetencion == 3:
            row = self.proxSolucRowHizo(row, -1)
            s = self.soluc[row]
            if s.tipo in 'Alg/Pos':
                self.cubo.mover(s.texto, animacion=False, haciaAtras=True)
        self.actualizaCurrentRowSoluc(row)
        self.cubo.refreshActores()

    def disableWhenPlaying(self, dis):
        self.solucPlayButton.setDisabled(dis)
        self.solucPPlayButton.setDisabled(dis)
        self.solucPPPlayButton.setDisabled(dis)
        self.solucBackButton.setDisabled(dis)
        self.solucBBackButton.setDisabled(dis)
        self.solucShowHints.setDisabled(dis)
        if not dis:
            #            self.solucPPlayButton.setDisabled( self.solucShowHints.isChecked() )
            self.solucPPPlayButton.setDisabled(self.solucShowHints.isChecked())

    def proxSolucRowHizo(self, row, inc=1):
        row = row + inc
        if 0 <= row < len(self.soluc):
            while (not self.soluc[row].hizo) and (0 <= row + inc < len(self.soluc)):
                row = row + inc
            if not self.soluc[row].hizo:
                row = row + inc
        return max(row, 0)

    def getNivelMetodo(self, row):
        s = self.soluc[row]
        while 'Met' not in s.tipo:
            row -= 1
            s = self.soluc[row]
        return s.nivel

    @pyqtSlot()
    def solucPlay(self, tipoDetencion):
        # tipoDetencion : 1 = ejecuta solo el renglon donde estoy parado y se detiene en el siguiente
        #                 2 = se detiene en el siguiente metodo que tenga el mismo nivel que el actual
        #                 3 = ejecutar hasta el final
        if self.solucRow >= len(self.soluc):
            return
        self.disableWhenPlaying(True)
        self.listaSolucWidget.setFocus()
        row = self.solucRow
        s = self.soluc[row]
        detenerEnImportants = False
        nivelDetencion = {1: 9999999, 2: self.getNivelMetodo(row), 3: 0}[tipoDetencion]
        if self.solucShowHints.isChecked():
            nivelDetencion = 0  # Si 'ShowHints', voy de algoritmo en algoritmo, saco la restriccion del nivel de detencion
            detenerEnImportants = (tipoDetencion == 2)  # si ademas presionaron '>>', detener en 'importants'
        comienzoEnAlg = (s.tipo in 'Alg/Pos')
        if not comienzoEnAlg or not self.solucShowHints.isChecked():
            self.clearHints(self.cubo)
        if s.tipo in 'Alg/Pos':
            self.anim.addJobs(s.texto)
        row = self.proxSolucRowHizo(row)
        if comienzoEnAlg:
            self.anim.addJobs('Actualiza-' + str(row))
            return
        while row < len(self.soluc):
            s = self.soluc[row]
            if s.nivel <= nivelDetencion:
                break
            if s.tipo in 'Alg/Pos' and self.solucShowHints.isChecked():
                if detenerEnImportants:
                    if s.tipo == 'Alg' and s.metodo.important:
                        break
                else:
                    break  # se detiene en cualquier renglon, siempre que sea un 'Alg' o 'Pos'
            self.anim.addJobs('Actualiza-' + str(row))
            if s.tipo in 'Alg/Pos':
                self.anim.addJobs(s.texto)
            row = self.proxSolucRowHizo(row)
        self.anim.addJobs('Actualiza-' + str(row))

    @pyqtSlot()
    def solucFin(self):
        self.clearHints(self.cubo)
        self.showSolutionWidgets.hide()
        self.tamanio.setDisabled(False)
        self.botonReset.setDisabled(False)
        self.botonMezclar.setDisabled(False)
        self.loadPreset.setDisabled(False)
        self.arbolMetodosWidgets.show()
        self.movimWidgets.show()

    def setAnimInc(self):
        x = self.dialAnimacion.value()
        self.anim.inc = (x / 5) + 90 / (100 - x)
        self.anim.mostrarMovim = self.showMovimCheckBox.isChecked()

    def elegirColorInterior(self):
        color = Qt.QColorDialog.getColor(initial=self.innerColor, options=Qt.QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.innerColor = color
            self.botonColorInt.setStyleSheet("background-color: " + self.innerColor.name())
            self.setStyle()

    def elegirColorFondo(self):
        color = Qt.QColorDialog.getColor(initial=self.backgroundColor, options=Qt.QColorDialog.ShowAlphaChannel)
        if color.isValid():
            self.backgroundColor = color
            self.botonColorFon.setStyleSheet("background-color: " + self.backgroundColor.name())
            self.setStyle()

    @pyqtSlot()
    def mostrarEjecucion(self):
        texto = self.arbolMetodos.currentItem().text(0)
        if texto[0:6] == 'Met : ':
            cuboAuxiliar = self.saveCubo()
            self.soluc = []
            t = time.time()
            met.ejecutarMetodo(self.cubo, self.metodos.metodo(texto[6:]), self.soluc)
            t = str(datetime.timedelta(seconds=round(time.time() - t, 2)))[:-4]
            alert('{0} movimientos, tiempo de ejecucion: {1}'.format(met.cantMovim(self.soluc), t))
            self.loadCuboFrom(cuboAuxiliar)
            self.cargaSolucion()
            self.arbolMetodosWidgets.hide()
            self.movimWidgets.hide()
            self.tamanio.setDisabled(True)
            self.botonReset.setDisabled(True)
            self.botonMezclar.setDisabled(True)
            self.loadPreset.setDisabled(True)
            self.showSolutionWidgets.show()
            self.disableWhenPlaying(False)

    @pyqtSlot()
    def ejecutarMetodo(self):
        texto = self.arbolMetodos.currentItem().text(0)
        if self.mezcladoPrevio.value() > 0:
            if texto[0:6] == 'Met : ':

                self.vtkWidget.setDisabled(True)
                self.cuboWidgets.setDisabled(True)
                self.styleWidgets.setDisabled(True)
                self.arbolMetodosWidgets.setDisabled(True)
                self.movimWidgets.setDisabled(True)
                self.showSolutionWidgets.setDisabled(True)
                self.animWidgets.setDisabled(True)

                self.anim.endAllJobs()
                tot = self.mezcladoPrevio.value()
                self.animProgressBar.setRange(0, tot)
                t = time.time()
                cantMovim = 0
                while self.mezcladoPrevio.value() > 0:
                    self.cubo.mezclar()
                    self.cubo.refreshActores()
                    cuboAuxiliar = self.saveCubo()
                    self.soluc = []
                    (hizo, success) = met.ejecutarMetodo(self.cubo, self.metodos.metodo(texto[6:]), self.soluc)
                    cantMovim = cantMovim + met.cantMovim(self.soluc)
                    if success:
                        self.mezcladoPrevio.setValue(self.mezcladoPrevio.value() - 1)
                        self.animProgressBar.setValue(tot - self.mezcladoPrevio.value())
                    else:
                        self.loadCuboFrom(cuboAuxiliar)
                        self.mezcladoPrevio.setValue(0)
                self.cubo.refreshActores()
                if success:
                    t = str(datetime.timedelta(seconds=round((time.time() - t) / tot, 2)))[:-4]
                    alert('Promedio: {0} movimientos, tiempo de ejecucion promedio: {1}'.format(cantMovim // tot, t))

                self.vtkWidget.setDisabled(False)
                self.cuboWidgets.setDisabled(False)
                self.styleWidgets.setDisabled(False)
                self.arbolMetodosWidgets.setDisabled(False)
                self.movimWidgets.setDisabled(False)
                self.showSolutionWidgets.setDisabled(False)
                self.animWidgets.setDisabled(False)

            self.mezcladoPrevio.setValue(0)
            self.animProgressBar.setRange(0, 1)
            self.animProgressBar.setValue(0)
        else:
            if texto[0:6] == 'Met : ':
                cuboAuxiliar = self.saveCubo()
                self.soluc = []
                met.ejecutarMetodo(self.cubo, self.metodos.metodo(texto[6:]), self.soluc)
                self.loadCuboFrom(cuboAuxiliar)
                for s in self.soluc:
                    if s.tipo in 'Pos/Alg':
                        self.anim.addJobs(s.texto)  # el movimiento lo hace anim.callBack cuando sea oportuno
            elif texto[0:6] == 'Pos : ':
                self.anim.addJobs(texto[6:])  # el movimiento lo hace anim.callBack cuando sea oportuno
            elif texto[0:6] == 'Alg : ':
                self.anim.addJobs(texto[6:])  # el movimiento lo hace anim.callBack cuando sea oportuno

    @pyqtSlot()
    def clickHacerMovim(self):
        movim = self.movimientos.text()
        self.anim.addJobs(movim)  # el movimiento lo hace anim.callBack cuando sea oportuno
        self.movimientos.setText("")

    class Preset:
        def __init__(self, c=None, l=None, conn=None, relColores=None):
            self.c = c
            self.l = l
            self.conn = conn
            self.relColores = relColores

    def saveCubo(self):
        # guardo solo algunos campos pues los objetos de vtk no son "deep copiables"
        cub = Cube(self.cubo.l)
        for cara in cub.c:
            for fila in range(cub.l):
                for columna in range(cub.l):
                    cub.c[cara][fila, columna].id = self.cubo.c[cara][fila, columna].id
                    cub.c[cara][fila, columna].color = self.cubo.c[cara][fila, columna].color
        preset = self.Preset(cub.c,
                             self.cubo.l,
                             copy.deepcopy(self.cubo.conn),
                             copy.deepcopy(self.cubo.relColores)
                             )
        return preset

    def loadCuboFrom(self, preset):
        if self.tamanio.value() != preset.l:
            self.tamanio.setValue(self.cubo.l)
        for cara in preset.c:
            for fila in range(preset.l):
                for columna in range(preset.l):
                    self.cubo.c[cara][fila, columna].id = preset.c[cara][fila, columna].id
                    self.cubo.c[cara][fila, columna].color = preset.c[cara][fila, columna].color
        self.cubo.l = preset.l
        self.cubo.conn = copy.deepcopy(preset.conn)
        self.cubo.relColores = copy.deepcopy(preset.relColores)
        self.renderer.RemoveAllViewProps()
        self.cubo.inicActores()

    @pyqtSlot()
    def clickSavePreset(self):
        p = self.preset.currentText()[0]
        self.presets[p] = self.saveCubo()
        self.presetIter += 1
        p = '{item}: {n}x{n} ({iter})'.format(item=p, n=self.cubo.l, iter=self.presetIter)
        self.preset.setItemText(self.preset.currentIndex(), p)

    @pyqtSlot()
    def clickLoadPreset(self):
        self.anim.endAllJobs()
        p = self.preset.currentText()[0]
        if p in self.presets:
            self.loadCuboFrom(self.presets[p])
            self.cubo.resetCamara()

    @pyqtSlot()
    def cambioTamanio(self):
        self.anim.endAllJobs()
        self.cubo.cambioTamanio(self.tamanio.value())

    @pyqtSlot()
    def clickBotonReset(self):
        self.anim.endAllJobs()
        self.cubo.inicCeldas()
        self.cubo.refreshActores()

    @pyqtSlot()
    def setStyle(self):
        self.cubo.setStyle(self.separacion.value() / 100,
                           self.innerColor,
                           self.backgroundColor,
                           (self.camPositionAzim.value(),
                            self.camPositionElev.value(),
                            self.camPositionZoom.value()
                            )
                           )
        self.setAnimInc()

    @pyqtSlot()
    def clickBotonMezclar(self):
        self.anim.endAllJobs()
        self.cubo.mezclar()
        self.cubo.refreshActores()

    @pyqtSlot()
    def clickResetCamara(self):
        self.cubo.resetCamara()


if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
