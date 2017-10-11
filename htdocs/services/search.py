#!/usr/bin/env python
"""Service for searching for products"""
import json
import cgi
import sys
import datetime

import psycopg2


def get_subsql(colname, fullwidth, param):
    """Generate fancy sql subquery with some optimizations"""
    if len(param) == fullwidth:
        return " %s = %%s" % (colname, )
    return " strpos(%s, %%s) > 0 " % (colname, )


def do_search(wmo_ttaaii, wmo_source, awips_id):
    """Make search great again"""
    sts = datetime.datetime.utcnow()
    pgconn = psycopg2.connect(database='id3b', host='localhost', user='nobody')
    cursor = pgconn.cursor()
    sql = []
    args = []
    if awips_id != "":
        sql.append(get_subsql("awips_id", 6, awips_id))
        args.append(awips_id)
    if wmo_source != "":
        sql.append(get_subsql("wmo_source", 4, wmo_source))
        args.append(wmo_source)
    if wmo_ttaaii != "":
        sql.append(get_subsql("wmo_ttaaii", 6, wmo_ttaaii))
        args.append(wmo_ttaaii)
    if sql:
        sql = "(%s)" % (" and ".join(sql), )
    else:
        sql = "(awips_id = %s and wmo_source = %s)"
        args = ('ADDMX', 'KDMX')

    cursor.execute("""
    SELECT wmo_ttaaii, wmo_source,
    to_char(entered_at at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as eat,
    size, product_id, awips_id,
    to_char(valid_at at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as vat,
    to_char(wmo_valid_at at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as wat
    from ldm_product_log where """ + sql + """
    ORDER by entered_at DESC LIMIT 100
    """, args)
    res = {'products': []}
    for row in cursor:
        res['products'].append({
            'wmo_ttaaii': row[0],
            'wmo_source': row[1],
            'entered_at': row[2],
            'size': row[3],
            'product_id': row[4],
            'awips_id': row[5],
            'valid_at': row[6],
            'wmo_valid_at': row[7]})
    res['generation_time[secs]'] = round((datetime.datetime.utcnow() -
                                          sts).total_seconds(), 3)
    res['generated_at'] = sts.strftime("%Y-%m-%dT%H:%M:%SZ")
    sys.stdout.write(json.dumps(res))


def main():
    """Attempt to do the right thing"""
    sys.stdout.write("Content-type: application/json\n\n")
    form = cgi.FieldStorage()
    awips_id = form.getfirst('awips_id', '')[:6].upper()
    wmo_source = form.getfirst('wmo_source', '')[:4].upper()
    wmo_ttaaii = form.getfirst('wmo_ttaaii', '')[:6].upper()
    do_search(wmo_ttaaii, wmo_source, awips_id)


if __name__ == '__main__':
    main()
