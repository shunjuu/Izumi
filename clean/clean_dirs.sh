#!/bin/bash

SRC="/media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public"
AUTO="/media/9da3/rocalyte/private/rtorrent/data/Public"

cd $SRC

# Clean out ruTorrent
cd .Nyaa
rmdir ./*
cd ..

# Clean NyaaKV
cd NyaaKV
rmdir ./*
cd ..

# Clean NyaaKV
cd Nyaa4
rmdir ./*
cd ..

cd $AUTO

# Clean out .Nyaa
cd .Nyaa
rmdir ./*
cd ..
