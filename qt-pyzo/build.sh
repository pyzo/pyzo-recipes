#!/bin/bash

if [ `uname` == Linux ]; then
    
    
    sudo apt-get -y install gcc g++
    sudo apt-get -y install libXext-dev libXrender-dev libX11-dev
    #sudo apt-get -y install libgtk2.0-dev (if enabled gtkstyle seems enabled by default
    sudo apt-get -y install libfontconfig-dev libfreetype6-dev
    sudo apt-get -y install libgl1-mesa-dev libglu1-mesa-dev
    sudo apt-get -y install libz-dev libbz2-dev liblzma-dev lzma-dev
    sudo apt-get -y install libssl-dev libgdb-dev libgdbm-dev libreadline-dev
    sudo apt-get -y install libXml2-dev libXslt-dev

    chmod +x configure
    ./configure \
        -release -fontconfig -continue -verbose \
        -no-qt3support -nomake examples -nomake demos \
        -webkit -qt-libpng -qt-zlib -opengl
    make
    sudo make install
fi

if [ `uname` == Darwin ]; then
    sudo port install qt4-mac
fi
