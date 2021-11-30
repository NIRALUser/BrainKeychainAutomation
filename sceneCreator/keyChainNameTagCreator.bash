#!/bin/bash
OpenSCADDir=$1
openSCAD_file=$2
inputDir=$3
length=$4
#length=$(($inputlength + 1 - 1))
saveName="/Nametags"
saveDir="$inputDir$saveName"
nameTagInputDir="Keychains"
subStr=""
declare -a doneTags
cd $inputDir
mkdir "Nametags"
cd $nameTagInputDir
echo doing Nametags $length $inputlength
for FILE in *.stl; 
	do (
	  #echo $FILE
		if [ "${FILE:0:7}" == "stx_neo" ]; then 
			pat="([^neo]*)-([^-]*)"
			[[ $FILE =~ $pat ]]	
			subStr="${BASH_REMATCH[1]}"
			subStr=${subStr:1}
			echo 1 $subStr
		elif [ "${FILE:0:11}" == "stx_noscale" ]; then
			subStr="${FILE:12:$length}"
			echo 2 $subStr
		elif [ "${FILE:0:15}" == "stx_stx_noscale" ]; then
			subStr="${FILE:16:$length}"
			echo 3 $subStr
		elif [ "${FILE:0:4}" == "stx_" ]; then
			#pat="([^_]*)-([^-]*)"
			subStr="${FILE:4:$length}"
			#echo 4 $subStr
    else
      pat="(^[^_]+)"
      [[ $FILE =~ $pat ]]
      subStr="${BASH_REMATCH[1]}"
      echo 5 $subStr
		fi
		cd ..
		$OpenSCADDir -o "${saveDir}/${subStr}.stl" $openSCAD_file -D "input=\"$subStr\"" -D "length=12"
		cd $nameTagInputDir
	);done
