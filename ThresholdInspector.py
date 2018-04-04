
from __future__ import print_function
import SimpleITK as sitk
import sys
import os
import time

basePath = "/Users/tommylin/MIMIA/bochengl/Project/subset0/1.3.6.1.4.1.14519.5.2.1.6279.6001.109002525524522225658609808059.mhd"

### Read the image
reader = sitk.ImageFileReader()
reader.SetFileName( basePath )
image = reader.Execute()

seeds = [(173, 265, 58), (87, 275, 58), (222, 275, 82), (419, 288, 82)]

seg = sitk.Image(image.GetSize(), sitk.sitkUInt8)
seg.CopyInformation(image)
for seed in seeds:
    seg[seed] = 1
seg = sitk.BinaryDilate(seg, 4)
print(seg)
### Use LabelStatisticsImageFilter to estimate the thresholds
stats = sitk.LabelStatisticsImageFilter()
stats.Execute(image, seg)
factor = 3
lowerThreshold = float(stats.GetMean(1)-factor*stats.GetSigma(1))
upperThreshold = float(stats.GetMean(1)+factor*stats.GetSigma(1))

print(lowerThreshold, upperThreshold)

minmaxFilter = sitk.MinimumMaximumImageFilter()
minmaxFilter.Execute(image)
print(minmaxFilter.GetMaximum(), minmaxFilter.GetMinimum())
