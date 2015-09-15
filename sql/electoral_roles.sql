CREATE ROLE electoral_admin
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE;
ALTER ROLE electoral_admin SET search_path=electoral_address, bde, public;

CREATE ROLE electoral_dba
  SUPERUSER INHERIT CREATEDB CREATEROLE;
ALTER ROLE electoral_dba SET search_path=electoral_address, bde, public;

CREATE ROLE electoral_user
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE;
ALTER ROLE electoral_user SET search_path=electoral_address, bde, public;
