#!/bin/bash
saveDir="Nametags"
openSCAD_file="keyChainTitle.scad"
nameTagInputDir="Keychains"
subStr=""
declare -a doneTags
mkdir $saveDir
cd $nameTagInputDir
for FILE in *.stl; 
	do (
		if [ "${FILE:0:7}" == "stx_neo" ]; then 
			pat="([^neo]*)-([^-]*)"
			[[ $FILE =~ $pat ]]	
			subStr="${BASH_REMATCH[1]}"
			subStr=${subStr:1}
			echo $subStr
		elif [ "${FILE:0:11}" == "stx_noscale" ]; then
			subStr="${FILE:12:6}"
			echo $subStr
		elif [ "${FILE:0:15}" == "stx_stx_noscale" ]; then
			subStr="${FILE:16:6}"
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
