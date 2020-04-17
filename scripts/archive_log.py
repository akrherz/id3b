"""Archive the ldm_product_log content for a given date

    python archive_log.py
"""
from __future__ import print_function
import os
import subprocess
import json
import datetime

import pytz
from pandas.io.sql import read_sql
import psycopg2


def process(pgconn, date):
    """Process this date please"""
    df = read_sql(
        """
        SELECT * from ldm_product_log WHERE
        entered_at >= %s and entered_at < %s
    """,
        pgconn,
        params=(date, date + datetime.timedelta(hours=24)),
        index_col=None,
    )
    basedir = date.strftime("/data/id3b/%Y/%m")
    if not os.path.isdir(basedir):
        os.makedirs(basedir)
    csvfn = basedir + date.strftime("/%Y%m%d.csv.bz2")
    if os.path.isfile(csvfn):
        print("Cowardly refusing archive_log dump for %s" % (csvfn,))
        return
    df.to_csv(csvfn, compression="bz2")
    cursor = pgconn.cursor()
    cursor.execute(
        """
    DELETE from ldm_product_log where entered_at >= %s and entered_at < %s
    """,
        (date, date + datetime.timedelta(hours=24)),
    )
    cursor.close()
    pgconn.commit()
    remotedir = date.strftime("/stage/id3b/%Y/%m")
    cmd = (
        "rsync -a --remove-source-files "
        f'--rsync-path "mkdir -p {remotedir} && rsync" '
        f"{csvfn} meteor_ldm@metl60.agron.iastate.edu:{remotedir}"
    )
    subprocess.call(cmd, shell=True)


def main():
    """Go Main Go"""
    CFGFN = "%s/settings.json" % (
        os.path.join(os.path.dirname(__file__), "../config"),
    )
    CONFIG = json.load(open(CFGFN))
    DBOPTS = CONFIG["databaserw"]
    pgconn = psycopg2.connect(
        database=DBOPTS["name"], host=DBOPTS["host"], user=DBOPTS["user"]
    )
    cursor = pgconn.cursor()
    cursor.execute(
        """
    SELECT distinct date(entered_at at time zone 'UTC') from ldm_product_log
    where entered_at < now() - '3 days'::interval ORDER by date ASC
    """
    )
    for row in cursor:
        date = datetime.datetime(
            year=row[0].year, month=row[0].month, day=row[0].day
        )
        date = date.replace(tzinfo=pytz.utc)
        process(pgconn, date)


if __name__ == "__main__":
    main()
