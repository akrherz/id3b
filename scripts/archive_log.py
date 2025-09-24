"""Archive the ldm_product_log content for a given date

python archive_log.py
"""

import subprocess
from datetime import datetime, timedelta, timezone

from psycopg import Connection
from pyiem.database import get_dbconn


def process(pgconn: Connection, dt: datetime):
    """Process this date please"""
    cursor = pgconn.cursor("streamer")
    cursor.execute(
        """
    select
    to_char(entered_at at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS'),
    md5sum, size,
    to_char(valid_at at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS'),
    ldm_feedtype, seqnum, product_id,
    replace(product_origin, ',', '_'), wmo_ttaaii, wmo_source,
    to_char(wmo_valid_at at time zone 'UTC', 'YYYY-MM-DD HH24:MI:SS'),
    wmo_bbb, awips_id from ldm_product_log WHERE entered_at < %s
    """,
        (dt + timedelta(hours=24),),
    )

    csvfn = dt.strftime("/mesonet/tmp/%Y%m%d.csv")
    with open(csvfn, "w") as fh:
        fh.write(
            "entered_at,md5sum,size,valid_at,ldm_feedtype,seqnum,"
            "product_id,product_origin,wmo_ttaaii,wmo_source,wmo_valid_at,"
            "wmo_bbb,awips_id\n"
        )
        for row in cursor:
            fh.write(",".join([str(s) for s in row]) + "\n")
    cursor.close()
    # Now bz2 this file
    subprocess.call(["bzip2", csvfn])
    cursor = pgconn.cursor()
    cursor.execute(
        "DELETE from ldm_product_log where entered_at < %s",
        (dt + timedelta(hours=24),),
    )
    cursor.close()
    pgconn.commit()
    remotedir = dt.strftime("/offline/id3b/%Y/%m")
    cmd = [
        "rsync",
        "-a",
        "--remove-source-files",
        "--rsync-path",
        f"mkdir -p {remotedir} && rsync",
        f"{csvfn}.bz2",
        f"meteor_ldm@akrherz-desktop.agron.iastate.edu:{remotedir}",
    ]
    subprocess.call(cmd)


def main():
    """Go Main Go"""
    # Compute 3 days ago
    dt = datetime.now() - timedelta(days=3)
    dt = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
    pgconn = get_dbconn("id3b")
    process(pgconn, dt)


if __name__ == "__main__":
    main()
