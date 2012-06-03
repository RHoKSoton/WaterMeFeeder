from osgeo import gdal
import os
from os.path import dirname, basename
import numpy as np
from ftplib import FTP
import re
import datetime
import pymysql
pymysql.install_as_MySQLdb()

ROOT_PATH = "/Users/robin/Documents/RHoK/"
IMAGE_PATH = "/Users/robin/Documents/RHoK/data"

MYSQL_SERVER = ""
MYSQL_USER = ""
MYSQL_PASSWD = ""
MYSQL_DB = ""

def do_stuff():
	#run_whole_process(2012, 5, 20, 17, 8)
	#run_whole_process(2012, 5, 27, 18, 8)
	#run_whole_process(2012, 5, 28, 17, 8)
	#run_whole_process(2012, 5, 28, 18, 8)
	
	for day in range(13, 27):
		print day
		run_whole_process(2012, 5, day, 12, 9)
		run_whole_process(2012, 5, day, 11, 9)

	#for day in range(1, 9):
	#	print day
	#	run_whole_process(2012, 5, day, 17, 8)
	#	run_whole_process(2012, 5, day, 18, 8)
		
	#for day in range(29, 32):
	#	print day
	#	run_whole_process(2012, 5, day, 17, 8)
	#	run_whole_process(2012, 5, day, 18, 8)

	
def run_whole_process(year, month, day, h, v):
	"""Download, process and insert into the database all values from the specified MODIS image.
	The image is specified by the year, month and day of the image, as the horizontal and vertical
	co-ordinates in the MODIS grid reference system (see http://www.yale.edu/ceo/DataArchive/modis.html)
	"""
	filename = get_from_ftp(year, month, day, h, v)
	#filename = "MOD09GA.A2006143.h17v03.005.2008320021945.hdf"
	resample(filename)
	date = datetime.datetime(year, month, day)
	add_to_db("/Users/robin/Documents/RHoK/data/MODIS_Reflectance", date)

def get_from_ftp(year, month, day, h, v):
	"""Given a year, month, day and horizontal and vertical co-ordinate in the MODIS grid reference system,
	download the MOD09GA product from the FTP site.
	
	This checks to see if the destination local file exists, and if so uses it rather than downloading again.
	"""
	ftp = FTP("e4ftl01.cr.usgs.gov")
	ftp.login()
	files = ftp.nlst("MOLT/MOD09GA.005/%02d.%02d.%02d/" % (year, month, day))
	
	for f in files:
		if re.search("h%02dv%02d.+\.hdf$" % (h, v), f):
			print f
			filename = f
	
	folder = dirname(filename)
	file = basename(filename)
	
	if os.path.exists(file): return file
	
	print "Downloading from FTP"
	ftp.cwd(folder)
	ftp.retrbinary('RETR %s' % file, open('%s' % file, 'wb').write)
	print "Downloaded file %s" % file
	ftp.close()

	return file

def resample(hdf_filename):
	"""Resample the given HDF filename to a WGS84 Geographic Co-ordinate System, storing the outputs
	as GeoTiffs.
	
	Uses the parameter values stored in base_param.prm, adding INPUT_FILENAME with the appropriate HDF
	file at the top.
	
	"""
	# Edit parameter file appropriately
	f = open("base_param.prm", "r")
	lines = f.readlines()
	
	outfile = open("image.prm", "w")
	outfile.write("INPUT_FILENAME = %s\n" % hdf_filename)
	outfile.writelines(lines)
	outfile.close()
	
	# Run MRT resample tool
	os.system("./ResampleTool %s/image.prm" % (ROOT_PATH)) 

def add_to_db(basename, date):
	"""Add the data from the MODIS GeoTIFF files with the basename given to the database.
	
	Values of database parameters are given at the top of this script. This assumes the reprojection
	has been done using the resample function in this file, so that the correct output bands are available.
	
	This ignores crazy values (< 0.01% reflectance), clouds and non-land pixels, using the appropriate masks in the
	MODIS data.
	
	"""
	print "Running add to db"
	quality_tiff = gdal.Open("%s.QC_500m_1.tif" % basename)
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
	
	q = quality_tiff.ReadAsArray()
	b1 = b1_tiff.ReadAsArray()
	b2 = b2_tiff.ReadAsArray()
	b3 = b3_tiff.ReadAsArray()
	b4 = b4_tiff.ReadAsArray()
	b5 = b5_tiff.ReadAsArray()
	b6 = b6_tiff.ReadAsArray()
	b7 = b7_tiff.ReadAsArray()
	
	ignore_below = 100
	
	conn = pymysql.connect(host=MYSQL_SERVER, user=MYSQL_USER, passwd=MYSQL_PASSWD, db=MYSQL_DB)
	cursor = conn.cursor()
	
	
	for index, value in np.ndenumerate(b1):
		y, x = index
		
		lat = maxY - (y * pixel_size)
		lon = minX + (x * pixel_size)
		
		#if lat > 52 or lat < 50: continue
		#if lon > 0 or lon < -1.5: continue
		

		band1 = value
		band2 = b2[y, x]
		band3 = b3[y, x]
		band4 = b4[y, x]
		band5 = b5[y, x]
		band6 = b6[y, x]
		band7 = b7[y, x]
		quality = q[y, x]
		
		all_bands = [band1, band2, band3, band4, band5, band6, band7]
		
		# Ignore all values below ignore_below
		# Basically negative is unmapped, and v low values are sea
		if min(all_bands) < ignore_below: continue
		
		# Bitwise AND to extract the last two binary digits of the quality int
		cloud_mask = quality & 3
		land_mask = quality & 56
		land_mask = land_mask >> 3
		
		# Don't bother with this cell unless it is clear
		if cloud_mask != 0: continue
		if land_mask != 1: continue
		
		
		print lat, lon, band1, band2, cloud_mask
		
		ndvi = (band2 - band1) / (float(band2) + band1)
		ndwi = (band2 - band5) / (float(band2) + band5)
		
		sql_string = "INSERT INTO Data (latitude, longitude, bandOne, bandTwo, bandThree, bandFour, bandFive, bandSix, bandSeven, vegetation, NDWI, timeTaken) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, \"%s\");" % (lat, lon, band1, band2, band3, band4, band5, band6, band7, ndvi, ndwi, date.strftime("%Y-%m-%d %H:%M:%S"))
		#print sql_string
		print cursor.execute(sql_string)
		conn.commit()