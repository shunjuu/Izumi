#!/bin/bash

SRC="/home/izumi/izumi"

cd $SRC

# Clean NyaaKV
cd NyaaKV
rmdir ./*
cd ..

# Clean Nyaa4
cd Nyaa4
rmdir ./*
cd ..

# Clean .NyaaV2
cd NyaaV2
rmdir ./*
cd ..

