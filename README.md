Welcome.

This page contains the Python and JavaScript (Google Earth Engine) scripts used for data production, statistical analyses, and result visualization of the RWI spectral index.

Spectral information for the sample points can be generated using the script ExportRandomPoints.js.The result of the processing in the file samplePointsCities_20240811_harmonized.csv.

The file ImageStatsResult.js presents the statistical processing results of the sample data.

The file RWI_MNDWI_comparison.js shows a comparison between the RWI and MNDWI indices, calculated for Sentinel-2 and Landsat-9 satellites for selected cities. This file also includes the method for calculating the RWI using Google Earth Engine.

It is strongly recommended to calculate the adjustment factor. However, if it is not possible to calculate the adjustment factor, values between 4 and 6 can be considered as divisors.
