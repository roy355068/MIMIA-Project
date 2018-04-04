import SimpleITK as sitk
import sys
import os
import time

class NeighborhoodConnectedSegmentation:
    def __init__(self, iters):
        self.iters = iters
        self.times = []

    def preprocess(self):
        pass

    def run(self):
        # 103, 104, 106, 108 contains the lungs in the image
        # 103 is bright but has an unknown structure blocks most of the area of the lungs
        # 104 got the brightest and clean image, so I use it to test my solution
        # for i in [103, 104, 106, 108]:
        # for i in [104]:
        basePath = "/Users/tommylin/MIMIA/bochengl/Project/subset0/1.3.6.1.4.1.14519.5.2.1.6279.6001.109002525524522225658609808059.mhd"

        reader = sitk.ImageFileReader()
        reader.SetFileName(basePath)
        # reader.SetFileName( sys.argv[1] )
        # reader.SetFileName(basePath + "000" + str(i) + ".dcm")
        image = reader.Execute()

        blurFilter = sitk.CurvatureFlowImageFilter()
        blurFilter.SetNumberOfIterations( 5 )
        blurFilter.SetTimeStep( 0.125 )
        image = blurFilter.Execute( image )

        # size = image.GetSize()
        # totalPixels = size[0] * size[1]
        # totalVal = 256 * totalPixels

        ### Rescale the image into 8 bits representation
        rescaleFilter = sitk.RescaleIntensityImageFilter()
        rescaleFilter.SetOutputMaximum(255)
        rescaleFilter.SetOutputMinimum(0)
        image = rescaleFilter.Execute(image)
        # sitk.Show(image)

        ### Iteratively compute the Optimal Thresholding
        # prevThreshold = 0.0
        # currThreshold = 140.0
        # while abs(prevThreshold - currThreshold) > 1e-6:
        #
        #     binaryFilter = sitk.BinaryThresholdImageFilter()
        #     binaryFilter.SetLowerThreshold(currThreshold)
        #     binaryFilter.SetInsideValue(0)
        #     binaryFilter.SetOutsideValue(255)
        #     image = binaryFilter.Execute(image)
        #
        #     brightPixel = float(sum(image > currThreshold))
        #     darkPixel = float(sum(image <= currThreshold))
        #     muBody = brightPixel / float(totalPixels)
        #     muNonBody = darkPixel / float(totalPixels)
        #
        #     prevThreshold = currThreshold
        #     currThreshold = 256 * float(muBody + muNonBody) / 2.0
        #     print(prevThreshold, currThreshold)


        binaryFilter = sitk.BinaryThresholdImageFilter()
        binaryFilter.SetLowerThreshold(128)
        binaryFilter.SetInsideValue(0)
        binaryFilter.SetOutsideValue(255)
        image = binaryFilter.Execute(image)
        # sitk.Show(image)


        # # NeighborhoodConnectedImageFilter for remove every white pixels on the border
        # # or connected to a pixel that is on the border.
        neighborFilter = sitk.ConnectedThresholdImageFilter()
        neighborFilter.AddSeed((466, 249, 111))
        neighborFilter.AddSeed((281, 206, 111))
        neighborFilter.AddSeed((229, 361, 90))
        neighborFilter.AddSeed((473, 51, 0))
        neighborFilter.AddSeed((483, 461, 0))
        neighborFilter.AddSeed((30, 80, 0))
        neighborFilter.AddSeed((26, 437, 0))

        # neighborFilter.AddSeed((483, 116, 0))
        # neighborFilter.AddSeed((27,457,0))

        # neighborFilter.AddSeed((153, 168, 0))
        # neighborFilter.AddSeed((348, 180,0))
        neighborFilter.SetReplaceValue(255)
        neighborFilter.SetLower(120)
        neighborFilter.SetUpper(255)
        seg1 = neighborFilter.Execute(image)

        subtractFilter = sitk.SubtractImageFilter()
        image = subtractFilter.Execute(image, seg1)
        sitk.Show(image)

        ### Dilate
        dilateFilter = sitk.DilateObjectMorphologyImageFilter()
        dilateFilter.SetKernelRadius(4)
        dilateFilter.SetObjectValue(255)
        dilateFilter.SetKernelType(1)

        ### Erode
        erodeFilter = sitk.ErodeObjectMorphologyImageFilter()
        erodeFilter.SetKernelRadius(4)
        erodeFilter.SetObjectValue(255)
        erodeFilter.SetKernelType(1)

        ### Hole filling
        holeFillingFilter = sitk.VotingBinaryIterativeHoleFillingImageFilter()
        holeFillingFilter.SetRadius(4)
        holeFillingFilter.SetBackgroundValue(0)
        holeFillingFilter.SetForegroundValue(255)
        holeFillingFilter.SetMaximumNumberOfIterations(5)

        image = dilateFilter.Execute(image)
        image = holeFillingFilter.Execute(image)
        image = erodeFilter.Execute(image)
        sitk.Show(image)

        ## Write out the result
        # writer = sitk.ImageFileWriter()
        # writer.SetFileName( "result.mha" )
        # writer.Execute(image)

        # ### Relabel
        # # Relabel the components and discard the smaller non-body area, which would be
        # # airway.
        # relabelFilter = sitk.RelabelComponentImageFilter()
        # relabelFilter.SetMinimumObjectSize(600)
        # image = relabelFilter.Execute(image)
        # # Extract the objects
        # binaryFilter = sitk.BinaryThresholdImageFilter()
        # binaryFilter.SetLowerThreshold(1)
        # binaryFilter.SetInsideValue(255)
        # binaryFilter.SetOutsideValue(0)
        # image = binaryFilter.Execute(image)
        # sitk.Show(image)
