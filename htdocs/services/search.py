"""Service for searching for products"""
import datetime
import json

import psycopg
from paste.request import parse_formvars

# protocol2/ldm5.h
LDM_FEEDTYPE_XREF = {
    4: "HDS",
    11: "IDS|DDPLUS",
    32: "UNIWISC",
    4096: "CONDUIT",
    8192: "FNEXRAD",
    16384: "LIGHTNING",
    2097152: "NIMAGE",
    8388608: "NGRID",
    134217728: "NEXRAD",
    268435456: "NEXRAD2",
    1073741824: "EXP",
}


def get_subsql(colname, fullwidth, param):
    """Generate fancy sql subquery with some optimizations"""
    if len(param) == fullwidth:
        return f" {colname} = %s"
    return f" strpos({colname}, %s) > 0 "


def do_search(wmo_ttaaii, wmo_source, awips_id, product_id):
    """Make search great again"""
    sts = datetime.datetime.utcnow()
    pgconn = psycopg.connect(
        dbname="id3b", host="iemdb-id3b.local", user="nobody"
    )
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
    if product_id != "":
        sql.append(get_subsql("product_id", -1, product_id))
        args.append(product_id)
    if sql:
        sql = f"({' and '.join(sql)})"
    else:
        sql = "(awips_id = %s and wmo_source = %s)"
        args = ("ADDMX", "KDMX")

    cursor.execute(
        f"""
    SELECT ldm_feedtype, wmo_ttaaii, wmo_source,
    to_char(entered_at at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as eat,
    size, product_id, awips_id,
    to_char(valid_at at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as vat,
    to_char(wmo_valid_at at time zone 'UTC', 'YYYY-MM-DDThh24:MI:SSZ') as wat
    from ldm_product_log where {sql}
    ORDER by entered_at DESC LIMIT 500
    """,
        args,
    )
    res = {"products": []}
    for row in cursor:
        res["products"].append(
            {
                "feedtype": LDM_FEEDTYPE_XREF.get(row[0], str(row[0])),
                "wmo_ttaaii": row[1],
                "wmo_source": row[2],
                "entered_at": row[3],
                "size": row[4],
                "product_id": row[5],
                "awips_id": row[6],
                "valid_at": row[7],
                "wmo_valid_at": row[8],
            }
        )
    pgconn.close()
    res["generation_time[secs]"] = round(
        (datetime.datetime.utcnow() - sts).total_seconds(), 3
    )
    res["generated_at"] = sts.strftime("%Y-%m-%dT%H:%M:%SZ")
    return json.dumps(res)


def application(environ, start_response):
    """Attempt to do the right thing"""
    fields = parse_formvars(environ)
    awips_id = fields.get("awips_id", "")[:6].upper()
    wmo_source = fields.get("wmo_source", "")[:4].upper()
    wmo_ttaaii = fields.get("wmo_ttaaii", "")[:6].upper()
    product_id = fields.get("product_id", "")
    res = do_search(wmo_ttaaii, wmo_source, awips_id, product_id)
    start_response("200 OK", [("Content-type", "application/json")])
    return [res.encode("ascii")]
