"""My parser"""

import struct
from collections import namedtuple
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

EPOCH = datetime(1970, 1, 1)
METAMSG = namedtuple(
    "METAMSG",
    [
        "md5sum",
        "size",
        "valid",
        "feedtype",
        "seqnum",
        "product_id",
        "product_origin",
    ],
)


def parser(bindata):
    """Process this bindata"""
    res = []
    leftover = b""
    while True:
        sample = bindata.read(4)
        if not sample:
            break
        if len(sample) != 4:
            leftover = sample
            break
        msgsize = struct.unpack("I", sample)[0]
        # msgsize includes the msgsize :/
        msgdata = bindata.read(msgsize - 4)
        if len(msgdata) != (msgsize - 4):
            # short read
            leftover = sample + msgdata
            break
        bindata.seek(bindata.tell() - (msgsize - 4))
        md5sum = "".join(
            [format(i, "02x") for i in struct.unpack("16B", bindata.read(16))]
        )
        prodsize = struct.unpack("I", bindata.read(4))[0]
        (seconds, microseconds) = struct.unpack("Qi", bindata.read(12))
        seconds += microseconds / 1000000.0
        valid = EPOCH + timedelta(seconds=seconds)
        valid = valid.replace(tzinfo=ZoneInfo("UTC"))
        feedtype = struct.unpack("I", bindata.read(4))[0]
        seqnum = struct.unpack("I", bindata.read(4))[0]
        prodid_size = struct.unpack("I", bindata.read(4))[0]
        prodid = "".join(
            chr(i)
            for i in struct.unpack(
                str(prodid_size) + "B", bindata.read(prodid_size)
            )
        )
        po_size = struct.unpack("I", bindata.read(4))[0]
        prod_orig = "".join(
            chr(i)
            for i in struct.unpack(str(po_size) + "B", bindata.read(po_size))
        )
        if seconds == 0:
            print("    skipping pqact initial empty message")
            continue
        res.append(
            METAMSG(
                md5sum=md5sum,
                size=prodsize,
                valid=valid,
                feedtype=feedtype,
                seqnum=seqnum,
                product_id=prodid,
                product_origin=prod_orig,
            )
        )
    return leftover, res
