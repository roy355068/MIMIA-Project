import SimpleITK as sitk
import sys
import os
import time

import os, errno


basePath = "/Users/tommylin/MIMIA/bochengl/Project/seg-lungs-LUNA16/1.3.6.1.4.1.14519.5.2.1.6279.6001.109002525524522225658609808059.mhd"
# basePath = "/Users/tommylin/MIMIA/bochengl/Project/subset0/1.3.6.1.4.1.14519.5.2.1.6279.6001.109002525524522225658609808059.mhd"
reader = sitk.ImageFileReader()
reader.SetFileName( basePath )
image = reader.Execute()

binaryFilter = sitk.BinaryThresholdImageFilter()
binaryFilter.SetUpperThreshold(0)
binaryFilter.SetInsideValue(0)
binaryFilter.SetOutsideValue(255)
image = binaryFilter.Execute(image)


try:
    os.makedirs("TestFolder")
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

sitk.Show(image)
writer = sitk.ImageFileWriter()
writer.SetFileName( "TestFolder/456.mhd" )
writer.Execute(image)
