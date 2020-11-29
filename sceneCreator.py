import os
import vtk
import itertools
import subprocess
import math

def createScene(matchedBrainTags, brainsPerScene, sceneIterator, brainsPerXAxis, brainsPerYAxis):
    keychainBounds = []
    keychainZMax = 0
    zBoundCounter = 0
    xAxisIterator = 0
    yAxisIterator = 0
    macthedKeys = list(matchedBrainTags.keys())
    # Find max z height so that it can be used to raise other surfaces to that level (make level scene)
    while zBoundCounter < brainsPerScene:
        reader = vtk.vtkSTLReader()  
        reader.SetFileName(matchedBrainTags[macthedKeys[zBoundCounter]])

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        mapper.Update()
        bounds = mapper.GetBounds()
        keychainBounds.append(bounds)
        if(bounds[4] > keychainZMax):
            keychainZMax = bounds[4]
        if(zBoundCounter == len(matchedBrainTags) - 1):
            zBoundCounter = brainsPerScene
        zBoundCounter += 1

    appendFilter = vtk.vtkAppendPolyData()

    appendingCounter = 0
    while appendingCounter < brainsPerScene:
        # Append key chain
        reader = vtk.vtkSTLReader()  # Read keychain
        print(matchedBrainTags[macthedKeys[appendingCounter]])
        reader.SetFileName(matchedBrainTags[macthedKeys[appendingCounter]])

        # Use mapper to get keychain bounds to correctly place in scene
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())
        mapper.Update()
        bounds = mapper.GetBounds() #Return bounding box (array of six doubles) of data expressed as (xmin,xmax, ymin,ymax, zmin,zmax).

        trans = vtk.vtkTransform()   # Set translation
        trans.Translate(xAxisIterator * 50, -(yAxisIterator * 70), keychainZMax - keychainBounds[appendingCounter][4])  # Add z offset to final translation

        process = vtk.vtkTransformPolyDataFilter()  # Process translate
        process.SetTransform(trans)
        process.SetInputConnection(reader.GetOutputPort())
        process.Update()

        appendFilter.AddInputConnection(process.GetOutputPort())    # Append to scene
        appendFilter.Update()

        # Append name tag
        reader = vtk.vtkSTLReader() # Read nametag
        print(macthedKeys[appendingCounter])
        reader.SetFileName(macthedKeys[appendingCounter])

        trans = vtk.vtkTransform()  # Set transltion
        trans.Translate((xAxisIterator * 50) - 35, -(yAxisIterator * 70) + 5, keychainZMax)

        process = vtk.vtkTransformPolyDataFilter()  # Process translate
        process.SetTransform(trans)
        process.SetInputConnection(reader.GetOutputPort())
        process.Update()

        appendFilter.AddInputConnection(process.GetOutputPort())    # Append to scene
        appendFilter.Update()

        if(appendingCounter == len(matchedBrainTags) - 1):
            appendingCounter = brainsPerScene    # End loop because out of surfaces but less than scene max
        if(xAxisIterator == brainsPerXAxis - 1):
            yAxisIterator += 1
            xAxisIterator = 0
        else:
            xAxisIterator += 1
        appendingCounter += 1

    # Write print scene
    writer = vtk.vtkSTLWriter()
    writer.SetFileName('./Scenes/keyChainScene' + str(sceneIterator) + '.stl')
    writer.SetInputConnection(appendFilter.GetOutputPort())
    writer.Write()
    return True

def main():
    inputWidth = int(input('Enter printer surface width in millimeters: '))
    inputHeight = int(input('Enter printer surface height in millimeters: '))
    brainsPerXAxis = math.floor(inputWidth / 50)
    brainsPerYAxis = math.floor(inputHeight / 70)
    brainsPerScene = brainsPerXAxis * brainsPerYAxis
    ##subprocess.call('./keyChainNameTagCreator.bash')
    # Gets user input for input directories
    brainDir = os.getcwd() + "/Keychains/"
    nametagDir = os.getcwd() + "/Nametags/"
    subprocess.call(['mkdir', os.getcwd() + '/Scenes'])
    # Match keychains and nametags (will be used later when rest of script is working)
    matchedBrainTags = {}
    brainScans = os.listdir(brainDir)
    # Matches the two if the brain filename contains the tag filename
    for filename in os.listdir(nametagDir):
        for brain in brainScans:
            if(filename[:len(filename)-4] in brain):
                matchedBrainTags[nametagDir + filename] = brainDir + brain

    totalBrainLength = len(matchedBrainTags)
    sceneCount = math.ceil(totalBrainLength / brainsPerScene)  # Finds number of scenes that will be printed
    sceneIterator = 0
    finalMacthedKeys = list(matchedBrainTags.keys()) 
    while sceneIterator < sceneCount:
        i = 0 # Iterator for deleting already used keychains
        createScene(matchedBrainTags, brainsPerScene, sceneIterator, brainsPerXAxis, brainsPerYAxis)
        if(not(sceneIterator == sceneCount - 1)):
            while(i < brainsPerScene):
                del matchedBrainTags[finalMacthedKeys[i]]
                i += 1
            finalMacthedKeys = finalMacthedKeys[brainsPerScene:]
        sceneIterator += 1

    # Create test visual of what the scene looks like
    '''
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(appendFilter.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)
    renderer.AddActor(actor)
    renderer.SetBackground(.3, .2, .1)
    renderWindow.Render()
    renderWindowInteractor.Start()
    '''
    return True

main()
