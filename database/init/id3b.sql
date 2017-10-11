-- Our database schema
CREATE TABLE ldm_product_log(
  entered_at timestamptz DEFAULT now(),
  md5sum char(32),
  size int,
  valid_at timestamptz,
  ldm_feedtype int,
  seqnum int,
  product_id varchar,
  product_origin varchar,
  wmo_ttaaii char(6),
  wmo_source char(4),
  wmo_valid_at timestamptz,
  wmo_bbb char(3),
  awips_id varchar(6)
);

CREATE INDEX ldm_product_log_wmo_source_idx on ldm_product_log(wmo_source);
CREATE INDEX ldm_product_log_wmo_ttaaii_idx on ldm_product_log(wmo_ttaaii);
CREATE INDEX ldm_product_log_awips_id_idx on ldm_product_log(awips_id);

GRANT ALL on ldm_product_log to ldm;
GRANT SELECT on ldm_product_log to nobody;