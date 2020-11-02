# BrainKeychainAutomation

## How To

1.) BrainKeyCreatorExtension.py  
- Download 3D Slicer and the MeshToLabelMap extension (you will need to reload 3D Slicer after doing so).  
- Download BrainKeyCreatorExtension.py. Then click on 'edit' at the top bar when you are in 3D slicer and then 'Application Settings'.  
- Click on 'Modules' and then either click 'Add' and specify where you downloaded the module, or drag the file location into the 'Additional module paths' section.  
- You should then be able to load the extension and specify a directory for input surfaces as well as a directory to save the keychain images in (be sure to follow the example format that is in as a placeholder).  
- Click 'Apply' and let the module run. If it says that 3D Slicer is not responding or has a loading icon, do not worry. The module will take a bit to process.  
- After it has finished running you should have a directory (that you specified) filled with brain keychains  

2.) keyChainNameTagCreator.bash  
- Download keyChainTitle.scad and keyChainNameTagCreator.bash and use a text editor to open the bash file.  
- Change the variable named 'saveDir' to whatever you would like the directory that holds the saved nameags in called.  
- Change the variable named 'nameTagInputDir' to the directory that has the input brain surfaces.  
- Make sure that the 'saveDir', 'nameTagInputDir' and keyChainTitle.scad are all in the same directory.  
- Save and close the text editor. Then click on the keyChainNameTagCreator.bash file.  
- If it says you do not have permission to run this file, you may need to run this command.  

## Contributors

Henry Pehr, Christian Nell, Martin Styner (UNC-Chapel Hill)
