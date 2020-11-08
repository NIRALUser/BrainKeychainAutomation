import os
import vtk
import itertools

def main():
    # Gets user input for input directories
    getInput = True
    while getInput:
        brainDir = input("Keychain directory location: ")
        if not(os.path.isdir(brainDir)):
            print("Directory does not exist")
        else:
            getInput = False
    getInput = True
    while getInput:
        nametagDir = input("Nametag directory location: ")
        if not(os.path.isdir(nametagDir)):
            print("Directory does not exist")
        else:
            getInput = False
    # Match keychains and nametags (will be used later when rest of script is working)
    matchedBrainTags = {}
    brainScans = os.listdir(brainDir)
    # Matches the two if the brain filename contains the tag filename
    for filename in os.listdir(nametagDir):
        for brain in brainScans:
            if(filename[:len(filename)-4] in brain):
                matchedBrainTags[nametagDir + filename] = brainDir + brain
    # Hard cooded translation for keychains
    switcherBrain = {0: [-50,60,0],
    1: [0,60,0],
    2: [50,60,0],
    3: [-50,0,0],
    4: [0,0,0],
    5: [50,0,0]}
    # Hard cooded translation for nametags
    switcherNameTag = {0: [-90,60,0],
    1: [-40,60,0],
    2: [10,60,0],
    3: [-90,0,0],
    4: [-40,0,0],
    5: [10,0,0]}

    sceneCount = len(matchedBrainTags) % 6
    sceneIterator = 0
    totalBrainLength = len(matchedBrainTags)
    print(totalBrainLength)
    macthedKeys = list(matchedBrainTags.keys())

    while sceneIterator < sceneCount:

        keychainBounds = []
        keychainZMax = 0

        zBoundCounter = 0
        # Find max z height so that it can be used to raise other surfaces to that level (make level scene)
        while zBoundCounter < 6:
            reader = vtk.vtkSTLReader()  
            reader.SetFileName(matchedBrainTags[macthedKeys[sceneIterator + zBoundCounter]])

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            mapper.Update()
            bounds = mapper.GetBounds()
            if(bounds[4] > keychainZMax):
                keychainZMax = bounds[4]
            zBoundCounter += 1

        coordinateCount = 0 # Used to keep track of which translation needs to be done for what part of the scene the loop is on.
        appendFilter = vtk.vtkAppendPolyData()

        appendingCounter = 0
        while appendingCounter < 6:
            # Append key chain
            reader = vtk.vtkSTLReader()  # Read keychain
            print(matchedBrainTags[macthedKeys[sceneIterator + appendingCounter]])
            reader.SetFileName(matchedBrainTags[macthedKeys[sceneIterator + appendingCounter]])

            # Use mapper to get keychain bounds to correctly place in scene
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())
            mapper.Update()
            bounds = mapper.GetBounds() #Return bounding box (array of six doubles) of data expressed as (xmin,xmax, ymin,ymax, zmin,zmax).

            trans = vtk.vtkTransform()   # Set translation
            coordinates = switcherBrain[coordinateCount]
            trans.Translate(coordinates[0], coordinates[1], (coordinates[2] + (keychainZMax - bounds[4])))  # Add z offset to final translation

            process = vtk.vtkTransformPolyDataFilter()  # Process translate
            process.SetTransform(trans)
            process.SetInputConnection(reader.GetOutputPort())
            process.Update()

            appendFilter.AddInputConnection(process.GetOutputPort())    # Append to scene
            appendFilter.Update()

            # Append name tag
            reader = vtk.vtkSTLReader() # Read nametag
            print(macthedKeys[sceneIterator + appendingCounter])
            reader.SetFileName(macthedKeys[sceneIterator + appendingCounter])

            trans = vtk.vtkTransform()  # Set transltion
            coordinates = switcherNameTag[coordinateCount]
            trans.Translate(coordinates[0], coordinates[1], coordinates[2] + keychainZMax)

            process = vtk.vtkTransformPolyDataFilter()  # Process translate
            process.SetTransform(trans)
            process.SetInputConnection(reader.GetOutputPort())
            process.Update()

            appendFilter.AddInputConnection(process.GetOutputPort())    # Append to scene
            appendFilter.Update()


            coordinateCount += 1
            appendingCounter += 1
            if((coordinateCount + (sceneIterator * 6)) == totalBrainLength):
                appendingCounter = 7    # End loop because out of surfaces but less than scene max

        # Write print scene
        writer = vtk.vtkSTLWriter()
        writer.SetFileName('keyChainScene' + str(sceneIterator) + '.stl')
        writer.SetInputConnection(appendFilter.GetOutputPort())
        writer.Write()

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
