#WaterMe Feeder

This is the data processing and loading code from the WaterMe project at #RHoKSoton.

**Aim**: To make contemporary NDWI data available over the internet and to provide an API to allow further visualisations of the dataset 

##Summary

MODIS data is collected on every region of the globe twice daily by a pair of satellites, we pick the images from the Terra satellite which provides images taken at 10.30 am, this was selected to give the best quality results. 

The MODIS data is available via FTP as a series of files, 3 files for each day: a JPG of visible light, an xml file, and an HDF file that stores data specifc to wavelength bands. We use bandFive and bandTwo to calculate an NDWI value, this value is a good estimate of the amount of water present in vegetation, and therefore a good indicator of the effect of water shortages.

An API allows for 3rd parties to develop their own visualisations of the NDWI data. Please see the WaterMe project for the API and user interface.

##Installation

Requirements:
 
* MODIS Reprojection Tool https://lpdaac.usgs.gov/tools/modis_reprojection_tool
* Java (as required by the MRT above)
* Python (to run this code) with the following modules:
	* gdal
	* pymysql
	* numpy
* A MySQL database with write permissions

You will need to fill in the paths and DB parameters at the top of the process.py file to get it to work on your system.

The table you will need must be as below:

```SQL
CREATE TABLE IF NOT EXISTS `Data` (
	`ID` int(11) NOT NULL AUTO_INCREMENT,
	`latitude` DECIMAL(8, 4) NOT NULL,
	`longitude` DECIMAL(8,4) NOT NULL,
	`bandOne` int(5) NOT NULL,
	`bandTwo` int(5) NOT NULL,
	`bandThree` int(5) NOT NULL,
	`bandFour` int(5) NOT NULL,
	`bandFive` int(11) NOT NULL,
	`bandSix` int(11) NOT NULL,
	`bandSeven` int(11) NOT NULL,
	`vegetation` float NOT NULL,
	`cloud` tinyint(1) NOT NULL,
	`NDWI` float NOT NULL,
	`timeTaken` datetime NOT NULL,
	PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;
```
