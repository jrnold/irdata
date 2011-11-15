""" Utility functions for dealing with xls spreadsheets """
import xlrd

class Reader(object):
    """Reader object to iterate over rows of an Excel Spreadsheet

    :param f: path to .xls file
    :param sheet: index of sheet to read
    :param na: parameter

    Returns each row as a list.

    """

    def __init__(self, f, sheet=0, na=['']):

        self._book = xlrd.open_workbook(f)
        self.sheet = self._book.sheet_by_index(sheet)
        self.na = na
        self.current_row = -1

    def _to_none(self, row):
        return [x if x not in self.na else None for x in row]

    def next(self):
        self.current_row += 1
        if (self.current_row >= self.sheet.nrows):
            raise StopIteration
        else:
            row = self.sheet.row_values(self.current_row)
            return self._to_none(row)

    def __iter__(self):
        return self


class DictReader(Reader):
    """Reader object to iterate over rows of an Excel Spreadsheet

    Like the :class:`Reader` class but maps each row to a dict
    in which the keys are the optional :param:`fieldnames`.
    If :param:`fieldnames` is omitted, then the first line is
    used to generate it.

    :param f: path to .xls file
    :param sheet: index of sheet to read
    :param fieldnames: names of columns
    :param **kwds: passed to :function:`Reader.__init__`

    """
    def __init__(self, f, sheet=0, fieldnames=None, **kwds):
        super(DictReader, self).__init__(f, sheet=sheet, **kwds)
        if fieldnames:
            self.fieldnames = fieldnames
        else:
            self.fieldnames = super(DictReader, self).next()

    def next(self):
        row = super(DictReader, self).next()
        return dict(zip(self.fieldnames, row))

