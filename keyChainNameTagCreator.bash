#!/bin/bash
cd /Users/christiannell/desktop/research/NIRAL/fullAutomation
saveDir="Priority3NameTags"
openSCAD_file="keyChainTitle.scad"
nameTagInputDir="Priority3"
subStr=""
declare -a doneTags
mkdir $saveDir
cd $nameTagInputDir
for FILE in *.vtk; 
	do (
		if [ "${FILE:0:7}" == "stx_neo" ]; then 
			pat="([^neo]*)-([^-]*)"
			[[ $FILE =~ $pat ]]	
			subStr="${BASH_REMATCH[1]}"
			subStr=${subStr:1}
			echo $subStr
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
