import vtk
from util import Clase


class Gallery:

    def __init__(self):
        self.points = vtk.vtkPoints()
        self.points.SetNumberOfPoints(25)
        for i in range(5):
            for j in range(5):
                self.points.SetPoint(5 * i + j, i - 2, j - 2, 0)

        self.lines = []
        self.lines.append(Clase())
        self.lines[-1].cellPoints = [2, 20, 24, 2]  # triangulo
        self.lines.append(Clase())
        self.lines[-1].cellPoints = [0, 16, 24, 8, 0]  # rombo
        self.lines.append(Clase())
        self.lines[-1].cellPoints = [5, 9, 19, 15, 5]  # rectangulo
        self.lines.append(Clase())
        self.lines[-1].cellPoints = [20, 2, 24, 12, 20]  # flecha
        self.lines.append(Clase())
        self.lines[-1].cellPoints = [0, 7, 4, 13, 24, 17, 20, 11, 0]  # cuadrado implosion
        self.lines.append(Clase())
        self.lines[-1].cellPoints = [10, 2, 14, 24, 20, 10]  # sobre
        self.lines.append(Clase())
        self.lines[-1].cellPoints = [0, 17, 4, 24, 20, 0]  # cuadrado con hendidura

        self.cicloFormas = len(self.lines)
        self.src = []
        self.map = []

        for f in range(self.cicloFormas):
            self.lines[f].cellArray = vtk.vtkCellArray()
            self.lines[f].cellArray.InsertNextCell(len(self.lines[f].cellPoints))
            for i in range(len(self.lines[f].cellPoints)):
                self.lines[f].cellArray.InsertCellPoint(self.lines[f].cellPoints[i])

            self.src.append(vtk.vtkPolyData())
            self.src[f].SetPoints(self.points)
            self.src[f].SetLines(self.lines[f].cellArray)

            self.map.append(vtk.vtkPolyDataMapper())
            self.map[f].SetInputData(self.src[f])
            self.map[f].Update()

        self.colores = [(1.0, 0.0, 1.0),
                        (0.0, 0.5, 0.5),
                        (0.7, 0.3, 0.3),
                        (0.5, 0.5, 0.5)
                        ]
        self.cicloColores = len(self.colores)

        self.colorVacio = len(self.colores)
        self.colorTachar = len(self.colores)
        self.colorCirculo = len(self.colores)
        self.colores.append((0.0, 0.0, 0.0))

        self.escala = 1 / 8

        # mapper Vacio
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(5)
        points.SetPoint(0, 0.0, 0.0, -0.1)
        points.SetPoint(1, -2.5, 0.0, -0.1)
        points.SetPoint(2, 2.5, 0.0, -0.1)
        points.SetPoint(3, 0.0, -2.5, -0.1)
        points.SetPoint(4, 0.0, 2.5, -0.1)
        caVacio = vtk.vtkCellArray()
        caVacio.InsertNextCell(1)
        caVacio.InsertCellPoint(0)
        srcVacio = vtk.vtkPolyData()
        srcVacio.SetPoints(points)
        srcVacio.SetLines(caVacio)
        mapVacio = vtk.vtkPolyDataMapper()
        mapVacio.SetInputData(srcVacio)
        mapVacio.Update()
        self.formaVacio = len(self.map)
        self.map.append(mapVacio)

        # mapper Tachar
        caTachar = vtk.vtkCellArray()
        caTachar.InsertNextCell(2)
        caTachar.InsertCellPoint(1)
        caTachar.InsertCellPoint(2)
        caTachar.InsertNextCell(2)
        caTachar.InsertCellPoint(3)
        caTachar.InsertCellPoint(4)
        srcTachar = vtk.vtkPolyData()
        srcTachar.SetPoints(points)
        srcTachar.SetLines(caTachar)
        mapTachar = vtk.vtkPolyDataMapper()
        mapTachar.SetInputData(srcTachar)
        mapTachar.Update()
        self.formaTachar = len(self.map)
        self.map.append(mapTachar)

        # mapper Circulo
        srcCirc = vtk.vtkRegularPolygonSource()
        srcCirc.SetNumberOfSides(32)
        srcCirc.SetRadius(2.5)
        srcCirc.GeneratePolygonOff()  # para que sea una circunferencia y no un circulo
        mapCirc = vtk.vtkPolyDataMapper()
        mapCirc.SetInputConnection(srcCirc.GetOutputPort())
        self.formaCirculo = len(self.map)
        self.map.append(mapCirc)

        self.resetCasting()

    def resetCasting(self):
        self.casting = {}
        self.casting["=="] = Clase()
        self.casting["=="].forma = self.formaVacio
        self.casting["=="].idxColor = self.colorVacio
        self.casting["->"] = Clase()
        self.casting["->"].forma = self.formaVacio
        self.casting["->"].idxColor = self.colorVacio
        self.casting["=>"] = Clase()
        self.casting["=>"].forma = self.formaVacio
        self.casting["=>"].idxColor = self.colorVacio
        self.casting["!="] = Clase()
        self.casting["!="].forma = self.formaTachar
        self.casting["!="].idxColor = self.colorTachar
        self.casting["a="] = Clase()
        self.casting["a="].forma = self.formaCirculo
        self.casting["a="].idxColor = self.colorCirculo
        self.casting["c="] = Clase()
        self.casting["c="].forma = self.formaCirculo
        self.casting["c="].idxColor = self.colorCirculo
        self.casting["o="] = Clase()
        self.casting["o="].forma = self.formaCirculo
        self.casting["o="].idxColor = self.colorCirculo
        self.casting["a!"] = Clase()
        self.casting["a!"].forma = self.formaCirculo
        self.casting["a!"].idxColor = self.colorCirculo
        self.casting["c!"] = Clase()
        self.casting["c!"].forma = self.formaCirculo
        self.casting["c!"].idxColor = self.colorCirculo
        self.casting["o!"] = Clase()
        self.casting["o!"].forma = self.formaCirculo
        self.casting["o!"].idxColor = self.colorCirculo
        self.nextForma = 0
        self.nextColor = 0

    def actor(self, nombre):
        if nombre not in self.casting:
            self.casting[nombre] = Clase()
            self.casting[nombre].forma = self.nextForma
            self.casting[nombre].idxColor = self.nextColor
            self.nextForma += 1
            self.nextColor += 1
            # como la cantidad de formas y COLORS son coprimas, recien vuelven a coincidir cuando se agoten las posibilidades
            if self.nextForma == self.cicloFormas:
                self.nextForma = 0
            if self.nextColor == self.cicloColores:
                self.nextColor = 0
        forma = self.casting[nombre].forma
        color = self.casting[nombre].idxColor
        act = vtk.vtkActor()
        act.SetMapper(self.map[forma])
        act.GetProperty().SetLineWidth(6)
        act.GetProperty().SetColor(self.colores[color])
        act.SetScale(self.escala, self.escala, self.escala)
        return act

    def actorT(self, texto):
        textSource = vtk.vtkVectorText()
        textSource.SetText(texto)
        textSource.Update()
        textMapper = vtk.vtkPolyDataMapper()
        textMapper.SetInputConnection(textSource.GetOutputPort())
        textActor = vtk.vtkActor()
        textActor.SetMapper(textMapper)
        textActor.GetProperty().SetColor(0, 0, 0)
        textActor.SetPosition(-0.4, -0.2, 0.0)
        textActor.SetScale(0.4, 0.4, 0.4)
        ass = vtk.vtkAssembly()
        ass.AddPart(textActor)
        return ass

    def symbolAndText(self, nombre, texto):
        textActor = self.actorT(texto)
        symbolActor = self.actor(nombre)
        textActor.SetPosition(-0.4, -0.2, 0.1)
        textActor.SetScale(0.4, 0.4, 0.4)
        ass = vtk.vtkAssembly()
        ass.AddPart(symbolActor)
        ass.AddPart(textActor)
        return ass
