#!/usr/bin/python2.7

import urllib
import zipfile

url = 'http://www.dryerzinia.io/robosub/test_videos.zip'
filehandle, _ = urllib.urlretrieve(url)
zip_file_object = zipfile.ZipFile(filehandle, 'r')
zip_file_object.extractall(path="test_videos")

