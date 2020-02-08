#!/bin/bash

# Loads all the binaries needed for core modules.

# If the rclone binaries all already exist, skip
if [ -f "acquisition/bin/rclone" ] && [ -f "distributor/bin/rclone" ] && [ -f "encoder/bin/rclone" ]; then
    echo "Rclone binaries already exist."
else
    echo "Rclone binaries are missing, downloading"

    mkdir bin
    cd bin

    curl -o "rclone.zip" "https://downloads.rclone.org/rclone-current-linux-amd64.zip"
    unzip rclone.zip
    rm rclone.zip

    echo "Moving rclone to bins"
    cd */.
    mv rclone ../
    rm -rf *

    cd ../..
    chmod 755 bin/rclone
    cp bin/rclone acquisition/bin
    cp bin/rclone distributor/bin
    cp bin/rclone encoder/bin

    echo "Cleaning up"
    rm -rf bin/
fi

# Now handle ffmpeg
if [ -f "encoder/bin/ffmpeg" ]; then
    echo "Ffmpeg binary already exist"
else
    echo "Didn't find ffmpeg in bin, downloading."

    cd encoder/bin

    curl -o "ffmpeg.tar.xz" "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
    tar -xf "ffmpeg.tar.xz"
    rm ffmpeg.tar.xz

    cd */.
    mv ffmpeg ../
    rm -rf *

    echo "Cleaning up (there may be some error messages)"
    cd ..
    rmdir *
    chmod 755 ffmpeg

    cd ../..
fi



