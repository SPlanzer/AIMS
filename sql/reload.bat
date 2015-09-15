setlocal
set psql="C:\Program Files (x86)\PostgreSQL\8.4\bin\psql"
set db=-h devgeo01 -d ngo_db -U splanzer
set p=%psql% %db%
%p% -c "DROP SCHEMA IF EXISTS electoral_address CASCADE"
%p% -f electoral_address_schema.sql
%p% -f electoral_address_functions.sql
%p% -f road_type_codes.sql
%p% -f system_data.sql
rem %p% -f test_source_types.sql
rem p% -f test_suppliers.sql
pause
