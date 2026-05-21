from pprint import pprint as pp
import database
import filtering
import re

class CliSession:
    def __init__(self, dataframe):
        self.df = dataframe
        self.separator = '-'
        self.run_gate = True

    def formatResults(self, results):
        longest = max([ len(i) for i in results ])
        
        print(self.separator * (longest+4))

        for i in results:
            # this is why of the +4
            print(self.separator * 3 + ' ' +i)
        
        print(self.separator * (longest+4))
        return True
    
    def formatInputs(self, inputs):
        splits = inputs.split(' ')
        out = []
        for i in splits:
            # ranges
            if '-' in i:
                start, end = list(map(int, i.split('-')))
                for r in range(start, end+1):
                    out.append(r)
            else:
                out.append(int(re.sub("[^0-9]", "", i)))

        return out

    def run(self):
        # Showing only first 15 rows
        pp(self.df)

        while self.run_gate:
            try:
                RAWINDEX = input("Type the space-separated indexes you want to open: ")
                indxs = self.formatInputs(RAWINDEX)
                
                out = [self.df['Source/Contact'].iloc[indx] for indx in indxs]
                self.formatResults(out)

                self.run_gate = False

            except:
                print("Input not valid - try again")
        return True
    

if __name__ == '__main__':

    df = database.main()
    s = CliSession(df)
    s.run()