"""Our fancy pants ingest of LDM product metadata"""
from __future__ import print_function
from syslog import LOG_LOCAL2
from io import BytesIO
import json
import os
import re
import datetime

from twisted.python import log, syslog
from twisted.internet import stdio
from twisted.internet import reactor
from twisted.protocols import basic
from twisted.enterprise import adbapi


from applib.parser import parser

WMO_RE = re.compile(
    (
        r"^([0-9A-Za-z]{4,6}) ([A-Z0-9]{4}) ([0-9]{6})( [A-Z]{3})?"
        r"( /p[A-Z0-9]{3,6})?"
    )
)
syslog.startLogging(prefix="id3b_ingest", facility=LOG_LOCAL2)
CFGFN = "%s/settings.json" % (
    os.path.join(os.path.dirname(__file__), "../config"),
)
CONFIG = json.load(open(CFGFN))
DBOPTS = CONFIG["databaserw"]
DBPOOL = adbapi.ConnectionPool(
    "psycopg2",
    database=DBOPTS["name"],
    cp_reconnect=True,
    cp_max=20,
    host=DBOPTS["host"],
    user=DBOPTS["user"],
    password=DBOPTS["password"],
)


def compute_wmo_time(valid, ddhhmm):
    """Attempt to resolve the time!"""
    day = int(ddhhmm[:2])
    if day < 5 and valid.day > 24:
        # Next month
        valid += datetime.timedelta(days=15)
    if day > 24 and valid.day < 5:
        # previous month
        valid -= datetime.timedelta(days=15)
    return valid.replace(
        day=day,
        hour=int(ddhhmm[2:4]),
        minute=int(ddhhmm[4:6]),
        second=0,
        microsecond=0,
    )


def handle_error(err):
    """Handle an error?"""
    print(err)


def save_msgs(txn, msgs):
    """Persist our message"""
    for msg in msgs:
        # print("%6s %s" % (msg.size, msg.product_id))
        tokens = WMO_RE.findall(msg.product_id)
        awips_id = None
        wmo_ttaaii = None
        wmo_source = None
        wmo_time = None
        wmo_bbb = None
        awips_id = None
        if tokens:
            (wmo_ttaaii, wmo_source, wmo_time, wmo_bbb, awips_id) = tokens[0]
            wmo_bbb = wmo_bbb.strip()
            awips_id = awips_id[3:]
            try:
                wmo_time = compute_wmo_time(msg.valid, wmo_time)
            except Exception as exp:
                print("%s valid: %s wmo_time: %s" % (exp, msg.valid, wmo_time))
        txn.execute(
            """
        INSERT into ldm_product_log
        (md5sum, size, valid_at, ldm_feedtype,
         seqnum, product_id, product_origin,
         wmo_ttaaii, wmo_source, wmo_valid_at, wmo_bbb, awips_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                msg.md5sum,
                msg.size,
                msg.valid,
                msg.feedtype,
                msg.seqnum,
                msg.product_id,
                msg.product_origin,
                wmo_ttaaii,
                wmo_source,
                wmo_time,
                wmo_bbb,
                awips_id,
            ),
        )


class IngestorProtocol(basic.LineReceiver):
    """Go"""

    def connectionLost(self, reason):
        """ Called when the STDIN connection is lost """
        log.msg("connectionLost")
        log.err(reason)
        reactor.callLater(15, reactor.callWhenRunning, reactor.stop)

    def dataReceived(self, data):
        """ Process a chunk of data """
        # print("Got %s bytes" % (len(data), ))
        #
        self.leftover, msgs = parser(BytesIO(self.leftover + data))
        if msgs:
            df = DBPOOL.runInteraction(save_msgs, msgs)
            df.addErrback(handle_error)
        else:
            if len(self.leftover) > 8000:
                print("ABORT RESET, leftover size is too large!")
                self.leftover = b""


class LDMProductFactory(stdio.StandardIO):
    """Go"""

    def __init__(self, protocol, **kwargs):
        """ constructor with a protocol instance """
        stdio.StandardIO.__init__(self, protocol, **kwargs)


def main():
    """Our main loop"""
    proto = IngestorProtocol()
    # Puts us into rawdata mode and not line receiver
    proto.setRawMode()
    # Something to store data between runs
    proto.leftover = b""
    _ = LDMProductFactory(proto)
    reactor.run()  # @UndefinedVariable


if __name__ == "__main__":
    main()
