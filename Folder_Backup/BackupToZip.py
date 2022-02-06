#! python3
#BackupToZip.py - Copies an entire folder and its contents into 
# a ZIP file whose filename increments.

import zipfile, os

from numpy import number

def backupToZip(folder):
    # Back up the entire content of "foder" into a ZIP file.

    folder = os.path.abspath(folder) # make sure folder is absolute

    # Figure out the filename this code should use based on
    # what files already exist
    number = 1
    while True:
        zipFilename = os.path.basename(folder) + '_' + str(number) + '.zip'
        if not os.path.exists(zipFilename):
            break
        number = number + 1

    # TODO: Create the ZIP file.

    # TODO: Walk, the entire folder tree and compress the files in each folder.
    print('Done.')

    backupToZip('C:\\Test')