import sys
from ui import JobScanner
import os
import argparse
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

def _args():
    parser = argparse.ArgumentParser(
                        prog='Job Net',
                        description='Get and filter job postings')
    parser.add_argument('-f', '--filters', nargs='+', help='keywords to filter data', default=[])
    parser.add_argument('-c', '--columns', nargs='+', help='column names', default=[])
    parser.add_argument('-ui', '--ui', action='store_true')
    parser.add_argument('-mr', '--mostRecent', action='store_true')

    return parser.parse_args()


if __name__ == '__main__':

    args = _args()

    if args.ui:
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon/icon.png')))
        window = JobScanner()
        sys.exit(app.exec_())

    if len(args.columns) > 0 and len(args.filters) > 0:
        # is this a good idea?
        import database
        import filtering
        from pprint import pprint as pp

        import pandas as pd
        import cli

        pd.options.display.expand_frame_repr = False

        t = database.main()
        out = filtering.advancedFilter(t, filters=args.filters, columnsToFilter=args.columns, mostRecent=args.mostRecent)

        s = cli.CliSession(out)
        s.run()
