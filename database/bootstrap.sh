# setup databases

# postgres 10 does not like unencrypted
psql -c "create user nobody with password 'secret';" -U postgres
psql -c "create user ldm with password 'secret';" -U postgres

psql -c "create database id3b;" -U postgres
psql -f init/id3b.sql -U postgres id3b
