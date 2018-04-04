# My implementation will take around 2 minutes to run on my Macbook Pro.
# In the part 3, I use the level set segmentation to implement my solution
# First I take the smaller data of ascending aorta to test my parameters, then
# apply the parameters I got to the full-volume data.
# I believe my algorithm does a better job than the expert segmentation in the
# sense that the "wall" won't be broken like the expert one.
#
# The seeds I tested and eventually picked are
# [(128, 144, 151), (162, 153, 89), (209, 150, 173), (133, 38, 49), (95, 83, 64)]
# The parameters I chose are
# RMS = 0.002
# Number of iteration = 1000
# Curvature scaling = 1
# Propagation scaling = 1
#
# Experiments show that increase the number of iterations in ThresholdSegmentationLevelSetImageFilter
# could significantly increase the accuracy of the result, but the runtime and time
# complexity of the filter is roughly O(iter ^ 2).
# When # of iterations exceed a certain value, the result would have no significant
# difference but the runtime will take too much time to complete.
# That "critical round number" is around 200 in the small testing dataset and
# around 1000 in the full volume dataset. So I picked 1000 in my full-volume test
#
# Experiments on the RMS with RMSs = [2, 0.2, 0.02, 0.002, 0.0002] shows that
# the smaller the RMS, the more accurate the result is. The results is basically
# have no significantly visible difference when the RMS = 0.002 and 0.0002,
# so I picked 0.002 as the final RMS in my implementation.
#
# Propagation Scaling and Curvature Scaling don't really affect the results very
# much, hence I keep them as they are like the values in the Level Set notebook

from __future__ import print_function
import SimpleITK as sitk
import sys
import os
import time
import errno

basePath = "/Users/tommylin/MIMIA/bochengl/Project/subset0/1.3.6.1.4.1.14519.5.2.1.6279.6001.109002525524522225658609808059.mhd"

class LevelSetSegmentation:
    def __init__(self, iters):
        self.iters = iters
        self.times = []
        try:
            os.makedirs("LevelSet")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    # Variable: factor, RMS, iteration
    def run(self, iter):
        ### Read the image
        reader = sitk.ImageFileReader()
        reader.SetFileName( basePath )
        image = reader.Execute()

        ### Set up the seeds
        seeds = [(173, 265, 58), (87, 275, 58), (222, 275, 82), (419, 288, 82)]

        seg = sitk.Image(image.GetSize(), sitk.sitkUInt8)
        seg.CopyInformation(image)
        for seed in seeds:
            seg[seed] = 1
        seg = sitk.BinaryDilate(seg, 4)

        ### Use LabelStatisticsImageFilter to estimate the thresholds
        stats = sitk.LabelStatisticsImageFilter()
        stats.Execute(image, seg)
        ###################
        factor = 3
        ###################
        lowerThreshold = float(stats.GetMean(1)-factor*stats.GetSigma(1))
        upperThreshold = float(stats.GetMean(1)+factor*stats.GetSigma(1))

        ### ThresholdSegmentationLevelSetImageFilter
        init_ls = sitk.SignedMaurerDistanceMap(seg, insideIsPositive=True, useImageSpacing=True)
        lsFilter = sitk.ThresholdSegmentationLevelSetImageFilter()
        lsFilter.SetLowerThreshold(lowerThreshold)
        lsFilter.SetUpperThreshold(upperThreshold)
        #######################################
        lsFilter.SetMaximumRMSError(0.002)
        lsFilter.SetNumberOfIterations(iter)
        #######################################
        lsFilter.SetCurvatureScaling(1)
        lsFilter.SetPropagationScaling(1)
        lsFilter.ReverseExpansionDirectionOn()
        ls = lsFilter.Execute(init_ls, sitk.Cast(image, sitk.sitkFloat32))

        ### ConnectedThresholdImageFilter
        segmentationFilter = sitk.ConnectedThresholdImageFilter()
        segmentationFilter.SetLower( 0 )
        segmentationFilter.SetUpper( 3 )
        segmentationFilter.SetReplaceValue( 255 )
        for seed in seeds:
            segmentationFilter.AddSeed( seed )

        ### Run the segmentation filter
        image = segmentationFilter.Execute( ls )
        for seed in seeds:
            image[seed] = 255

        ### Write out the result
        writer = sitk.ImageFileWriter()
        writer.SetFileName( "LevelSet/%d.mhd" % iter )
        writer.Execute(image)

if __name__ == "__main__":
    test = LevelSetSegmentation()
    test.run(1000)
