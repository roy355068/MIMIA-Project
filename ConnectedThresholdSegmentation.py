
import SimpleITK as sitk
import sys
import os
import time
import errno
basePath = "/Users/tommylin/MIMIA/bochengl/Project/subset0/1.3.6.1.4.1.14519.5.2.1.6279.6001.109002525524522225658609808059.mhd"
class ConnectedThresholdSegmentation:
    def __init__(self, iters = []):
        self.iters = iters
        self.iterToTimes = {}

        try:
            os.makedirs("ConnectedThreshold")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def preprocess(self):

        reader = sitk.ImageFileReader()
        reader.SetFileName(basePath)
        image = reader.Execute()

        blurFilter = sitk.CurvatureFlowImageFilter()
        blurFilter.SetNumberOfIterations( 5 )
        blurFilter.SetTimeStep( 0.125 )
        image = blurFilter.Execute( image )

        ### Rescale the image into 8 bits representation
        rescaleFilter = sitk.RescaleIntensityImageFilter()
        rescaleFilter.SetOutputMaximum(255)
        rescaleFilter.SetOutputMinimum(0)
        image = rescaleFilter.Execute(image)

        binaryFilter = sitk.BinaryThresholdImageFilter()
        binaryFilter.SetLowerThreshold(128)
        binaryFilter.SetInsideValue(0)
        binaryFilter.SetOutsideValue(255)
        image = binaryFilter.Execute(image)

        # ConnectedThresholdImageFilter for remove every white pixels on the border
        # or connected to a pixel that is on the border.
        neighborFilter = sitk.ConnectedThresholdImageFilter()
        seeds = [(173, 265, 58), (87, 275, 58), (222, 275, 82), (419, 288, 82)]
        for seed in seeds:
            neighborFilter.AddSeed(seed)

        neighborFilter.SetReplaceValue(255)
        neighborFilter.SetLower(120)
        neighborFilter.SetUpper(255)
        image = neighborFilter.Execute(image)

        return image

    # The parameters here are SetKernelRadius and SetMaximumNumberOfIterations
    def run(self, image, iter, kernelRadius = 4):
        ### Dilate
        dilateFilter = sitk.DilateObjectMorphologyImageFilter()
        dilateFilter.SetKernelRadius(kernelRadius)
        dilateFilter.SetObjectValue(255)
        dilateFilter.SetKernelType(1)

        ### Erode
        erodeFilter = sitk.ErodeObjectMorphologyImageFilter()
        erodeFilter.SetKernelRadius(kernelRadius)
        erodeFilter.SetObjectValue(255)
        erodeFilter.SetKernelType(1)

        ### Hole filling
        holeFillingFilter = sitk.VotingBinaryIterativeHoleFillingImageFilter()
        holeFillingFilter.SetMajorityThreshold(5)
        holeFillingFilter.SetRadius(kernelRadius)
        holeFillingFilter.SetBackgroundValue(0)
        holeFillingFilter.SetForegroundValue(255)
        ###################################################
        holeFillingFilter.SetMaximumNumberOfIterations(iter)
        ###################################################

        tempImage = dilateFilter.Execute(image)
        tempImage = holeFillingFilter.Execute(tempImage)
        tempImage = erodeFilter.Execute(tempImage)

        writer = sitk.ImageFileWriter()
        writer.SetFileName( "ConnectedThreshold/%d.mhd" % iter )
        writer.Execute(tempImage)

if __name__ == "__main__":
    test = ConnectedThresholdSegmentation()
    tempImage = test.preprocess()
    test.run(tempImage, 1)
