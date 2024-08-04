# programita para probar/ver los dibujos de la gallery de simbolos


import vtk
import numpy as np

from gallery import Gallery

# Create the window, renderer, and interactor.
renderer = vtk.vtkRenderer()
textos = ['->', '=>', '==', '!=', 'a=', 'c=', 'o=', 'a!', 'c!', 'o!']
grid = 6
sep = 1
x, y = 0, 0
gal = Gallery()
for i in range(grid*grid):
    act = gal.symbolAndText(i, textos[i % len(textos)])
    act.SetPosition(x-(grid-1)*sep/2, y-(grid-1)*sep/2, 0)
    renderer.AddActor(act)
    x = x + sep
    if (i+1) % grid == 0:
        x, y = 0, y + sep


# renderer.AddActor(textactor)
window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
renderer.SetBackground(1,1,1)
renderer.ResetCamera()
renderer.GetRenderWindow().Render()

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

interactor.Initialize()
    
window.SetSize(500, 500)
window.Render()
interactor.Start()
