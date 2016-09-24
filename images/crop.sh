#!/bin/sh

cropped_dir="cropped"

if [ ! -d $cropped_dir ]; then
    mkdir $cropped_dir
fi

for fname in `ls *.bmp`
do
    newfname="$cropped_dir/$fname"
    echo convert $fname -crop 48x33+0+15 $newfname
    convert $fname -crop 48x33+0+15 $newfname
done

