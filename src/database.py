import os
import re
from datetime import date
import pandas as pd
import csv
import pygsheets
from pathlib import Path

from filtering import _dateOrdering

from dotenv import load_dotenv
parent = os.path.dirname(os.path.dirname(__file__)) # parent of the parent directory
dotenv_path = os.path.join(parent, '.env')
load_dotenv(dotenv_path)

#TODO implement logging
#TODO create args for this module for cli

# GLOBALS
COLUMNS = ['Studio','City', 'Country','Job Title', 'Date', 'Source/Contact' ]

def authenticate():
    """
    Authenticate with google spreadsheet using client key

    Args:
        - pygsheets.Client
    Returns:
        - pygsheets.Client
    """
    clientKey = os.getenv('GOOGLECLIENTKEY')

    if clientKey is None:
        print("Client Key environment variable not found")
        return False
    
    client = pygsheets.authorize(service_account_file=clientKey)

    return client

def getRawDatabase(client):
    """
    Get and return raw spreadsheet data as pandas Dataframe

    Args:
        - pygsheets.Client
    Returns:
        - Pandas.Dataframe
    """
    SPREADSHEET_ID = '1eR2oAXOuflr8CZeGoz3JTrsgNj3KuefbdXJOmNtjEVM'
    sheet = client.open_by_key(SPREADSHEET_ID)
    wks = sheet.worksheet_by_title('Openings')
    local_dataframe = wks.get_as_df()

    current_cols = local_dataframe.columns
    res = set(COLUMNS) & set(current_cols)

    tweak = True if len(res)==0 else False

    if tweak:
        local_dataframe.columns = local_dataframe.iloc[0]
        local_dataframe = local_dataframe.iloc[2:].reset_index(drop=True)

    return local_dataframe

def formatFileName():
    """
    Args:
        -
    Returns:
        - str
    """
    return os.path.join(os.path.dirname(__file__), 'utils', f'db_{date.today()}.csv')

def isUpdated(filepath):
    """
    Check if we have latest updates

    Args:
        - 
    Returns:
        - Bool
    """
    return os.path.exists(filepath)

def deleteOldDatabese(folderpath):
    """
    Scan supplied directory and remove old csv file

    Args:
        - str : path to a folder which contains an older version of the .csv
    Returns:
        - 
    """
    pattern = re.compile(r'db_[0-9]{4}-[0-9]{2}-[0-9]{2}.csv')
    for i in os.listdir(folderpath):
        if re.match(pattern, i):
            os.remove(os.path.join(folderpath,i))
            break
        else:
            pass
    return

def getNewDatabase(db):
    """
    Rename Studio column, remove all unnecessary columns and cleanup empty rows

    Args:
        - Pandas.Dataframe
    Returns:
        - None or str
    """
    db.rename(columns={'Studio\n(Featured listings in blue)\n(Most recent in orange)':'Studio'}, inplace=True)
    db.drop(db.columns.difference(['Studio','City', 'Country','Job Title', 'Date', 'Source/Contact' ]), axis=1, inplace=True)
    db.reset_index(drop=True) #TODO: investigate as this could be wrongly used here
    db.dropna(inplace=True)
    return db

def writeDatabaseToFile(filename, db):
    """
    Write to disk a .csv containing db at filename location

    Args:
        - str : the path where we want to save the .csv
        - Pandas.Dataframe
    Returns:
        - Pandas.Dataframe
    """
    return db.to_csv(filename, index=False)

#TODO: create docstring
#TODO: implement error handling
def getUpdated(client):
    rawDatabase = getRawDatabase(client)
    newDatabase = getNewDatabase(rawDatabase)    
    return newDatabase

def main(force=False):
    """
    Check if we have latest updates
    if not, it fetches updates, format accordingly, delete old database and writes new one to disk

    Args:
        - force bool forces the download of the job postings data
    Returns:
        - 
    """
    filename = formatFileName()
    if isUpdated(filename) and not force: return _dateOrdering(pd.read_csv(filename))

    client = authenticate()
    if client:
        newDatabase = getUpdated(client)

        deleteOldDatabese(os.path.dirname(filename)) #TODO: possible errors that end you being left with
        writeDatabaseToFile(filename, newDatabase)   #      no database at all as it fails to write it?

        return _dateOrdering(newDatabase)

    else:
        print('Authentication to Google Spreadsheet failed')

    return False


if __name__ == '__main__':
    # main(force=False)
    client = authenticate()
    t = getUpdated(client)
