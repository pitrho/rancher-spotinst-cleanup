#!/bin/bash

ZIP_NAME='lambda_function.zip'

# Crete the build directory
rm $ZIP_NAME
rm -rf build
mkdir build

# Copy the sources
cp handler.py build/
cp -r env/lib/python2.7/site-packages/requests* build/

# Create zip directory
cd build
zip -r "../${ZIP_NAME}" *

# clean up
cd ..
rm -rf build
