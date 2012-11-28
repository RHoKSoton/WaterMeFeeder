#!/usr/bin/env python
#-*- coding:utf-8 -*-

import ftplib
import gdal
import numpy as np

"""
Author: Pete
Date: 	28th November 2012
Version: 0.0.0

{FEEDER} ~ Rewrite due to MRT dependance
		 ~ Moving to GDAL for handling resampling, output and possible tile creation

		 ~ totally beta but... Run the script and the tiles that cover the particular month and year
		   specified and it will download the files to where the script lies.		

"""

data_dir = []
print 'Welcome to the Feeder : )'

ftp = ftplib.FTP("e4ftl01.cr.usgs.gov")
ftp.login("anonymous", "thisisme")
ftp.cwd("/MOLT/MOD09A1.005/")
print 'Loading data directories...'

ftp.dir(data_dir.append)
#print data_dir

dirnames = [i.split() [-1] for i in data_dir[1:]]
#print dirnames

dirinfo = np.array([ (len(k) == 3 and k) or [0,0,0] for k in [[ (unicode(j).isnumeric() and int(j)) or 0 for j in i.split()[-1].split('.')] for i in data_dir[1:]]])
#print dirinfo[:,0]

""" 
Enter a year and month of interest

"""
###################################

aMonth = 11 # << EXAMPLE
aYear = 2012 # << EXAMPLE

###################################

yearMatch = dirinfo[:,0] == aYear
monthMatch = dirinfo[:,1] == aMonth
allMatch = yearMatch * monthMatch
w = np.where(allMatch)[0]
print 'Item numbers: ', w

print 'Year: %d' % aYear
print 'Month: %d' % aMonth

dir_i_want = np.array(dirnames)[w]

#print dir_i_want

def getDownload(block):
	file.write(block)

tileOfInterest = 'h09v05'
for i in dir_i_want:
	ftp.cwd(i)
	this = []
	ftp.dir(this.append)
	filenames = [i.split() [-1] for i in this[1:]]
	fileinfo = np.array([i.split('.') for i in this[1:]])
	tileMatch = np.array([i[2] == tileOfInterest for i in fileinfo])
	w = np.where(tileMatch) [0]
	for f in np.array(filenames)[w]:
		print 'Opening local file ' + f
		file = open(f, 'wb')
	print 'Getting ' + f
	ftp.retrbinary('RETR %s'%f, getDownload)
	ftp.cwd('..')

print 'Finishing up...'
ftp.quit()


