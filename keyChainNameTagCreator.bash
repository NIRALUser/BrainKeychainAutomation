#!/bin/bash
cd /Users/christiannell/desktop/research/NIRAL/fullAutomation
saveDir="Nametags"
openSCAD_file="keyChainTitle.scad"
nameTagInputDir="Priority4"
subStr=""
declare -a doneTags
mkdir $saveDir
cd $nameTagInputDir
for FILE in *.vtk; 
	do (
		echo 
		if [ "${FILE:0:7}" == "stx_neo" ]; then 
			pat="([^neo]*)-([^-]*)"
			[[ $FILE =~ $pat ]]	
			subStr="${BASH_REMATCH[1]}"
			subStr=${subStr:1}
			echo $subStr
		elif [ "${FILE:0:11}" == "stx_noscale" ]; then
			subStr="${FILE:12:6}"
			echo $subStr
			echo hi
		elif [ "${FILE:0:4}" == "stx_" ]; then
			pat="([^_]*)-([^-]*)"
			[[ $FILE =~ $pat ]]	
			subStr="${BASH_REMATCH[1]}"
			echo $subStr
		fi
		cd ..
		/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD -o "${saveDir}/${subStr}.stl" $openSCAD_file -D "input=\"$subStr\"" -D "length=12"
		cd $nameTagInputDir
	);done

