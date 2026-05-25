import pandas as pd
import numpy as np

#Inplace waiting for a proper fix
import warnings
warnings.simplefilter('ignore')

#TODO implement logging
#TODO create args for this module for cli - is it really needed?

def _dateOrdering(database):
    from datetime import datetime

    database['Date'] = pd.to_datetime(database['Date'], format='%B %d, %Y')
    database.sort_values(by=['Date'], inplace=True, ascending=False)
    database.reset_index(drop=True, inplace=True)

    database['Date'] = pd.to_datetime(database['Date'], format='%B %d, %Y')
    database["Date"] = database['Date'].dt.strftime('%B %d, %Y')

    return database

def _filterMostRecent(database):
    from datetime import datetime

    tmp = database.copy()
    tmp['Date'] = pd.to_datetime(tmp['Date'], format='%B %d, %Y') # output YYYY-MM-DD

    today = datetime.today().date()
    delta = pd.Timedelta(days=14) # two weeks
    start = today - delta

    today = today.strftime('%Y-%m-%d')
    start = start.strftime('%Y-%m-%d')

    mask = (tmp['Date'] >= start) & (tmp['Date'] <= today)

    out = database.loc[mask]

    return out

def advancedFilter(database, filters=[], columnsToFilter=[], mostRecent=False):
    """
    Advance filter ... wip

    Args:
        - Pandas.Dataframe
    Optional args:
        - filters list of str
        - columnsToFilter list of str
        - mostRecent bool
    Returns:
        - Pandas.Dataframe
    """

    if (len(filters) == 0 or len(columnsToFilter) == 0) and mostRecent == False:
        return database
    
    baseCondition = r"{}.str.lower().str.contains('{}'.lower(), na=False)"

    conditions = []
    for c in columnsToFilter:
        if " " in c:
            c = f"{"`"}{c}{"`"}" # escape character if column name contains a space

        partialConditions = []
        for f in filters:
            partialCondition = baseCondition.format( c, f )

            #pre check
            tmp = database.query(partialCondition)
            if tmp.size > 0:
                partialConditions.append( partialCondition )

        if len(partialConditions) > 0:
            partialConditionsSet = '(' + " | ".join(partialConditions) + ')'
            conditions.append(partialConditionsSet)

    if len(conditions) > 0:
        mask = " & ".join(conditions)
        out = database.query("{}".format(mask))

        if out.size == 0:
            print("Filters returned nothing")
            out = database
    else:
        out = database

    out = _dateOrdering(out)

    if mostRecent:
        out = _filterMostRecent(out)

    return out

if __name__ == "__main__":
    import database
    t = database.main()
    print(_dateOrdering(t))
