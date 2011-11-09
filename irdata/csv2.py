""" Unicode CSV module

All code taken from http://docs.python.org/library/csv.html

"""

import csv
import codecs
import cStringIO

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class Reader(object):
    """
    A CSV reader which will iterate over lines in the CSV file 
    which is encoded in the given encoding.

    Any entries matching the attribute na are replace by None.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", na = [''], **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
        self.na = na

    def _to_none(self, row):
        return [x if x not in self.na else None for x in row]

    def next(self):
        row = self.reader.next()
        return self._to_none([unicode(s, "utf-8") for s in row])

    def __iter__(self):
        return self

class DictReader(Reader):
    """ """
    def __init__(self, f, fieldnames=None, **kwds):
        super(DictReader, self).__init__(f, **kwds)
        if fieldnames:
            self.fieldnames = fieldnames
        else:
            self.fieldnames = super(DictReader, self).next()

    def next(self):
        row = super(DictReader, self).next()
        return dict(zip(self.fieldnames, row))


class Writer(object):
    """
    A CSV writer which will write rows to CSV file 
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)        
