ROOTDIR="/nfs/qnap/data/uPython/pycom/build"
UPYDIR="pycom-micropython-sigfox"

## INSTALL PYCOM-IDF
cd $ROOTDIR
git clone --recursive https://github.com/pycom/pycom-esp-idf.git
cd pycom-esp-idf
git submodule update --init
export IDF_PATH=$ROOTDIR/pycom-esp-idf

## INSTALL MICROPYTHON
cd $ROOTDIR
rm -rf $UPYDIR
git clone --recursive https://github.com/pycom/pycom-micropython-sigfox.git
cd $UPYDIR
git submodule update --init
ln -rs $ROOTDIR/GNUmakefile $ROOTDIR/$UPYDIR/esp32/GNUmakefile


## INSTALL XTENSA
cd $ROOTDIR
rm -rf xtensa-esp32-elf
# XFN="xtensa-esp32-elf-linux64-1.22.0-61-gab8375a-5.2.0.tar.gz"
XFN="xtensa-esp32-elf-osx-1.22.0-61-gab8375a-5.2.0.tar.gz"
curl -O https://dl.espressif.com/dl/$XFN
tar -xzf $XFN
rm -rf $XFN

# export PATH=$PATH:/nfs/qnap/data/uPython/build/common/xtensa-esp32-elf/bin

## BUILD
cd "$ROOTDIR/$UPYDIR"
make -C mpy-cross

cd "$ROOTDIR/$UPYDIR/esp32"
osxcln # Cleanup OSX ._DS files.

## Edit the pins.csv file.
mv boards/WIPY/pins.csv boards/WIPY/pins.csv.orig 
cp -rp $ROOTDIR/pins.csv boards/WIPY

#Make the app & bootloader
make BOARD=WIPY -j5 TARGET=boot
make BOARD=WIPY -j5 TARGET=app

## Erase & Flash
skill /dev/tty.SLAB_USBtoUART
make BOARD=WIPY -j5 erase ESPPORT=/dev/tty.SLAB_USBtoUART
make BOARD=WIPY -j5 flash ESPPORT=/dev/tty.SLAB_USBtoUART ESPFLASHMODE=dio

