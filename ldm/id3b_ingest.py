"""Our fancy pants ingest of LDM product metadata"""
from __future__ import print_function
from syslog import LOG_LOCAL2
import StringIO
import json
import os

from twisted.python import log, syslog
from twisted.internet import stdio
from twisted.internet import reactor
from twisted.protocols import basic
from twisted.internet import task
from twisted.enterprise import adbapi


from applib.parser import parser

syslog.startLogging(prefix='id3b_ingest', facility=LOG_LOCAL2)
CFGFN = "%s/settings.json" % (os.path.join(os.path.dirname(__file__),
                                           "../config"),)
CONFIG = json.load(open(CFGFN))
DBOPTS = CONFIG['databaserw']
DBPOOL = adbapi.ConnectionPool('psycopg2', database=DBOPTS['name'],
                               cp_reconnect=True, cp_max=20,
                               host=DBOPTS['host'],
                               user=DBOPTS['user'],
                               password=DBOPTS['password'])


def handle_error(err):
    """Handle an error?"""
    print(err)


def save_msgs(txn, msgs):
    """Persist our message"""
    for msg in msgs:
        # print("%6s %s" % (msg.size, msg.product_id))
        txn.execute("""
        INSERT into ldm_product_log
        (md5sum, size, valid_at, ldm_feedtype,
         seqnum, product_id, product_origin)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (msg.md5sum, msg.size, msg.valid, msg.feedtype,
              msg.seqnum, msg.product_id, msg.product_origin))


class IngestorProtocol(basic.LineReceiver):
    """Go"""

    def connectionLost(self, reason):
        ''' Called when the STDIN connection is lost '''
        log.msg('connectionLost')
        log.err(reason)
        reactor.callLater(15, reactor.callWhenRunning, reactor.stop)

    def dataReceived(self, data):
        ''' Process a chunk of data '''
        # print("Got %s bytes" % (len(data), ))
        #
        self.leftover, msgs = parser(StringIO.StringIO(self.leftover + data))
        if msgs:
            df = DBPOOL.runInteraction(save_msgs, msgs)
            df.addErrback(handle_error)
        else:
            if len(self.leftover) > 8000:
                print("ABORT RESET, leftover size is too large!")
                self.leftover = ""


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
    reactor.run()


if __name__ == '__main__':
    main()
