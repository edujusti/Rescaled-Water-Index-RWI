Welcome.

This page contains the Python and JavaScript (Google Earth Engine) scripts used for data production, statistical analyses, and result visualization of the RWI spectral index.

Spectral information for the sample points can be generated using the script ExportRandomPoints.js, which references the following image datasets available in Google Earth Engine:
• COPERNICUS/S2_SR_HARMONIZED/20210605T131249_20210605T131243_T23KLP
• COPERNICUS/S2_SR_HARMONIZED/20210613T132231_20210613T132548_T22JFS
• COPERNICUS/S2_SR_HARMONIZED/20210613T132231_20210613T132548_T22JGQ
• COPERNICUS/S2_SR_HARMONIZED/20210613T132231_20210613T132548_T22JDM
• COPERNICUS/S2_SR_HARMONIZED/20210617T135119_20210617T135609_T21HUB
• COPERNICUS/S2_SR_HARMONIZED/20210607T143731_20210607T144845_T19HBD

The file ImageStatsResult.js presents the statistical processing results of the sample data.

The file RWI_MNDWI_comparison.js shows a comparison between the RWI and MNDWI indices, calculated for Sentinel-2 and Landsat-9 satellites for selected cities. This file also includes the method for calculating the RWI using Google Earth Engine.

It is strongly recommended to calculate the adjustment factor. However, if it is not possible to calculate the adjustment factor, values between 4 and 6 can be considered as divisors.
