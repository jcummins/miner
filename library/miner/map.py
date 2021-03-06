"""
The basic form of a Map...
Should be general enough that it can fit all maps (unless there seems good reason to ignore this)
Should be specific enough that it does a lot of the heavy lifting for Maps
"""

from messy2sql.core import Messy2SQL
from messytables import CSVTableSet, HTMLTableSet, XLSTableSet, PDFTableSet
import re, os
from conf.settings import *
from library.utils.helpers import download_file, unpack_tar, unpack_gzip, unpack_zip, guess_extension
from library.utils.db import DBConnect


class Map:
	# Methods internal to Maps class

	# These are here rather than in __init__ so that subclasses can simply define each of these
	# within the subclass maps
	
	# URL for homepage of dataset (e.g. http://census.gov/)
	homepage = ''

	description = ''

	# Specific URLs for the dataset downloads
	# needs to be a dictionary ala
	# data = {'census1': {url: 'http://www.census.gov/census1.zip', mirror: '', sha1: '', dictionary: ''}}
	# TODO: data is downloaded and added to databases in the order listed here. if one set depends on installation of another, put the
	# dependent ones later
	data = {}

	# type of database to install e.g. 'docstore','sql','keyvalue'
	# see conf/settings.py for available databases
	db_type = 'sql'

	db_name = ''


	def __init__(self, db_name=None):

		# specific database name specified
		if db_name:
			self.db_name = db_name

					# open MySQL connection
		self.db = DBConnect()


	def __is_installed(self, db_name):
		"""
		Utility to check if Map is already installed in base database using available
		databases and db prefix names
		"""

		# Create database if it isn't there already
		# Need to check that this returns TRUE
		return self.db.query(("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '%s';" % self.db_name))

	def setup(self):
		""" Need to prep by creating a folder and changing the system into that directory """
		global VERBOSE, TMP_DIRECTORY

		if VERBOSE:
			print "Initializing temporary working directory..."

		# make directory for this in temp dir + name_of_map
		# switch to this directory
		os.chdir(TMP_DIRECTORY)

		try:
			os.mkdir(self.__name__)
		except OSError:
			print "Directory already exists for this file..."

		os.chdir((TMP_DIRECTORY + '%s' % self.__name__))

		# in case of sql, create a database here
		# commit query

	def download(self):
		"""
		Using data dictionary of urls, grab the files and display a nice progress bar while doing it
		"""
		global VERBOSE, TMP_DIRECTORY
		if VERBOSE:
			print "Downloading data files..."

		os.chdir(TMP_DIRECTORY + "%s" % self.__name__)

		# need an iterator to download what is either a single page or a load of files, but that should get specified.
		# this should be the easiest one to write
		for k, v in self.data.iteritems():
			download_file(v['url'], with_progress_bar=True)

		# use a messy2sql because we'll need it
		# eventually this can be part of an IF import -- we only need it if we are doing SQL
		#m2s = Messy2SQL()
		

	def unpack(self):
		"""
		Unpack the downloads into the root directory for this map
		"""
		global VERBOSE

		if VERBOSE:
			print "Unpacking data files to disk..."

		# need to check what file type we've got now...
		file_types = {
			'.csv': lambda x: None,  # don't need to unpack uncompressed files
			'.sql': lambda x: None,
			'.xls': lambda x: None,
			'.xlsx': lambda x: None,
			'.html': lambda x: None,
			'.pdf': lambda x: None,
			'.tar': unpack_tar,
			'.gz': unpack_gzip,
			'.tgz': unpack_tar,
			'.tar.gz': unpack_tar,
			'.zip': unpack_zip,
		}

		# get all files in working directory of this map
		files = os.listdir(TMP_DIRECTORY + '%s/' % self.__name__)

		# iterate through files
		for f in files:
			file_name = os.path.basename(f)

			# separate out the file extension
			root, ext = guess_extension(file_name)

			# using file type, extract this file!
			file_types[ext](os.path.basename(f))


	def install(self):
		"""
		Does installation of the files into user's chosen database

		This is a primarily internal method, but if base it should just get called.

		NOTES:
			- Does installation have to assume that it can just install from each of the files available? Do we
			  have to re-write the installer for something complex like the US Census? And is that an acceptable level
			  of configuration for a Map?

		TODO:
			- Need to fix how headers work -- can specify whether headers are present, whether all data should be installed
			  into the same database?
		"""

		# check if we need a separate db for each url or whether one is enough
		# one is enough if specified here
		if self.db_name:
			db_name = self.db_name
			self.db.create_db(self.__name__)

		# for every file url
		#files = os.listdir(TMP_DIRECTORY + '%s/' % self.__name__)
		for k, v in self.data.iteritems():
			
			root, ext = guess_extension(v['url'])
			file_name = os.path.basename(root + ext)

			# If we don't have a db name, we should find it in the URLs
			if self.db_name:
				db_name = self.db_name
			else:
				db_name = v['database']
				self.db.create_db(db_name=db_name)
			
			if ext == ".sql":
				# if we have a SQL file, we should run that
				# TODO: THIS DOESN'T ACTUALLY WORK, BUT WE NEED TO DO SOMETHING LIKE THIS
				self.db.query(f)

			elif ext in (".csv", ".pdf", ".xls", ".xlsx", ".html"):	
				# create messy2sql instance
				m2s = Messy2SQL(file_name, DATABASES['sql']['type'])
				# if we have PDF, HTML, CSV, or Excel files, we should use messy2sql
				# get a table query, run it!


				fh = open((TMP_DIRECTORY + self.__name__ + '/' + file_name), 'rb')
				
				# use messytables to build a MessyTables RowSet with file type
				rows = {
					'.csv': CSVTableSet(fh).tables[0],
					# '.pdf': PDFTableSet(file_name),
					# '.xlsx': XLSTableSet(file_name),
					# '.xls': XLSTableSet(file_name),
					# '.html': HTMLTableSet(file_name),
				}[ext]

				# use the rowset here to create a sql table query and execute
				self.db.create_table(query = m2s.create_sql_table(rows), db_name=db_name)

				# get insert statements
				self.db.insert(query = m2s.create_sql_insert(rows), db_name=db_name, table_name=root)
			else:
				pass


	def cleanup(self):
		global VERBOSE

		if VERBOSE:
			print "Cleaning up folders and closing DB connections..."
		
		# need to delete all the files in tmp/thismap
		os.chdir('../')
		os.rmdir(self.__name__)

		# close DB connection
		cursor.close()
		cnx.close()
	