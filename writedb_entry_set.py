#!/usr/bin/env python3
# encoding: utf-8
"""
writedb_entry_set.py

Created by Giles Velarde on 2009-12-03.
Copyright (c) 2009 Wellcome Trust Sanger Institute. All rights reserved.
"""

import logging
import sys
import subprocess
import os
import lib
import setup
import shutil

logger = logging.getLogger("writedb_entry_set")

outhandler = logging.StreamHandler(sys.stdout)
outhandler.setLevel(logging.DEBUG)
outhandler.setFormatter(logging.Formatter(("[%(asctime)s - %(levelname)s] %(message)s")))
logger.addHandler(outhandler)

errorhandler = logging.StreamHandler(sys.stderr)
errorhandler.setLevel(logging.ERROR)
errorhandler.setFormatter(logging.Formatter(("[%(asctime)s - %(levelname)s] %(message)s")))
logger.addHandler(errorhandler)


"""
   Iterate through an array of artemis_call objects, executing it, and returning ones that caused an exception.
"""
def run_artemis_calls(artemisCalls):
    artemisCallsWithExceptions = []
    for artemisCall in artemisCalls:
       artemisCall.execLine()
       if artemisCall.exception is not None:
           artemisCallsWithExceptions.append(artemisCall)
    return artemisCallsWithExceptions


"""
   Split failing batch artemis calls into individual artemis calls, and attempt to rerun them individually.
"""
def re_run_artemis_calls(artemis_calls):
    cloned_calls = []
    for artemis_call in artemis_calls:
        for featureID in artemis_call.featureIDs:
            new_artemis_call = lib.ArtemisCall(artemis_call.filePath, artemis_call.connectionFactory, artemis_call.output_format, artemis_call.writedb_exec, artemis_call.test, artemis_call.flattened,artemis_call.submission, artemis_call.ignoreobsolete)
            new_artemis_call.addFeatureID(featureID)

            cloned_calls.append(new_artemis_call)

    return run_artemis_calls(cloned_calls)

"""
   Generate artemis_call objects for each feature supplied, in batches, and run them.
"""
def make_and_run_artemis_calls(top_level, start_at_feature_uniquename = None):
    artemisCalls = []

    artemisCall = None

    run_counter=1
    file_counter = 1
    level_name = ""
    folder_counter = 1

    max_files_per_folder = setup.options.max_files_per_folder
    max_feature_increment = setup.options.max_feature_increment

    must_add_feature = True
    if start_at_feature_uniquename is not None:
        must_add_feature = False

    for line in top_level:
        line = line.rstrip()

        new_call = False
        append_to_call = True

        if (line.startswith("#")):
            file_counter = 1
            folder_counter = 1

            level_name = line[1:]

            new_call = True
            append_to_call = False

        elif file_counter > max_files_per_folder:
            file_counter = 1
            folder_counter+=1
            new_call = True

        elif (run_counter > max_feature_increment):
            new_call = True

        if new_call:
            filePath = "%s/%s/%s"  % ( setup.baseFilePath , level_name, folder_counter )
            run_counter = 1
            logger.info("filePath: " + filePath)
            artemisCall = lib.ArtemisCall(filePath, setup.connectionFactory, setup.format, setup.options.writedb_entry, setup.options.test, setup.options.flattened, setup.options.submission, setup.options.ignoreobsolete)
            artemisCalls.append(artemisCall)

        if append_to_call:
            if start_at_feature_uniquename is not None:
                logger.debug("'%s' == '%s' " % ((start_at_feature_uniquename, line)))
                if start_at_feature_uniquename == line:
                    logger.debug("Started!")
                    must_add_feature = True
            if must_add_feature is True:
                artemisCall.addFeatureID(line)
            run_counter+=1
            file_counter+=1

    return run_artemis_calls(artemisCalls)



def main():
    if (setup.options.verbose):
        logger.setLevel(logging.DEBUG)

    logger.info( "Fetching features for: " )
    logger.info( setup.options.organism )

    organisms = []
    for org_common_name in setup.options.organism:
        organisms.append(lib.makeOrganism(setup.connectionFactory, org_common_name))
        lib.mkDir(setup.baseFilePath + "/" + org_common_name)

    annotated_only = setup.options.annotated_only
    for organism in organisms:
        if organism.organismName in annotated_only:
            organism.annotatedOnly = True

    sqlw = lib.Sql2IndexWriter(setup.connectionFactory)
    logger.debug("Initialised database connection factory")

    [logger.debug(x) for x in organisms]
    [sqlw.get_top_level_annotated(x) for x in organisms]

    top_level = sqlw.out

    failing_calls = make_and_run_artemis_calls(top_level, setup.options.start_at_feature_uniquename)

    if len(failing_calls) > 0 :
        still_failing_calls = re_run_artemis_calls(failing_calls)

        if len(still_failing_calls) > 0:
            logger.error("Exceptions occurred:")
            logger.error("\n")
            for artemisCall in still_failing_calls:
                if artemisCall.exception is not None:
                    logger.error("Batch : ")
                    logger.error(str(artemisCall.featureIDs))
                    logger.error("\n")
                    logger.error(str(artemisCall.exception))
                    logger.error("\n")
                    logger.error("\n")
            sys.exit(1)

    if setup.options.bundle:
        ftpPath = setup.options.bundle
        tgzFilePath = setup.baseFilePath + '.tar.gz'
        logger.info('tar -zcvf '+ tgzFilePath + ' ' + setup.baseFilePath)
        tgz = subprocess.Popen(['tar', '-zcvf', tgzFilePath, setup.baseFilePath ], stdout=subprocess.PIPE).communicate()[0]
        logger.info (tgz)
        mkdir = lib.mkDir(ftpPath)
        logger.info (mkdir)
        mv = subprocess.Popen(['mv', tgzFilePath, ftpPath ], stdout=subprocess.PIPE).communicate()[0]
        logger.info (mv)

    if setup.options.single_file:
        for common_name in setup.options.organism:
            if len(common_name) == 0:
                continue
        targetfilename = setup.baseFilePath + '/' + common_name + '.gff3.gz'
        cmd = "find " + setup.baseFilePath + '/' + common_name + \
              " -name '*.gff.gz' | xargs  " + setup.options.gtbin + \
              " gff3 -sort -retainids -tidy -gzip -force -o " + \
              targetfilename + " 2> " + \
              setup.baseFilePath + '/' + common_name + ".log"
        logger.info (cmd)
        rval = os.system(cmd)
        if rval != 0:
            raise Exception("error tidying/merging/sorting input for " + common_name + " into " + targetfilename)
        if os.path.isdir(setup.baseFilePath + '/' + common_name):
            shutil.rmtree(setup.baseFilePath + '/' + common_name)

if __name__ == "__main__":
    sys.exit(main())
