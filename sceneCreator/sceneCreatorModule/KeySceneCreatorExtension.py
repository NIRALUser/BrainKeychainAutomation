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
This extension generates adaptive print scenes for keychains and their matching nametags. This script assumes 
each keychain is no larger than 50 mm in width and 50 mm in length. Each keychain and nametag are allocated 50 mm in width 
and 70 mm in length for spacing. All input fields below are required.
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
    self.widthInput.text = '160'
    parametersFormLayout.addRow("Input print surface width (in cm, required): ", self.widthInput)


    # Adds length text box
    self.lengthInput = qt.QLineEdit()
    self.lengthInput.text = '150'
    parametersFormLayout.addRow("Input print surface length (in cm, required): ", self.lengthInput)

    # Adds search directory finder
    self.inputDirSelector = ctk.ctkPathLineEdit()
    self.inputDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.inputDirSelector.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.inputDirSelector.currentPath = '/Users/christiannell/Desktop/research/NIRAL/BrainKeychainAutomation-main/sceneCreator'
    self.inputDirSelector.settingKey = 'inputDir'
    parametersFormLayout.addRow("Location of 'Keychains' folder (required):", self.inputDirSelector)

    # Adds output directory finder
    self.outputDirSelector = ctk.ctkPathLineEdit()
    self.outputDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.outputDirSelector.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.outputDirSelector.currentPath = '/Users/christiannell/Desktop/research/NIRAL/BrainKeychainAutomation-main/sceneCreator'
    self.outputDirSelector.settingKey = 'outputDir'
    parametersFormLayout.addRow("Output 'Scene' folder location (optional, blank will output in same folder as 'Keychains'):", self.outputDirSelector)

    # Adds bash directory finder
    self.bashDirSelector = ctk.ctkPathLineEdit()
    self.bashDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.bashDirSelector.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.bashDirSelector.currentPath = '/Users/christiannell/Desktop/research/NIRAL/BrainKeychainAutomation-main/sceneCreator'
    self.bashDirSelector.settingKey = 'bashDir'
    parametersFormLayout.addRow("Folder the 'keyChainNameTagCreator.bash' file is in (optional if in the same folder as 'Keychain'):", self.bashDirSelector)

    # Adds openSCAD file finder
    self.openSCADFileSelector = ctk.ctkPathLineEdit()
    self.openSCADFileSelector.currentPath = '/Users/christiannell/Desktop/research/NIRAL/BrainKeychainAutomation-main/sceneCreator/keyChainTitle.scad'
    self.openSCADFileSelector.settingKey = 'openSCADDir'
    parametersFormLayout.addRow("Location of 'keyChainTitle.scad' file (optional if in the same folder as 'Keychain'):", self.openSCADFileSelector)

    # Adds openSCAD directory finder
    self.openSCADDirSelector = ctk.ctkPathLineEdit()
    self.openSCADDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.openSCADDirSelector.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.openSCADDirSelector.currentPath = '/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD'
    self.openSCADDirSelector.settingKey = 'openSCADDir'
    parametersFormLayout.addRow("Location of 'OpenSCAD.app' file (required if OpenSCAD isn't located here):", self.openSCADDirSelector)


    #
    # check box to check if user wants to keep keychain and nametag folders
    #
    self.keepKeychainNametag = qt.QCheckBox()
    self.keepKeychainNametag.checked = True
    self.keepKeychainNametag.setToolTip("If checked, keeps the Keychain and Nametag folder. If not, deletes them after the scenes are created.")
    parametersFormLayout.addRow("Keep 'Keychains' and 'Nametags' folders: " , self.keepKeychainNametag)


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
        self.outputDirSelector.currentPath, self.bashDirSelector.currentPath, 
        self.openSCADFileSelector.currentPath, self.openSCADDirSelector.currentPath, 
        self.keepKeychainNametag.checked)


#
# KeySceneCreatorExtensionLogic
#

class KeySceneCreatorExtensionLogic(ScriptedLoadableModuleLogic):
  """This class implements the generation of the key chain surface from the brain surfaces
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def run(self, width, length, inputDir, outputDir, bashDir, openSCADFile, openSCADDir, keepKeyName):
    """
    Run the actual algorithm
    """
    logging.info('Processing started')

    def createScene(matchedBrainTags, brainsPerScene, sceneIterator, brainsPerXAxis, brainsPerYAxis, outputDir):
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
        writer.SetFileName(outputDir + '/Scenes/keyChainScene' + str(sceneIterator) + '.stl')
        writer.SetInputConnection(appendFilter.GetOutputPort())
        writer.Write()
        return True

    def sceneSetup(width, length, inputDir, outputDir, bashDir, openSCADFile, openSCADDir):
        inputWidth = width
        inputLength = length
        brainsPerXAxis = math.floor(inputWidth / 50)
        brainsPerYAxis = math.floor(inputLength / 70)
        brainsPerScene = brainsPerXAxis * brainsPerYAxis
        subprocess.call(['sh', 'keyChainNameTagCreator.bash', openSCADDir, openSCADFile, inputDir], cwd=bashDir)
        # Gets user input for input directories
        brainDir = inputDir + "/Keychains/"
        nametagDir = inputDir + "/Nametags/"
        subprocess.call(['mkdir', outputDir + '/Scenes'])
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
            createScene(matchedBrainTags, brainsPerScene, sceneIterator, brainsPerXAxis, brainsPerYAxis, outputDir)
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
    if (len(str(bashDir)) == 0):
        bashDir = inputDir
    if (len(str(openSCADFile)) == 0):
        openSCADFile = inputDir + '/keyChainTitle.scad'
    if (len(str(outputDir)) == 0):
        outputDir = inputDir
    sceneSetup(width, length, inputDir, outputDir, bashDir, openSCADFile, openSCADDir)
    if (not(keepKeyName)):
        subprocess.call(['rm', '-r', 'Keychains'], cwd=inputDir)
        subprocess.call(['rm', '-r', 'Nametags'], cwd=inputDir)

