#!/bin/bash

SRC="/media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public"
AUTO="/media/9da3/rocalyte/private/rtorrent/data/"

cd $SRC

# Clean out ruTorrent
cd .Nyaa
rmdir ./*
cd ..

# Clean NyaaKV
cd NyaaKV
rmdir ./*
cd ..

# Clean Nyaa4
cd Nyaa4
rmdir ./*
cd ..

cd $AUTO

# Clean out all folders in data/
rmdir ./*
