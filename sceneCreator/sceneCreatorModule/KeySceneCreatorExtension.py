import os
import vtk, qt, ctk, slicer
import itertools
import subprocess
import math
from slicer.ScriptedLoadableModule import *
import logging
import slicer

#
# KeySceneCreatorExtension
#

class KeySceneCreatorExtension(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "KeySceneCreator Extension"
    self.parent.categories = ["Keychain to print scene"]
    self.parent.dependencies = []
    self.parent.contributors = ["Christian Nell, Martin Styner (UNC-Chapel Hill)"]
    self.parent.helpText = """
This extension generates a print scene with keychains.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
Neuro Image Research and Analysis Lab, University of North Carolina, Chapel Hill
""" # replace with organization, grant and thanks.

#
# KeySceneCreatorExtensionWidget
#

class KeySceneCreatorExtensionWidget(ScriptedLoadableModuleWidget):
  """Interface class, Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)


    # Adds width text box
    self.widthInput = qt.QLineEdit()
    parametersFormLayout.addRow("Input print surface width (cm): ", self.widthInput)


    # Adds length text box
    self.lengthInput = qt.QLineEdit()
    parametersFormLayout.addRow("Input print surface length (cm): ", self.lengthInput)

    # Adds search directory text box
    self.inputDirSelector = ctk.ctkPathLineEdit()
    self.inputDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.inputDirSelector.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.inputDirSelector.settingKey = 'inputDir'
    parametersFormLayout.addRow("Location of 'Keychain' folder (required):", self.inputDirSelector)

    # Adds bash directory text box
    self.bashDirSelector = ctk.ctkPathLineEdit()
    self.bashDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.bashDirSelector.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.bashDirSelector.settingKey = 'bashDir'
    parametersFormLayout.addRow("Location of 'keyChainNameTagCreator.bash' folder (required):", self.bashDirSelector)


    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the keychain scene generator."
    self.applyButton.enabled = True
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)


  def onApplyButton(self):
    logic = KeySceneCreatorExtensionLogic()
    logic.run(self.widthInput.text, self.lengthInput.text, self.inputDirSelector.currentPath,
        self.bashDirSelector.currentPath)


#
# KeySceneCreatorExtensionLogic
#

class KeySceneCreatorExtensionLogic(ScriptedLoadableModuleLogic):
  """This class implements the generation of the key chain surface from the brain surfaces
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def run(self, width, length, inputDir, bashDir):
    """
    Run the actual algorithm
    """
    logging.info('Processing started')

    def createScene(matchedBrainTags, brainsPerScene, sceneIterator, brainsPerXAxis, brainsPerYAxis, inputDir):
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
        writer.SetFileName(inputDir + '/Scenes/keyChainScene' + str(sceneIterator) + '.stl')
        writer.SetInputConnection(appendFilter.GetOutputPort())
        writer.Write()
        return True

    def sceneSetup(width, length, inputDir, bashDir):
        print('This script assumes each keychain is no larger than 50 mm in width and 50 mm in length.')
        print('Each keychain and nametag are allocated 50 mm in width and 70 mm in length for spacing.')
                #inputWidth = int(input('Enter printer surface width in millimeters: '))
                #inputLength = int(input('Enter printer surface length in millimeters: '))
        inputWidth = width
        inputLength = length
        brainsPerXAxis = math.floor(inputWidth / 50)
        brainsPerYAxis = math.floor(inputLength / 70)
        brainsPerScene = brainsPerXAxis * brainsPerYAxis
        subprocess.call(['./keyChainNameTagCreator.bash'], cwd=bashDir)
        # Gets user input for input directories
                #brainDir = os.getcwd() + "/Keychains/"
                #nametagDir = os.getcwd() + "/Nametags/"
        brainDir = inputDir + "/Keychains/"
        nametagDir = bashDir + "/Nametags/"
        subprocess.call(['mkdir', inputDir + '/Scenes'])
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
            createScene(matchedBrainTags, brainsPerScene, sceneIterator, brainsPerXAxis, brainsPerYAxis, inputDir)
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

    width = int(width)
    length = int(length)
    sceneSetup(width, length, inputDir, bashDir)
