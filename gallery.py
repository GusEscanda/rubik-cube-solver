import vtk
from util import Clase


class Gallery:
    class Line:
        def __init__(self, cellPoints):
            self.cellPoints = cellPoints
            self.cellArray = vtk.vtkCellArray()
            self.cellArray.InsertNextCell(len(cellPoints))
            for i in range(len(self.cellPoints)):
                self.cellArray.InsertCellPoint(self.cellPoints[i])

    class Shape:
        def __init__(self, mapId, colorId):
            self.mapId = mapId
            self.colorId = colorId

    def __init__(self):
        self.points = vtk.vtkPoints()
        self.points.SetNumberOfPoints(25)
        for i in range(5):
            for j in range(5):
                self.points.SetPoint(5 * i + j, i - 2, j - 2, 0)

        self.lines = [
            self.Line([2, 20, 24, 2]),  # triangle
            self.Line([0, 16, 24, 8, 0]),  # diamond
            self.Line([5, 9, 19, 15, 5]),  # rectangle
            self.Line([20, 2, 24, 12, 20]),  # arrow
            self.Line([0, 7, 4, 13, 24, 17, 20, 11, 0]),  # implosion square
            self.Line([10, 2, 14, 24, 20, 10]),  # envelope
            self.Line([0, 17, 4, 24, 20, 0]),  # square with slit
        ]

        self.shapeCycle = len(self.lines)
        self.src = []
        self.map = []

        for f in range(self.shapeCycle):
            self.src.append(vtk.vtkPolyData())
            self.src[f].SetPoints(self.points)
            self.src[f].SetLines(self.lines[f].cellArray)

            self.map.append(vtk.vtkPolyDataMapper())
            self.map[f].SetInputData(self.src[f])
            self.map[f].Update()

        self.colors = [
            (1.0, 0.0, 1.0),
            (0.0, 0.5, 0.5),
            (0.7, 0.3, 0.3),
            (0.5, 0.5, 0.5)
        ]
        self.colorCycle = len(self.colors)
        self.colors.append((0.0, 0.0, 0.0))  # will cycle all the colors but this one

        self.scale = 1 / 8

        self.casting = {}

        # mapper Empty
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(5)
        points.SetPoint(0, 0.0, 0.0, -0.1)
        points.SetPoint(1, -2.5, 0.0, -0.1)
        points.SetPoint(2, 2.5, 0.0, -0.1)
        points.SetPoint(3, 0.0, -2.5, -0.1)
        points.SetPoint(4, 0.0, 2.5, -0.1)
        cellArray = vtk.vtkCellArray()
        cellArray.InsertNextCell(1)
        cellArray.InsertCellPoint(0)
        source = vtk.vtkPolyData()
        source.SetPoints(points)
        source.SetLines(cellArray)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(source)
        mapper.Update()
        self.map.append(mapper)
        self.casting["=="] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)
        self.casting["->"] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)
        self.casting["=>"] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)

        # mapper Cross out
        cellArray = vtk.vtkCellArray()
        cellArray.InsertNextCell(2)
        cellArray.InsertCellPoint(1)
        cellArray.InsertCellPoint(2)
        cellArray.InsertNextCell(2)
        cellArray.InsertCellPoint(3)
        cellArray.InsertCellPoint(4)
        source = vtk.vtkPolyData()
        source.SetPoints(points)
        source.SetLines(cellArray)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(source)
        mapper.Update()
        self.map.append(mapper)
        self.casting["!="] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)

        # mapper Circle
        source = vtk.vtkRegularPolygonSource()
        source.SetNumberOfSides(32)
        source.SetRadius(2.5)
        source.GeneratePolygonOff()  # make it a hollow circle
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        self.map.append(mapper)
        self.casting["a="] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)
        self.casting["c="] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)
        self.casting["o="] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)
        self.casting["a!"] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)
        self.casting["c!"] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)
        self.casting["o!"] = self.Shape(mapId=len(self.map)-1, colorId=len(self.colors)-1)

        self.nextShape = 0
        self.nextColor = 0

    def actor(self, name):
        if name not in self.casting:
            self.casting[name] = self.Shape(mapId=self.nextShape, colorId=self.nextColor)
            self.nextShape = (self.nextShape + 1) % self.shapeCycle
            self.nextColor = (self.nextColor + 1) % self.colorCycle
            # Since the number of shapes and colors are coprime, a combination will only be repeated when the possibilities are exhausted.
        mapId = self.casting[name].mapId
        colorId = self.casting[name].colorId
        act = vtk.vtkActor()
        act.SetMapper(self.map[mapId])
        act.GetProperty().SetLineWidth(6)
        act.GetProperty().SetColor(self.colors[colorId])
        act.SetScale(self.scale, self.scale, self.scale)
        return act

    def actorT(self, text):
        textSource = vtk.vtkVectorText()
        textSource.SetText(text)
        textSource.Update()
        textMapper = vtk.vtkPolyDataMapper()
        textMapper.SetInputConnection(textSource.GetOutputPort())
        textActor = vtk.vtkActor()
        textActor.SetMapper(textMapper)
        textActor.GetProperty().SetColor(0, 0, 0)
        textActor.SetPosition(-0.4, -0.2, 0.0)
        textActor.SetScale(0.4, 0.4, 0.4)
        assembly = vtk.vtkAssembly()
        assembly.AddPart(textActor)
        return assembly

    def symbolAndText(self, name, text):
        textActor = self.actorT(text)
        symbolActor = self.actor(name)
        textActor.SetPosition(-0.4, -0.2, 0.1)
        textActor.SetScale(0.4, 0.4, 0.4)
        assembly = vtk.vtkAssembly()
        assembly.AddPart(symbolActor)
        assembly.AddPart(textActor)
        return assembly
