#!/bin/sh

cd meta
mkdir -p usr/lib/enigma2/python/Plugins/Extensions/E2Sudoku
cp -r ../E2Sudoku/* usr/lib/enigma2/python/Plugins/Extensions/E2Sudoku
tar -cvzf data.tar.gz usr
tar -cvzf control.tar.gz control

version=$(grep Version control|cut -d " " -f 2)
package=$(grep Package control|cut -d " " -f 2|tr "A-Z" "a-z")

rm -f ../${package}_${version}_all.ipk
ar -r ../${package}_${version}_all.ipk debian-binary control.tar.gz data.tar.gz

rm -fr control.tar.gz data.tar.gz usr
