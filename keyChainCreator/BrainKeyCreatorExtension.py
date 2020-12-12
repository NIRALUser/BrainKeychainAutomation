import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import slicer
import SimpleITK as sitk
global sitkUtils
import sitkUtils
import numpy
import subprocess


#
# BrainKeyCreatorExtension
#

class BrainKeyCreatorExtension(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "BrainKeychain Extension"
    self.parent.categories = ["Surface Models"]
    self.parent.dependencies = []
    self.parent.contributors = ["Henry Pehr, Christian Nell, Martin Styner (UNC-Chapel Hill)"]
    self.parent.helpText = """
This extension generates a small key chain surface (for 3D printing) from brain surface input. Tested on Slicer 4.10.2, Python 2.7.13 and macOS.
Required: An input folder that contains VTK surfaces (left and right hemispheres). Filenames for the left and right hemispheres must be identical outside of 
'left' and 'right' in each respective filenames. Ex.) stx_neo-0232-2-1-6year_mid_left.vtk and stx_neo-0232-2-1-6year_mid_right.vtk
Optional: An output folder location. This is where a folder called 'Keychains' will be places with all the finished keychains.
If a location is not specified, the same location of the input folder will be used.
"""
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
Neuro Image Research and Analysis Lab, University of North Carolina, Chapel Hill
""" # replace with organization, grant and thanks.

#
# BrainKeyCreatorExtensionWidget
#

class BrainKeyCreatorExtensionWidget(ScriptedLoadableModuleWidget):
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

    # Adds search directory text box
    self.inputDirSelector = ctk.ctkPathLineEdit()
    self.inputDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.inputDirSelector.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.inputDirSelector.settingKey = 'inputDir'
    parametersFormLayout.addRow("Input surface folder (required):", self.inputDirSelector)

    # Adds save directory text box
    self.saveDirSelector = ctk.ctkPathLineEdit()
    self.saveDirSelector.filters = ctk.ctkPathLineEdit.Dirs
    self.saveDirSelector.options = ctk.ctkPathLineEdit.ShowDirsOnly
    self.saveDirSelector.settingKey = 'saveDir'
    parametersFormLayout.addRow("Output folder location (optional):", self.saveDirSelector)


    self.meshScaleFactor = slicer.qMRMLSliderWidget()
    self.meshScaleFactor.decimals = 4
    self.meshScaleFactor.tickInterval = 0.01
    self.meshScaleFactor.singleStep = 0.01
    self.meshScaleFactor.value = 0.25
    self.meshScaleFactor.minimum = 0.0001
    self.meshScaleFactor.maximum = 1.00
    self.meshScaleFactor.setMRMLScene( slicer.mrmlScene )
    self.meshScaleFactor.setToolTip( "The Scaling factor, default 0.25." )
    parametersFormLayout.addRow("Mesh Scale Factor: ", self.meshScaleFactor)
    
    
    self.handleShift = slicer.qMRMLSliderWidget()
    self.handleShift.decimals = 1
    self.handleShift.tickInterval = 1
    self.handleShift.singleStep = 1
    self.handleShift.minimum = -40
    self.handleShift.maximum = 40
    self.handleShift.value = -5
    self.handleShift.setMRMLScene( slicer.mrmlScene )
    self.handleShift.setToolTip( "Z-axis shift of handle." )
    parametersFormLayout.addRow("S-I shift: ", self.handleShift)
    
    #
    # no output volume selector
    #

    #
    # check box to trigger taking screen shots for later use in tutorials
    #
    self.enableScreenshotsFlagCheckBox = qt.QCheckBox()
    self.enableScreenshotsFlagCheckBox.checked = 0
    self.enableScreenshotsFlagCheckBox.setToolTip("If checked, take screen shots for tutorials. Use Save Data to write them to disk.")
    parametersFormLayout.addRow("Enable Screenshots", self.enableScreenshotsFlagCheckBox)

    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the brain key chain generator."
    self.applyButton.enabled = True
    parametersFormLayout.addRow(self.applyButton)

    # connections
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    #self.inputLeft.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.inputRight.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
    #self.searchDir.textChanged.connect(self.onSelect)
        #self.saveDir.textChanged.connect(self.onSelect)
    # self.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    #self.onSelect()

  def cleanup(self):
    pass

    '''
  def onSelect(self):   
    #self.applyButton.enabled = self.inputLeft.currentNode() and self.inputRight.currentNode()
    self.applyButton.enabled = self.searchDir.isModified()
    '''

  def onApplyButton(self):
    logic = BrainKeyCreatorExtensionLogic()
    enableScreenshotsFlag = self.enableScreenshotsFlagCheckBox.checked
    if(len(str(self.saveDirSelector.currentPath)) == 0):
        self.saveDir = os.path.split(str(self.inputDirSelector.currentPath))[0] + '/Keychains/'
    else:
        self.saveDir = str(self.saveDirSelector.currentPath) + '/Keychains/'
    subprocess.call(['mkdir', self.saveDir])
    # leftVTKSearch will be used to place all VTK files that contain 'left'
    # rightVTKSearch will be used to place all VTK files that contain 'right'
    # goodVTKPairs will be used to pair and store matching filenames
    leftVTKSearch = []
    rightVTKSearch = []
    goodVTKPairs = []
    # Load directory with brain surfaces and place into left surface array or right surface array if it is a .vtk file
    for filename in os.listdir(str(self.inputDirSelector.currentPath)):
        if filename[len(filename)-3:] == 'vtk':
            if('left' in filename):
                leftVTKSearch.append(filename)
            else:
                rightVTKSearch.append(filename)
    # Go through all the left surfaces and find the matching right surface, then remove found right surface from array to reduce search time
    for leftEntry in leftVTKSearch:
        removedLeftVTK = leftEntry.replace('left','')
        for rightEntry in rightVTKSearch:
            removedRightVTK = rightEntry.replace('right','')
            if(removedLeftVTK == removedRightVTK):
                goodVTKPairs.append((leftEntry, rightEntry))
                rightVTKSearch.remove(rightEntry)

    # Go through all the found VTK pairs and run the logic on them (and eventually save)
    for entry in goodVTKPairs:
        # Load nodes into scence
        leftInput = slicer.util.loadModel(str(self.inputDirSelector.currentPath) + '/'+entry[0], returnNode=True)[1]
        rightInput = slicer.util.loadModel(str(self.inputDirSelector.currentPath)+ '/' + entry[1], returnNode=True)[1]
        # Create keychain name that will be saved at the end of saveDir file path
        keyChainName = entry[0].replace('.vtk','').replace('left','')
        savedFilePath = str(self.saveDir+keyChainName)
        # Add KeyChain.stl to end of file path so it is easy to differentiate between pre-run files and key chain files
        if(keyChainName[len(keyChainName)-1]=='_'):
            savedFilePath = savedFilePath + "keyChain.stl"
        else:
            savedFilePath = savedFilePath + "_keyChain.stl"
        # Run logic of pair of nodes
        surfNode = logic.run(savedFilePath, leftInput, rightInput, self.meshScaleFactor.value, self.handleShift.value, enableScreenshotsFlag)
        # Write to STL file
        slicer.util.saveNode(surfNode, savedFilePath)
        # Remove nodes after saving for next logic run
        slicer.mrmlScene.RemoveNode(leftInput) 
        slicer.mrmlScene.RemoveNode(rightInput)
        slicer.mrmlScene.RemoveNode(surfNode)



#
# BrainKeyCreatorExtensionLogic
#

class BrainKeyCreatorExtensionLogic(ScriptedLoadableModuleLogic):
  """This class implements the generation of the key chain surface from the brain surfaces
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qimage = ctk.ctkWidgetsUtils.grabWidget(widget)
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(savedFilePath, self, leftVol, rightVol, meshScaleFactor, handleShift, enableScreenshots=0):
    """
    Run the actual algorithm
    """
    logging.info('Processing started')
    
    ############################################
    ############################################
    # Set up the boundary parameters
    ############################################
    ############################################
    
    # left right front back bottom top
    leftData = leftVol.GetPolyData().GetPoints().GetBounds()
    rightData = rightVol.GetPolyData().GetPoints().GetBounds()
    leftBound = leftData[0]
    rightBound = rightData[1]
    topBound = max(leftData[5],rightData[5])
    bottomBound = min(leftData[4], rightData[4])            #bottomBound
    frontBound = min(leftData[2],rightData[2])
    backBound = max(leftData[3],rightData[3])
    midline = (leftBound+rightBound)/2
    halfway = -(backBound+frontBound)/1.9
    print(leftBound, rightBound)
    print("Midline:", midline)
    print(frontBound,backBound)
    print("Halfway:", halfway)
    print("Top:", topBound)
    print("Bottom:", bottomBound)                           #bottomBound

    ############################################
    ############################################
    # Generate an empty image as placeholder
    ############################################
    ############################################
    nodeName = "Blank Volume Helper"
    imageSize = [400, 500, 400]
    voxelType=vtk.VTK_UNSIGNED_CHAR
    #this needs to be replaced by the lower left corner of the two surfaces

    imageOrigin = [rightBound,backBound,bottomBound]        #new origin
    imageSpacing = [0.5, 0.5, 0.5]
    imageDirections = [[-1,0,0], [0,-1,0], [0,0,1]]
    fillVoxelValue = 255

    # Create an empty image volume, filled with fillVoxelValue
    imageData = vtk.vtkImageData()
    imageData.SetDimensions(imageSize)
    imageData.AllocateScalars(voxelType, 1)
    thresholder = vtk.vtkImageThreshold()
    thresholder.SetInputData(imageData)
    thresholder.SetInValue(fillVoxelValue)
    thresholder.SetOutValue(fillVoxelValue)
    thresholder.Update()
    # Create volume node
    blankVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", nodeName)
    blankVolumeNode.SetOrigin(imageOrigin)
    blankVolumeNode.SetSpacing(imageSpacing)
    blankVolumeNode.SetIJKToRASDirections(imageDirections)
    blankVolumeNode.SetAndObserveImageData(thresholder.GetOutput())
    blankVolumeNode.CreateDefaultDisplayNodes()
    blankVolumeNode.CreateDefaultStorageNode()
    logging.info('Created empty volume for brain surface labelmap')

    print("Handle Shift: ", handleShift)
    print("Mesh Scaling Factor: ", meshScaleFactor)
    

    def makeHandle():
        fn = vtk.vtkParametricTorus()
        fn.SetRingRadius((rightBound-leftBound)/5)
        fn.SetCrossSectionRadius((rightBound-leftBound)/15)
        #vtk.FlipNormalsOn()
        source = vtk.vtkParametricFunctionSource()
        source.SetParametricFunction(fn)
        source.Update()

        trans = vtk.vtkTransform()
        trans.RotateX(90)
        trans.Translate(midline,topBound + handleShift,halfway)
        # vtk generate normals
        # communicate with SLACK
        rotate = vtk.vtkTransformPolyDataFilter()
        rotate.SetTransform(trans)
        rotate.SetInputConnection(source.GetOutputPort())
        rotate.Update()

        return rotate.GetOutput()

    leftBLM = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "leftBLM")
    # leftBLM.CreateDefaultDisplayNodes()
    # leftBLM.CreateDefaultStorageNode()

    rightBLM = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "rightBLM")
    # rightBLM.CreateDefaultDisplayNodes()
    # rightBLM.CreateDefaultStorageNode()

    handleBLM = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "handleBLM")
    # handleBLM.CreateDefaultDisplayNodes()
    # handleBLM.CreateDefaultStorageNode()
    
    ############################################
    ############################################
    # Make the handle surface
    ############################################
    ############################################
    
    handle = makeHandle()
    handleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', "handle")
    handleNode.SetAndObservePolyData(handle)
    handleNode.CreateDefaultDisplayNodes()
    handleNode.CreateDefaultStorageNode()
    
    ############################################
    ############################################
    # Convert the surfaces and the handle to images
    ############################################
    ############################################
    
    handleParams = {'reference' : blankVolumeNode.GetID(), 'mesh' : handleNode.GetID(), 'labelMap': handleBLM.GetID(), 'value' : 255}
    process = slicer.cli.run(slicer.modules.meshtolabelmap, None, handleParams, wait_for_completion=True)
    #print(process)
    
    leftParams = {'sampleDistance' : 0.1, 'InputVolume' : blankVolumeNode.GetID(), 'surface' : leftVol.GetID(), 'OutputVolume': leftBLM.GetID()}
    process = slicer.cli.run(slicer.modules.modeltolabelmap, None, leftParams, wait_for_completion=True)

    rightParams = {'sampleDistance' : 0.1, 'InputVolume' : blankVolumeNode.GetID(), 'surface' : rightVol.GetID(), 'OutputVolume': rightBLM.GetID()}
    process = slicer.cli.run(slicer.modules.modeltolabelmap, None, rightParams, wait_for_completion=True)
    
    
    ############################################
    ############################################
    # Save surfaces and then load via simpleITK
    ############################################
    ############################################
    
    path = slicer.util.tempDirectory("saves")
    leftPath = path + "/left.nrrd"
    rightPath = path + "/right.nrrd"
    handlePath = path + "/handle.nrrd"

    slicer.util.saveNode(leftBLM,leftPath)
    slicer.util.saveNode(rightBLM,rightPath)
    slicer.util.saveNode(handleBLM,handlePath)

    left = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(leftBLM.GetName()))
    right = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(rightBLM.GetName()))
    handleVol = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(handleBLM.GetName()))
    
    ############################################
    ############################################
    # Use simpleITK to combine, smooth and fill holes
    ############################################
    ############################################
    
    orFilter = sitk.OrImageFilter()
    brain = orFilter.Execute(right,left)
    or2Filter = sitk.OrImageFilter()
    keychain = or2Filter.Execute(brain,handleVol)

    dilateFilter = sitk.BinaryDilateImageFilter()
    #rad = round((rightBound-leftBound)/30)
    #print("DilationRadius:", rad)
    dilateFilter.SetKernelRadius(2)
    dilateFilter.SetBackgroundValue(0)
    dilateFilter.SetForegroundValue(255)
    print(dilateFilter.GetKernelType(), dilateFilter.GetKernelRadius())

    keychain_dilated = dilateFilter.Execute(keychain)

    holesFilter = sitk.BinaryFillholeImageFilter()
    keychain_dilated_fixed = holesFilter.Execute(keychain_dilated, True, 255)

    
    keychainNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLLabelMapVolumeNode', "keyChainLabel")
    keychainNode.CreateDefaultDisplayNodes()
    keychainNode.CreateDefaultStorageNode()
    
    sitkUtils.PushVolumeToSlicer(keychain_dilated_fixed, keychainNode)
    
    ############################################
    ############################################
    # Generate surface from the combined image
    ############################################
    ############################################
    
    modelHierarchyNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelHierarchyNode', "keychainHierarchy")
    surfParams = {'InputVolume' : keychainNode.GetID(), 'Name' : 'KeyChain', 'SkipUnNamed' : False, 'ModelSceneFile' : modelHierarchyNode.GetID()}
    process = slicer.cli.run(slicer.modules.modelmaker, None, surfParams, wait_for_completion=True)
    
    
    ############################################
    ############################################
    # Reduce size by factor meshScaleFactor
    ############################################
    ############################################
    
    transform = slicer.vtkMRMLLinearTransformNode()
    slicer.mrmlScene.AddNode(transform)
    vTransform = vtk.vtkTransform()
    vTransform.Scale(meshScaleFactor,meshScaleFactor,meshScaleFactor)
    transform.SetAndObserveMatrixTransformToParent(vTransform.GetMatrix())
    
    surfNodeCollection = slicer.mrmlScene.GetNodesByName("KeyChain_255_mambazo")
    numberNodes = surfNodeCollection.GetNumberOfItems()
    surfNode = surfNodeCollection.GetItemAsObject(numberNodes - 1)
    surfNode.SetAndObserveTransformNodeID(transform.GetID())
    
    logic = slicer.vtkSlicerTransformLogic()
    logic.hardenTransform(surfNode)
    
    ############################################
    ############################################
    # Clean up a bit
    ############################################
    ############################################
    
    slicer.mrmlScene.RemoveNode(leftBLM)
    slicer.mrmlScene.RemoveNode(rightBLM)
    slicer.mrmlScene.RemoveNode(handleBLM)
    slicer.mrmlScene.RemoveNode(transform)
    slicer.mrmlScene.RemoveNode(handleNode)
    
    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('BrainKeyCreatorExtensionTest-Start','MyScreenshot',-1)


    logging.info('Processing completed')

    return surfNode


class BrainKeyCreatorExtensionTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_BrainKeyCreatorExtension1()

  def test_BrainKeyCreatorExtension1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """


    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    nodeName = "BlankVolume"
    imageSize = [390, 466, 318]
    voxelType=vtk.VTK_UNSIGNED_CHAR
    imageOrigin = [98, 98, -72]
    imageSpacing = [0.5, 0.5, 0.5]
    imageDirections = [[-1,0,0], [0,-1,0], [0,0,1]]
    fillVoxelValue = 255
    # Create an empty image volume, filled with fillVoxelValue
    imageData = vtk.vtkImageData()
    imageData.SetDimensions(imageSize)
    imageData.AllocateScalars(voxelType, 1)
    thresholder = vtk.vtkImageThreshold()
    thresholder.SetInputData(imageData)
    thresholder.SetInValue(fillVoxelValue)
    thresholder.SetOutValue(fillVoxelValue)
    thresholder.Update()
    # Create volume node
    blankVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", nodeName)
    blankVolumeNode.SetOrigin(imageOrigin)
    blankVolumeNode.SetSpacing(imageSpacing)
    blankVolumeNode.SetIJKToRASDirections(imageDirections)
    blankVolumeNode.SetAndObserveImageData(thresholder.GetOutput())
    blankVolumeNode.CreateDefaultDisplayNodes()
    blankVolumeNode.CreateDefaultStorageNode()
    logging.info('Created empty volume Blank Volume')

    def makeHandle():
        fn = vtk.vtkParametricTorus()
        fn.SetRingRadius(20)
        fn.SetCrossSectionRadius(7)

        source = vtk.vtkParametricFunctionSource()
        source.SetParametricFunction(fn)
        source.Update()

        trans = vtk.vtkTransform()
        trans.RotateX(90)
        trans.Translate(-8,52,25)
        rotate = vtk.vtkTransformPolyDataFilter()
        rotate.SetTransform(trans)
        rotate.SetInputConnection(source.GetOutputPort())
        rotate.Update()

        return rotate.GetOutput()

    handleNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', "handle")
    handle = makeHandle()

    handleNode.SetAndObservePolyData(handle)
    handleNode.CreateDefaultDisplayNodes()
    handleNode.CreateDefaultStorageNode()


    self.delayDisplay('Test passed!')
