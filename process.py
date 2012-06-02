from osgeo import gdal
import os
import numpy as np
import pymysql
pymysql.install_as_MySQLdb()

IMAGE_PATH = "/Users/robin/Documents/RHoK"

def get_from_ftp(date, h, v):
	

def resample(hdf_filename):
	# Edit parameter file appropriately
	f = open("base_param.prm", "r")
	lines = f.readlines()
	
	outfile = open("image.prm", "w")
	outfile.write("INPUT_FILENAME = %s\n" % hdf_filename)
	outfile.writelines(lines)
	outfile.close()
	
	# Run MRT resample tool
	os.system("./ResampleTool %s/image.prm" % (IMAGE_PATH)) 

def add_to_db(basename):
	b1_tiff = gdal.Open("%s.sur_refl_b01_1.tif" % basename)
	b2_tiff = gdal.Open("%s.sur_refl_b02_1.tif" % basename)
	b3_tiff = gdal.Open("%s.sur_refl_b03_1.tif" % basename)
	b4_tiff = gdal.Open("%s.sur_refl_b04_1.tif" % basename)
	b5_tiff = gdal.Open("%s.sur_refl_b05_1.tif" % basename)
	b6_tiff = gdal.Open("%s.sur_refl_b06_1.tif" % basename)
	b7_tiff = gdal.Open("%s.sur_refl_b07_1.tif" % basename)
	
	
	
	g = b1_tiff.GetGeoTransform()
	minX = g[0]
	maxY = g[3]
	pixel_size = g[1]
	
	b1 = b1_tiff.ReadAsArray()
	b2 = b2_tiff.ReadAsArray()
	b3 = b3_tiff.ReadAsArray()
	b4 = b4_tiff.ReadAsArray()
	b5 = b5_tiff.ReadAsArray()
	b6 = b6_tiff.ReadAsArray()
	b7 = b7_tiff.ReadAsArray()
	
	ignore_below = 100
	
	conn = pymysql.connect(host="31.222.179.91", user="ndwi", passwd="datandwi2012", db="RHoK_NDWI")
	cursor = conn.cursor()
	
	
	for index, value in np.ndenumerate(b1):
		y, x = index
		
		# Ignore all values below ignore_below
		# Basically negative is unmapped, and v low values are sea
		if value < ignore_below: continue
		
		lat = maxY - (y * pixel_size)
		lon = minX + (x * pixel_size)
		
		if lat > 52 or lat < 50: continue
		if lon > 0 or lon < -1.5: continue
		
		band1 = value
		band2 = b2[y, x]
		band3 = b3[y, x]
		band4 = b4[y, x]
		band5 = b5[y, x]
		band6 = b6[y, x]
		band7 = b7[y, x]
		
		print lat, lon, band1, band2
		
		ndvi = (band2 - band1) / (float(band2) + band1)
		ndwi = (band2 - band5) / (float(band2) + band5)
		
		sql_string = "INSERT INTO Data (latitude, longitude, bandOne, bandTwo, bandThree, bandFour, bandFive, bandSix, bandSeven, vegetation, NDWI) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);" % (lat, lon, band1, band2, band3, band4, band5, band6, band7, ndvi, ndwi)
		print cursor.execute(sql_string)
		conn.commit()
		
#hdf_filename = "/Users/robin/Downloads/MOD09GA.A2012148.h17v03.005.2012150062118.hdf"
#resample(hdf_filename)