from itertools import product

def simplePairing(columnsToFilter=[], filters=[]):
    raw = list(product(columnsToFilter, filters))
    out = list(map(lambda x : [x[0], x[1]], raw))
    return out

#TODO move this into the ui with the right-click context in the custom model (?)
def open_link(self,signal):
        brave_cmd = r'open -a /Applications/Brave\ Browser.app'
        row = signal.row()
        column = signal.column()
        cell_dict = self.model.itemData(signal)
        cell_value = cell_dict.get(0)

        if column == 5:
            if 'http' in cell_value:
                try:
                    os.system('{} {}'.format(brave_cmd, cell_value))
                except:
                    webbrowser.open_new(cell_value)
            else:
                webbrowser.open('mailto:{}'.format(cell_value), new=1)
        elif column == 0:
            application_manager.add_position(cell_value)
            print('adding {} to application tracking sheet'.format(cell_value))
        else:
            pass

#set()-like for dataframe based on multiple columns (subsets)
def getSubsetsDf(databse, subsets=[]):
    # additional = ['Address', 'Longitude', 'Latitude']
    additional = []

    new = databse.drop_duplicates( 
        subset = subsets, 
        keep = 'last').reset_index(drop=True)
    
    new.drop(list(set(databse.columns) - set(subsets)), axis=1, inplace=True)
    for a in additional:
        new[a] = ''
    return new

# adding new values to the studio info database in case new job postings
# appear and we haven't seen the studio info yet
def updateStudioData():
    return


if __name__ == '__main__':
    from pprint import pprint as pp

    columns = ['Job Title', 'City']
    filters = ['vancouver', 'comp']

    pp(simplePairing(filters=filters, columnsToFilter=columns))