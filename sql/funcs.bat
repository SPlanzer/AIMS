setlocal
set psql="C:\Program Files\postgresql\9.0\bin\psql"
set db=-h localhost -d ccrook -U batch
set p=%psql% %db%
%p% -f electoral_address_functions.sql
pause
