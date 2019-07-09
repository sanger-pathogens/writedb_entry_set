#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Giles Velarde on 2009-12-03.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import datetime

import optparse
import sys
import os
import time
import configparser
from distutils.spawn import find_executable


import options
import password

import lib
import connectionfactory

parser = optparse.OptionParser()

parser.add_option(
    "-o", "--organism",
    dest="organism",
    action="append",
    help="the organism common_name (can specify many of these)")

parser.add_option(
    "-n", "--annotated_only",
    dest="annotated_only",
    action="append",
    default=[],
    help="for the organisms specified with this option, only retrieve top-level features that are deemed to have annotations")

parser.add_option(
    "-e", "--embl",
    dest="embl",
    action="store_true",
    default=False,
    help="export in EMBL format (defaults to GFF)")

parser.add_option(
    "-p", "--prefix",
    dest="prefix",
    action="store",
    default="artemis",
    help="a prefix to prepend to the export folder name")

parser.add_option(
    "-b", "--bundle",
    dest="bundle",
    action="store",
    help="if you wish to autogenerate a bundle, provide path here")

parser.add_option(
    "-w", "--writedb_entry",
    dest="writedb_entry",
    action="store",
    default="writedb_entry",
    help="the path to writedb_entry")

parser.add_option(
    "-m", "--max_feature_increment",
    dest="max_feature_increment",
    action="store",
    type="int",
    default=10,
    help="the max number features to be batched by artemis in one go")

parser.add_option(
    "-f", "--max_files_per_folder",
    dest="max_files_per_folder",
    action="store",
    type="int",
    default=1000,
    help="the max number of files per folder")

parser.add_option(
    "", "--single_file",
    dest="single_file",
    action="store_true",
    default=False,
    help="write sorted, postprocessed single GFF file per organism (requires GenomeTools `gt' executable in PATH)")

parser.add_option(
    "-v", "--verbose",
    dest="verbose",
    action="store_true",
    default=False,
    help="output additional information while running")

parser.add_option(
    "-d", "--database_connection",
    dest="database_connection",
    action="store",
    help="either a database uri or a path to a conf_file")

parser.add_option(
    "-x", "--export_folder",
    dest="export_folder",
    action="store",
    help="the path to the destination_folder")

parser.add_option(
    "-a", "--suffix_date_in_path",
    dest="suffix_date_in_path",
    action="store_true",
    default=False,
    help="suffixes the base path with the starting date and time")

parser.add_option(
    "-t", "--test",
    dest="test",
    action="store_true",
    default=False,
    help="add the -test option")

parser.add_option(
    "-l", "--flattened",
    dest="flattened",
    action="store_true",
    default=True,
    help="if embl, flatten")

parser.add_option(
    "-s", "--start_at_feature_uniquename",
    dest="start_at_feature_uniquename",
    action="store",
    help="start at the feature_id (for resuming stalled exports)")

parser.add_option(
    "-z", "--emblsubmission",
    dest="submission",
    action="store_true",
    default=False,
    help="if embl, use submission format")

parser.add_option(
    "-i", "--ignoreobsolete",
    dest="ignoreobsolete",
    action="store_true",
    default=False,
    help="do not export obsolete features")

(options, args) = parser.parse_args()

if (options.organism == None):
    print("\nYou must specify at least one organism.\n")
    parser.print_help()
    sys.exit()

if (options.single_file):
    options.gtbin = find_executable('gt')
    if options.gtbin == None:
        print("\nThe option `--single_file' requires the `gt' binary in the PATH but it could not be found.\n")
        sys.exit(1)
    if options.embl == True:
        print("\nThe option `--single_file' implies GFF3 output but EMBL was requested.\n")
        sys.exit(1)

if (options.database_connection == None):
    print("\nYou must specify a database connection.\n")
    parser.print_help()
    sys.exit()

if (options.export_folder == None):
    print("\nYou must specify a export_folder.\n")
    parser.print_help()
    sys.exit()


data_path = options.export_folder

host = ""
database=""
port= 0
user = ""
password = ""

if os.path.isfile(options.database_connection):

    config_parser = configparser.ConfigParser()
    config_parser.read(options.database_connection)

    host=config_parser.get('Connection', 'host')
    database=config_parser.get('Connection', 'database')
    user=config_parser.get('Connection', 'user')
    password=config_parser.get('Connection', 'password')
    port=config_parser.get('Connection', 'port')

else:
    (host, port, database, user) = options.parse_database_uri(options.database_connection)
    password = password.get_password("WRITEDB_ENTRIES_PASSWORD")

connectionFactory = connectionfactory.ConnectionFactory(host, database, user, password, port)

format = "GFF"
if options.embl == True:
    format = "EMBL"

strTime = str(datetime.date.today())
actualTime = time.strftime("%H:%M:%S", time.localtime())
baseFilePath = data_path + "/" + options.prefix

if options.suffix_date_in_path == True:
    baseFilePath += "-" + strTime + "-" + actualTime

baseFilePath += "/" + format


lib.mkDir(baseFilePath)




