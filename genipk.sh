#!/bin/sh

cd meta
mkdir -p usr/lib/enigma2/python/Plugins/Extensions/E2Sudoku
cp -r ../E2Sudoku/* usr/lib/enigma2/python/Plugins/Extensions/E2Sudoku
tar -cvzf data.tar.gz usr
tar -cvzf control.tar.gz control

rm -f ../e2sudoko_0.1_all.ipk
ar -r ../e2sudoko_0.1_all.ipk debian-binary control.tar.gz data.tar.gz

rm -fr control.tar.gz data.tar.gz usr
