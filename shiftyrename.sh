#!/bin/bash
# renames pictures in directory and offsetting the time according to offset
#
# ./shiftyrename /path/to/directory/ OFFSET
# where OFFSET is of the form "Y:m:d H:M:S" (MUST BE IN QUOTES!!)


RENAME_FORMAT="%Y-%m-%d-%H%M%S%%-c.%%e"
NEW_DIR="renamed_pictures"
DIV="========================================"

# go to directory with pictures (first arg)
cd $1
mkdir $NEW_DIR
touch $NEW_DIR/record.txt
shopt -s nocaseglob # makes globs case-insensitive

# JPG files, normal ones
printf "$DIV\n\tNormal JPG Files\n$DIV\n"
exiftool "-testname<createdate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *jpg *jpeg |
    tee -a $NEW_DIR/record.txt
read -rp "Looks OK? [y/N]" INPUT
if [[ $INPUT =~ y(es)?$ ]]
then
    exiftool "-filename<createdate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *jpg *jpeg > /dev/null 2>&1
else
    printf "Not renaming files...\n"
fi

# JPG files, rest of them
printf "\n\n$DIV\n\tOther JPG Files
\t(may not rename properly)\n$DIV\n"

exiftool "-testname<filemodifydate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *jpg *jpeg |
    tee -a $NEW_DIR/record.txt
read -rp "Looks OK? [y/N]" INPUT
if [[ $INPUT =~ y(es)?$ ]]
then
    exiftool "-filename<filemodifydate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *jpg *jpeg > /dev/null 2>&1
else
    printf "Not renaming files...\n"
fi

# M4V files, typically from iPhone camera
printf "$DIV\n\tM4V Files\n$DIV\n"
exiftool "-testname<contentcreatedate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *.m4v |
    tee -a $NEW_DIR/record.txt
read -rp "Looks OK? [y/N]" INPUT
if [[ $INPUT =~ y(es)?$ ]]
then
    exiftool "-filename<contentcreatedate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *.m4v > /dev/null 2>&1
else
    printf "Not renaming files...\n"
fi


###############################################
######### DONT NEED BELOW ANY MORE ############
###############################################

# wait why not above??? I'm going to uncomment below

# PNG files, snapchats and screenshots
printf "$DIV\n\tPNG Files (snapchats and screenshots)\n$DIV\n"
exiftool "-testname<datecreated" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *png |
    tee -a $NEW_DIR/record.txt
read -rp "Looks OK? [y/N]" INPUT
if [[ $INPUT =~ y(es)?$ ]]
then
    exiftool "-filename<datecreated" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *png > /dev/null 2>&1
else
    printf "Not renaming files...\n"
fi

# MOV files, typically from Nikon camera
printf "$DIV\n\tMOV Files\n$DIV\n"
exiftool "-testname<creationdate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *.mov |
    tee -a $NEW_DIR/record.txt
read -rp "Looks OK? [y/N]" INPUT
if [[ $INPUT =~ y(es)?$ ]]
then
    exiftool "-filename<creationdate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *.mov > /dev/null 2>&1
else
    printf "Not renaming files...\n"
fi

# MP4 files, typically from iPhone camera
printf "$DIV\n\tMP4 Files\n$DIV\n"
exiftool "-testname<createdate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *.mp4 |
    tee -a $NEW_DIR/record.txt
read -rp "Looks OK? [y/N]" INPUT
if [[ $INPUT =~ y(es)?$ ]]
then
    exiftool "-filename<createdate" -globalTimeShift "$2" -d "$NEW_DIR/$RENAME_FORMAT" *.mp4 > /dev/null 2>&1
else
    printf "Not renaming files...\n"
fi

shopt -u nocaseglob # makes globs case-sensitive again

printf "$DIV\n\tDone renaming files\n$DIV\n\n"
