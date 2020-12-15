# Brain Keychain Automation

[Tutorial (ppt)](https://docs.google.com/presentation/d/1Bq0jW6ZUMaFMooyvN8xE0ZmX54jMMEjBkEPmdlKC7bg/edit#slide=id.gae891ae01e_0_3 "Tutorial (ppt)")

## Prerequisites

- Unix, or Unix like environment (includes macOS, not tested on windows).  
- 3D Slicer and openSCAD

## How To

## 1.) keyChainCreator 

### BrainKeyCreatorExtension.py  
- Download [3D Slicer](https://download.slicer.org/ "3D Slicer").  
- Open 3D Slicer and click on the extensions button in the top right corner of the screen (it is blue and right next to the python logo).
- Click 'Install Extensions', then click the search bar in the top right corner.  
- Search 'MeshToLabelMap' then click install (you will need to reload 3D Slicer after installing).  
- Download BrainKeyCreatorExtension.py. Open 3D Slicer again and click on 'edit' at the very top of your screen and then click on 'Application Settings'.  
- Click on 'Modules' and then either click 'Add' and specify where you downloaded the module, or drag the file location into the 'Additional modules' section. 
- Close and then open, or restart 3D Slicer so that the module will load into your extension list.
- To find the module, click on the search bar to the right of 'modules' on the home screen of 3D Slicer and search BrainKeyCreatorExtension.
- You should then be able to load the extension and specify a directory for input surfaces (be sure to follow the example format that is in as a placeholder).
- Click 'Apply' and let the module run. If it says that 3D Slicer is not responding or has a loading icon, do not worry. The module takes roughly 3-5 minutes to render each keychain.  
- After it has finished running you should have a directory called 'Keychains' in the same directory as your input directory.  

## 2.) sceneCreator  

### sceneCreatorModule (sceneCreator.py)
- Download and make sure the file is in the same directory as Keychains. 
- Run sceneCreator.py in a terminal.  
- Specify a print surface width and length. Each keychain should be less than 50 mm in length and width. Each keychain is allocated a 50 mm x 50 mm block on the print surface with an additional 20 mm in length for the nametag. Total, each keychain/nametag combination will an allocated block of 50 mm in width and 70 mm in length.  
- This means if you specify a print surface with a width of 160 mm and length of 150 mm, it will output a 3 x 2 (width x length) field of keychains.
- The script will create keychain/nametag scenes. They will be named 'keyChainScene' + 'some-iteration-number' in a directory called Scenes.

### keyChainNameTagCreator.bash (sceneCreator.py continued)  
- Download keyChainTitle.scad and keyChainNameTagCreator.bash and make sure it is in the same directory as the input surfaces.   
- Also, make sure keyChainTitle.scad is in the same directory.  
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
Or
```bash
stx_stx_noscale_110940_V24_t1w_mid_surface_rsl_left_327680_native_NRRDSpace.vtk
```

* The script will take the substring '0207-1-1', 'T0247-1-1', '241033' and '110940' respectively.  

### keyChainTitle.scad

## 3.) Printing
- Download slicing software such as Ultimaker Cura and open it.
- Drag a print scene into the software and configure the printing setting to how you would like.
- Click slice and let the software add support structures. Then you are ready to print!

## Contributors

Christian Nell, Henry Pehr, Martin Styner (UNC-Chapel Hill)
