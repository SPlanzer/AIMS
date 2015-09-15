#!/bin/sh
db='-h devgeo01 -d ngo_db -U ccrook-u'
psql $db -c "DROP SCHEMA IF EXISTS electoral_address CASCADE"
psql $db -f electoral_roles.sql
psql $db -f electoral_address_schema.sql
psql $db -f electoral_address_functions.sql
psql $db -f system_data.sql
psql $db -f road_type_codes.sql
#psql $db -f test_source_types.sql
#psql $db -f test_suppliers.sql

