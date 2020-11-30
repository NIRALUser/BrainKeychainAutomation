# Brain Keychain Automation

## How To

### 1.) BrainKeyCreatorExtension.py  
- Download [3D Slicer](https://download.slicer.org/ "3D Slicer") and the MeshToLabelMap extension (you will need to reload 3D Slicer after doing so).  
- Download BrainKeyCreatorExtension.py. Then click on 'edit' at the top bar when you are in 3D slicer and then 'Application Settings'.  
- Click on 'Modules' and then either click 'Add' and specify where you downloaded the module, or drag the file location into the 'Additional modules section.  
- You should then be able to load the extension and specify a directory for input surfaces (be sure to follow the example format that is in as a placeholder).  
- Click 'Apply' and let the module run. If it says that 3D Slicer is not responding or has a loading icon, do not worry. The module will take a bit to process.  
- After it has finished running you should have a directory called keychains in the same directory as your input directory.  

### 3.) sceneCreator.py
- Download and make sure the file is in the same directory as Keychains and Nametags.  
- Run sceneCreator.py in a terminal.  
- It will create keychain/nametag scenes with up to 6 matches in each scene. They will be named 'keyChainScene' + 'some-iteration-number' in a directory called Scenes.

### 3.) keyChainNameTagCreator.bash  
- Download keyChainTitle.scad and keyChainNameTagCreator.bash and make sure it is in the same directory as the input surfaces.   
- Also make sure keyChainTitle.scad is in same directory.  
- Then click on the keyChainNameTagCreator.bash file.  
- If it says you do not have permission to run this file, you may need to run this command in the directory with the Bash file.  
```bash
chmod 755 keyChainNameTagCreator.bash 
```
- If that does not work then run another chmod command that will give your device permission to run the executable.  
- After it is done running you will have a directory containing nametags with a substring title based on the surface filename.  

**Note**  

* The surface filename needs to be in one of the following example formats to work.  
```bash
stx_neo-0207-1-1-1year-mid_left.vtk  
```
Or
```bash
stx_T0247-1-1-4year_mid_right.vtk  
```
Or
```bash
stx_noscale_241033_V06_t1w_RAI_mid_left.vtk
```
or
```bash
stx_stx_noscale_110940_V24_t1w_mid_surface_rsl_left_327680_native_NRRDSpace.vtk
```

* The script will take the substring '0207-1-1' in the first example and 'T0247-1-1' in the second.  
* Also, the first couple of commands are changing the directory in the script to the one where all the files are. These 'cd' commands will need a different working directory location than what is there now (the one in there now is the location of the files on my device).  

### 4.) Printing
- Download slicing software such as Ultimaker Cura and open it.
- Drag a print scene into the software and configure the printing setting to how you would like.
- Click slice and let the software add support structures. Then you are ready to print!

## Contributors

Christian Nell, Henry Pehr, Martin Styner (UNC-Chapel Hill)
