#!/bin/bash

# Initialize the submodules regardless of mode
git submodule init
git submodule update

function interactive {
    # This script is for preparing the application for running in any mode
    pip3 install --user -r requirements.txt
}

function docker {
    mkdir -p bin

    # Make sure bin has all the executables
    # 1. Make sure ffmpeg and ffprobe exist
    if [ -f "bin/ffmpeg" ] && [ -f "bin/ffprobe" ]; then
        echo "FFmpeg and FFprobe binaries exist"
    else
        echo "Didn't find ffmpeg and/or ffprobe in bin, downloading"

        # Delete the existing binaries
        rm -f bin/ffmpeg
        rm -f bin/ffprobe

        cd bin
        
        curl -o "ffmpeg.tar.xz" "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        tar -xf "ffmpeg.tar.xz"

        rm ffmpeg.tar.xz

        echo "Moving ffmpeg executables to bin"
        cd */.
        mv ffmpeg ../
        mv ffprobe ../
        rm -rf *

        echo "Cleaning up... (There should be some failure messages)"
        cd ..
        rmdir *
        chmod 700 ffmpeg ffprobe

        cd ..
    fi

    # Make sure rclone exists
    if [ -f "bin/rclone" ]; then
        echo "Rclone binaries exist"
    else
        echo "Didn't find rclone in bin, downloading"
        
        cd bin

        curl -o "rclone.zip" "https://downloads.rclone.org/rclone-current-linux-amd64.zip"
        unzip rclone.zip
        rm rclone.zip

        echo "Moving rclone executable to bin"
        cd */.
        mv rclone ../
        rm -rf *

        echo "Cleaning up... (There should be some failure messages)"
        cd ..
        rmdir *
        chmod 700 rclone

        cd ..
    fi
}

function helper {
    echo "Run the script with one of the following args: "
    echo "interactive || i || docker || d"
}

case "$1" in

    "interactive"|"i")
        interactive
        ;;
    
    "docker"|"d")
        docker
        ;;
    
    "help"|"h")
        helper
        ;;
    
    *)
        helper
        ;;

esac