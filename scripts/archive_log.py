"""Archive the ldm_product_log content for a given date

    python archive_log.py
"""
import os
import subprocess
import json
import datetime

import pytz
from pandas import read_sql
import psycopg2


def process(DBOPTS, pgconn, date):
    """Process this date please"""
    dsn = f"postgresql://{DBOPTS['user']}@{DBOPTS['host']}/{DBOPTS['name']}"
    df = read_sql(
        "SELECT * from ldm_product_log WHERE "
        "entered_at >= %s and entered_at < %s",
        dsn,
        params=(date, date + datetime.timedelta(hours=24)),
        index_col=None,
    )
    csvfn = date.strftime("/tmp/%Y%m%d.csv.bz2")
    if os.path.isfile(csvfn):
        print(f"Cowardly refusing archive_log dump for {csvfn}")
        return
    df.to_csv(csvfn, compression="bz2", index=False)
    cursor = pgconn.cursor()
    cursor.execute(
        "DELETE from ldm_product_log "
        "where entered_at >= %s and entered_at < %s",
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
    CFGFN = os.path.join(
        os.path.dirname(__file__),
        "../config",
        "settings.json",
    )
    with open(CFGFN, encoding="utf-8") as fh:
        CONFIG = json.load(fh)
    DBOPTS = CONFIG["databaserw"]
    pgconn = psycopg2.connect(
        database=DBOPTS["name"], host=DBOPTS["host"], user=DBOPTS["user"]
    )
    cursor = pgconn.cursor()
    cursor.execute(
        "SELECT distinct date(entered_at at time zone 'UTC') "
        "from ldm_product_log where entered_at < now() - '3 days'::interval "
        "ORDER by date ASC"
    )
    for row in cursor:
        date = datetime.datetime(
            year=row[0].year, month=row[0].month, day=row[0].day
        )
        date = date.replace(tzinfo=pytz.utc)
        process(DBOPTS, pgconn, date)


if __name__ == "__main__":
    main()
