# id3b
Unidata IDD Database

The purpose of this repository is to create an LDM ingest tool and website that
displays a catalog of what flows over the [Unidata IDD](http://www.unidata.ucar.edu/projects/index.html#idd). This is a project born out of the Unidata Users Committe.

This code takes advantage of a nice feature of [pqact](https://www.unidata.ucar.edu/software/ldm/ldm-current/basics/pqact.conf.html) whereby product metadata is set over the pqact PIPE action

Causes the metadata of the data-product to be written to the file before any 
data. The metadata is written in the following order using the indicated binary data-types of the C language:

* Metadata-length in bytes (uint32_t)
* Data-product signature (MD5 checksum) (uchar[16])
* Data-product size in bytes (uint32_t)
* Product creation-time in seconds since the epoch:
    * Integer portion (uint64_t)
    * Microseconds portion (int32_t)
* Data-product feedtype (uint32_t)
* Data-product sequence number (uint32_t)
* Product-identifier:
    * Length in bytes (excluding NUL) (uint32_t)
    * Non-NUL-terminated string (char[])
* product-origin:
    * Length in bytes (excluding NUL) (uint32_t)
    * Non-NUL-terminated string (char[])
