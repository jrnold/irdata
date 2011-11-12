def load_contdir(src):
    """ Load direct contiguity data from csv file"""
    session = model.SESSION()
    reader = csv2.DictReader(src, encoding='latin1')
    cols = [x.name for x in model.ContDir.__table__.c]
    for row in reader:
        start_mon = datetime.date(int(row['begin'][:4]),
                                  int(row['begin'][4:]), 1)
        end_mon = datetime.date(int(row['end'][:4]),
                                int(row['end'][4:]), 1)
        
        if end_mon.month == 12:
            end_mon = datetime.date(end_mon.year + 1, 1, 1)
        else:
            end_mon = datetime.date(end_mon.year, end_mon.month + 1, 1)
        end_mon += datetime.timedelta(days = -1)
        row['end_date'] = end_mon
        row['start_date'] = start_mon
        data = utils.subset(row, cols)
        session.add(model.ContDir(**data))
    session.commit()


