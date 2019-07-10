#!/usr/bin/env python
# encoding: utf-8
"""
lib.py

Created by Giles Velarde on 2009-12-03.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import logging
import subprocess
import os

logger = logging.getLogger("writedb_entry_set")

class Organism(object):
    def __init__(self, organismName, organismID, annotatedOnly = False):
        self.organismName = organismName
        self.organismID = organismID
        self.annotatedOnly = annotatedOnly

    def __str__(self):
        return self.organismName + "(" + str(self.organismID) + " " + str(self.annotatedOnly) + ")"

class ArtemisCall(object):

    def __init__(self, filePath, connectionFactory, output_format, writedb_exec, test, flattened, submission, ignoreobsolete):
        self.filePath = filePath
        self.featureIDs = []
        self.output_format = output_format
        self.connectionFactory = connectionFactory
        self.writedb_exec = writedb_exec

        self.test=test
        self.flattened=flattened

        self.submission=submission
        self.submissions=[]
        if (self.submission is True):
            self.submissions=["-a", "n"]

        self.ignoreobsolete = ignoreobsolete
        self.ignoreobsoletes=[]
        if (self.ignoreobsolete is True):
            self.ignoreobsoletes=["-i", "y"]

        self.exception = None

        if not os.path.isdir(filePath):
            mkDir(filePath)

    def getGexecArgs(self):

        f = "n"
        if self.flattened is True:
            f = "y"

        exec_args = [
            "-Djava.awt.headless=true",
            "-f",
            f,
            "-c",
            self.connectionFactory.host + ":" + self.connectionFactory.port + "/" + self.connectionFactory.database + "?" + self.connectionFactory.user,
            "-o",
            self.output_format,
            "-u",
            "script",
            "-flt",
          #  "orthologous_to",
            "history",
            "fasta_file",
            "timelastmodified",
            "feature_id",
            "isObsolete",
            "colour",
            "blastx_file",
            "blastp_file",
            "blastn_file",
            "blast_file",
            "full_GO",
            "estimated_length",
            "blastp+go_file",
            "blastx_file",
            "clustalx_file",
            "eMBL_qualifier",
            "tblastx_file",
            "-p",
            self.connectionFactory.password
        ]

        exec_args.extend(self.submissions)
        exec_args.extend(self.ignoreobsoletes)

        if self.test is True:
            exec_args.insert(0, "-test")

        return exec_args

    def addFeatureID(self, featureID):
        self.featureIDs.append(featureID)

    def generateCommandArray(self):
        array = [self.writedb_exec]

        for arrg in self.getGexecArgs():
            array.append(arrg)

        array.append("-fp")
        array.append(self.filePath)

        array.append("-s")
        for featureID in self.featureIDs:
            array.append(featureID)

        return array

    def execLine(self):

        if len(self.featureIDs) < 1:
            logger.info("No ids in this call, skipping")
            return

        array = self.generateCommandArray()
        logger.info(subprocess.list2cmdline(array))
        process = subprocess.Popen(array, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outputs = process.communicate()
        logger.info("Checking for Exceptions...")
        for output in outputs:
            output_text = output.decode()
            if output_text.find("Exception") > -1:
                logger.info("Found exception!")
                self.exception = output_text
            else:
                logger.info("No exceptions found")

            logger.info(output_text)




class Sql2IndexWriter(object):

    def __init__(self, connectionFactory):
        self.out = []
        self.cur = connectionFactory.getConnection().cursor()

    def write_rows(self, rows):
        for row in rows:
            logger.debug("Retrieved row: " + str(row[0]) + "\t" + str(row[1]))
            self.out.append( str(row[0]) + "\n" )

    def get_top_level_annotated(self, organism):
        logger.debug ("#" + organism.organismName + " annotated only? " + str(organism.annotatedOnly) )
        self.out.append ("#" + organism.organismName + "\n" )

        query  = "select f.uniquename,f.feature_id from feature f "
        query += "join cvterm on f.type_id = cvterm.cvterm_id "
        query += "join featureprop using (feature_id) "
        query += "where f.organism_id= "

        query += str(organism.organismID)

        query += " and featureprop.type_id in "
        query += "  (select cvterm_id from cvterm join cv using (cv_id) where cv.name = 'genedb_misc' and cvterm.name = 'top_level_seq') "

        query += " and f.type_id not in ('432', '1087') "

        if organism.annotatedOnly == True:
            query += "and f.feature_id in "
            query += "  (select srcfeature_id from featureloc where srcfeature_id = f.feature_id group by srcfeature_id having count(*) > 1 ) "

        query += "order by uniquename ";

        self.cur.execute(query)
        rows = self.cur.fetchall()

        self.write_rows(rows)



def getOrganismIDFromCommonName(connectionFactory, commonName):
    # print commonName
    query  = " select organism_id from organism where common_name = '" + commonName + "'";
    cur = connectionFactory.getConnection().cursor()
    cur.execute(query)
    rows = cur.fetchall()
    for row in rows:
        return int(row[0])
    raise Exception("Could not find an ID for %s." % commonName)


def makeOrganism(connectionFactory, orgName):
    orgID = getOrganismIDFromCommonName(connectionFactory, orgName)
    org = Organism( orgName, orgID )
    return org


def mkDir(path):
    mkdir = subprocess.Popen(['mkdir', '-p', path], stdout=subprocess.PIPE).communicate()[0]
    logger.debug(mkdir)
    return mkDir

def getIndexFilePath(baseFilePath, prefix, strTime):
    iPath = baseFilePath + "/" + prefix + "_" + strTime + "_top_level_features.txt"
    logger.debug(iPath)
    return iPath
