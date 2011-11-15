import xlrd

class Reader(object):
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
    def __init__(self, f, sheet=0, fieldnames=None, **kwds):
        super(DictReader, self).__init__(f, sheet=sheet, **kwds)
        if fieldnames:
            self.fieldnames = fieldnames
        else:
            self.fieldnames = super(DictReader, self).next()

    def next(self):
        row = super(DictReader, self).next()
        return dict(zip(self.fieldnames, row))

