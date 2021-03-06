"""
Global Settings

settings.py initiates global settings. Keeps all of these in one area so users can easily update and change based
on their own needs.

Global settings need to be imported into functions and classes with the 'global' keyword before the variable/function name
They are all in capital letters to differentiate them from other variables which are in lower case and separated by underscores '_'

Eventually setup.py should allow the user to configure these on first use or installation of the software so that they work
However, at this point, the user will need to update these themself.
"""

import os

#################
# CORE SETTINGS #
#################

# VERBOSE							should we display verbose-ness?
VERBOSE = True

# debug								should debug information be displayed?
DEBUG = True

# DELETE_TMP_ON_COMPLETE			delete or save temporary files when extracting is finished?
DELETE_TMP_ON_COMPLETE = True

# DICTIONARIES						directory to store data dictionaries
DICTIONARIES = "./dictionaries"

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__)) + "/../"

# TMP_DIRECTORY						directory to store temporary download files while extracting
TMP_DIRECTORY = PROJECT_ROOT + "tmp/"

#####################
# DATABASE SETTINGS #
#####################

# SQL_DATABASE						connection information for relational database
# NOSQL_DATABASE					connection information for docstore database

# At minimum, SQL_DATABASE and NOSQL_DATABASE must be installed
# Different maps will prefer certain database types, not all types are appropriate for each map

DATABASES = {
		'sql': {
			'type': 'mysql',
			'username': 'specialuser',
			'password': 'specialpass',
			'hostname': 'localhost',
			'db_prefix': 'miner_', # If DB_PREFIX isn't set, no prefix will be used
		},

		'docstore': {
			'type': 'hadoop',
		},

		'keyvalue': {
			'type': 'redis',
		}
	}

# DROP_IF_EXISTS					if database or table already exists, should it be ignored or dropped?
DROP_IF_EXISTS = True