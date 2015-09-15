-- DROP SCHEMA IF EXISTS electoral_address CASCADE;

SET client_min_messages=WARNING;

SET ROLE electoral_dba;

CREATE SCHEMA electoral_address AUTHORIZATION electoral_dba;

GRANT USAGE ON SCHEMA electoral_address TO electoral_admin;
GRANT USAGE ON SCHEMA electoral_address TO electoral_user;

SET SEARCH_PATH TO electoral_address, public;

-- ------------------------------------------------------------------------ 

CREATE TABLE code
(
    code_type VARCHAR(32) NOT NULL,
    code VARCHAR(32) NOT NULL,
    value text,
    PRIMARY KEY (code_type, code)
);

COMMENT ON TABLE code IS
$comment$
code is a table of system codes values.  Defines a sets of code/value pairs
for each code_type.  The meaning of each code type is defined by the 
code/value pairs with code_type "code_type"!
$comment$;

REVOKE ALL ON TABLE code FROM PUBLIC;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE code TO electoral_admin;
GRANT SELECT ON TABLE code TO electoral_user;

INSERT INTO code (code_type, code, value) VALUES 
('code_type','sys_code_type','System code types in this table'),
('code_type','code_type','User code types in this table');

-- ------------------------------------------------------------------------ 

CREATE TABLE source_type
(
    stp_id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    fileext VARCHAR(10) NOT NULL,
    srsid INT NOT NULL,
    reader_type VARCHAR(32) NOT NULL,
    reader_params VARCHAR(256) NOT NULL,
    ACTIVE BOOLEAN NOT NULL DEFAULT 't'
);

COMMENT ON TABLE source_type IS
$comment$
source_type is an application table used to manage the different data sources
used by the application.  It is principally for use by the application.

stp_id - system id for the source type
name - the user visible name of the source
fileext - the file extension for datafiles for this source
srsid - the spatial reference system id for this source
reader_type - the name of the Python class used to read this source
reader_params - the parameters used by the reader

The parameters are entered as a string in which the first character 
is a delimiter used to split the remainder of the string.  The remainder
is a set of name value pairs defining the parameters. 
$comment$;

REVOKE ALL ON TABLE source_type FROM PUBLIC;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE source_type TO electoral_admin;
GRANT USAGE ON SEQUENCE source_type_stp_id_seq TO electoral_admin;
GRANT SELECT ON TABLE source_type TO electoral_user;
GRANT USAGE ON SEQUENCE source_type_stp_id_seq TO electoral_user;

-- ------------------------------------------------------------------------ 

CREATE TABLE supplier
(
    sup_id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    stp_id int NOT NULL
       REFERENCES source_type(stp_id),
    stt_id INT,
    active BOOLEAN NOT NULL DEFAULT 't'
);

COMMENT ON TABLE supplier IS
$comment$
supplier holds a list of suppliers of address information

sup_id - system id for the supplier type
name - the user name for the supplier
stp_id - the source type used by the supplier
stt_id - id of the supplier TA in the crs_statist_area table
active - current active status of the supplier, either Y or N

$comment$;

REVOKE ALL ON TABLE supplier FROM PUBLIC;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE supplier TO electoral_admin;
GRANT USAGE ON SEQUENCE supplier_sup_id_seq TO electoral_admin;
GRANT SELECT ON TABLE supplier TO electoral_user;
GRANT USAGE ON SEQUENCE supplier_sup_id_seq TO electoral_user;

-- ------------------------------------------------------------------------ 

CREATE TABLE upload
(
    upl_id SERIAL NOT NULL PRIMARY KEY,
    created_by name NOT NULL,
    creation_time TIMESTAMP NOT NULL DEFAULT clock_timestamp(),
    filename TEXT
);

ALTER TABLE upload OWNER TO electoral_dba;
REVOKE ALL ON TABLE upload FROM PUBLIC;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE upload TO electoral_admin;
GRANT USAGE ON SEQUENCE upload_upl_id_seq TO electoral_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE upload TO electoral_user;
GRANT USAGE ON SEQUENCE upload_upl_id_seq TO electoral_user;

COMMENT ON TABLE upload IS
$comment$
Defines an electoral address upload dataset for Landonline

Fields:
upl_id - primary key
created_by - user creating the upload
creation_time - date at which the upload was created
filename - the last filename used for the upload file
$comment$;

-- ------------------------------------------------------------------------ 

CREATE TABLE job
(
    job_id SERIAL NOT NULL PRIMARY KEY,
    created_by name NOT NULL,
    description text,
    source_name text,
    notes text,
    sup_id int NOT NULL
       REFERENCES supplier(sup_id),
    stp_id int NOT NULL
       REFERENCES source_type(stp_id),
    upl_id INT
       REFERENCES upload(upl_id),
    creation_time TIMESTAMP NOT NULL DEFAULT clock_timestamp(),
    completed_time TIMESTAMP,
    uploaded_time TIMESTAMP,
    status CHAR(1) NOT NULL DEFAULT 'N',
    link_date DATE,
    -- Configuration settings
    road_search_radius DOUBLE PRECISION DEFAULT 2000.0,
    same_address_tolerance DOUBLE PRECISION DEFAULT 500.0,
    same_location_tolerance DOUBLE PRECISION DEFAULT 0.10
);

ALTER TABLE job OWNER TO electoral_dba;
REVOKE ALL ON TABLE job FROM PUBLIC;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE job TO electoral_admin;
GRANT USAGE ON SEQUENCE job_job_id_seq TO electoral_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE job TO electoral_user;
GRANT USAGE ON SEQUENCE job_job_id_seq TO electoral_user;

DELETE FROM code WHERE code_type='job_status';
DELETE FROM code where code_type='sys_code_type' AND code='job_status';

INSERT INTO code( code_type, code, value )
values 
('sys_code_type','job_status','Status of the address update job'),
('job_status','N','New job'),
('job_status','P','Work in progress'),
('job_status','C','Completed'),
('job_status','D','Deleted'),
('job_status','U','Uploaded');

COMMENT ON TABLE job IS
$comment$
Defines an electoral address update job

Fields:
job_id - primary key
created_by - user creating the job
description - description of job
source_name - usually the file name of the original data set
notes - user text field for accumulating notes
sup_id - references the supplier table
stp_id - references the source_type table
creation_time - date at which the job was created
completed_time - date of the last update to the data
uploaded_time - date at which the data was flagged as uploaded
   (Landonline upload SQL generated)
status - current status of the job - reference code_type 'job_status'
link_date - date at which Landonline links were last updated

Configuration settings
road_search_radius - default radius for seeking roads matching supplied name
same_address_tolerance - default radius for seeking moved address (ie same number and roadname at different location)
same_location_tolerance - default radius for seeking edited address (ie different number/roadname at same location)

$comment$;

-- ------------------------------------------------------------------------ 

CREATE TABLE address
(
    adr_id SERIAL NOT NULL PRIMARY KEY,
    job_id INT NOT NULL
       REFERENCES job(job_id),
    src_id varchar(32),
    src_status char(4) DEFAULT 'UNKN',
    src_roadname varchar(100) NOT NULL,
    src_housenumber varchar(25) NOT NULL,
    src_comment text NOT NULL DEFAULT '',
    housenumber varchar(25) NOT NULL,
    range_low int,
    range_high int,
    status char(4) DEFAULT 'UNKN',
    warning_codes varchar(32) DEFAULT '' NOT NULL,
    warnings_accepted varchar(32) DEFAULT '' NOT NULL,
    notes text DEFAULT '',
    rna_id INT,
    rcl_id INT,
    sad_id INT,
    sad_sufi INT,
    sad_par_id INT,
    par_id INT,
    par_sad_count INT,
    par_range_low INT,
    par_range_high INT,
    mbk_id INT,
    cluster_id varchar(16),
    linked BOOLEAN DEFAULT FALSE,
    merge_adr_id INT DEFAULT NULL,
    ismerged BOOLEAN DEFAULT FALSE,
    shape GEOMETRY,
    src_shape GEOMETRY,

    CONSTRAINT enforce_dims_shape CHECK ((public.ndims(shape) = 2)),
    CONSTRAINT enforce_geotype_shape CHECK (((GeometryType(shape) = 'POINT'::text) OR (shape IS NULL))),
    CONSTRAINT enforce_srid_shape CHECK ((srid(shape) = 4167)),

    CONSTRAINT enforce_dims_src_shape CHECK ((public.ndims(src_shape) = 2)),
    CONSTRAINT enforce_geotype_src_shape CHECK (((GeometryType(src_shape) = 'POINT'::text) OR (src_shape IS NULL))),
    CONSTRAINT enforce_srid_src_shape CHECK ((srid(src_shape) = 4167))
);

CREATE INDEX address_job_adr_index ON address( job_id, adr_id );
CREATE INDEX address_shape_index ON address USING gist (shape);

DELETE FROM geometry_columns
WHERE
    f_table_catalog='' AND
    f_table_schema=current_schema() AND
    f_table_name='address';

INSERT INTO geometry_columns (
    f_table_catalog, f_table_schema, f_table_name, f_geometry_column, coord_dimension, srid, type
)
VALUES
    ('', current_schema(), 'address',    'shape', 2, 4167, 'POINT');

DELETE FROM code WHERE code_type='address_status';
DELETE FROM code where code_type='sys_code_type' AND code='address_status';

INSERT INTO code( code_type, code, value )
values 
('sys_code_type','address_status','Status of the address update item'),
('address_status','UNKN','Undefined'),
('address_status','BADR','Invalid road name'),
('address_status','BADG','Invalid geometry'),
('address_status','BADN','Invalid road number'),
('address_status','REPL','Replace address'),
('address_status','NEWA','New address'),
('address_status','DELE','Delete address'),
('address_status','IGNR','Ignore'),
('address_status','MERG','Merged into new address');

DELETE FROM code WHERE code_type='address_warning';
DELETE FROM code where code_type='sys_code_type' AND code='address_warning';

INSERT INTO code( code_type, code, value )
values 
('sys_code_type','address_warning','Warnings relating to the address'),
('address_warning','BADR','Address doesn''t match a nearby Landonline road'),
('address_warning','BADG','Address has no point location'),
('address_warning','MDIF','Replacing an address point on a different parcel'),
('address_warning','MSAD','There are other address points on the parcel'),
('address_warning','BDTA','Invalid TA for supplier'),
('address_warning','BADN','Invalid formatted number'),
('address_warning','NUMM','Number has been modified'),
('address_warning','RNGI','Range inconsistent with existing addresses on parcel'),
('address_warning','SHPM','Address point location has been shifted')
;

ALTER TABLE address OWNER TO electoral_dba;
REVOKE ALL ON TABLE address FROM PUBLIC;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE address TO electoral_admin;
GRANT USAGE ON SEQUENCE address_adr_id_seq to electoral_admin;
GRANT SELECT, UPDATE, INSERT, DELETE ON TABLE address TO electoral_user;
GRANT USAGE ON SEQUENCE address_adr_id_seq to electoral_user;

COMMENT ON TABLE address IS
$comment$
Defines an addess in an electoral address update job

Fields:
adr_id - unique id for the record
job_id - the job from which this is loaded
status - a status code from the 'address_status' code type list
src_id - reference id from supplier to assist querying etc
src_status - status from the supplier (to allow delete specification)
src_roadname - supplied roadname
src_housenumber - supplied house number
src_comment - comment from supplier regarding the address
warning_codes - space separated list of codes referencing code type address_warning
notes - use notes
housenumber - the house number (may be edited after supplied)
range_low - lowest number in range
range_high - lowest number in range
rna_id - link to landonline road name record
rcl_id - link to landonline centreline
sad_id - link to landonline street address
sad_par_id - landonline primary parcel holding linked address
par_id - landonline primary parcel holding the address point
par_sad_count - Count of landonline address points on the same parcel
par_range_low - Lowest numbered address point on parcel
par_range_high - Highest numbered address point on parcel
mbk_id - Meshblock id, used for linking to territorial authority
cluster_id - Identifies spatial clusters within the data set
linked - True if landonline links are up to date
merge_adr_id - id of merged address replacing this address (ie from merging a range of supplied addresses into a single address)
ismerged - true if this is a merged from a group of supplied addresses
shape - point geometry locating the record (may be edited)
src_shape - original point geometry locating the record

$comment$;


-- Function to determine the status of a mark

CREATE OR REPLACE FUNCTION electoral_address._elc_trg_SetAddressStatus ()
RETURNS TRIGGER
AS
$body$
DECLARE
    l_warning address.warning_codes%type;
    l_stt_id INT;
    l_numberre TEXT;
    l_match TEXT[];
    l_numvalid INT;
    l_status job.status%type;
    l_range_tolerance INT;
BEGIN
    l_range_tolerance := 10;

    SELECT 
        sup.stt_id,
        job.status
    INTO
        l_stt_id,
        l_status
    FROM
       job
       JOIN supplier sup ON sup.sup_id = job.sup_id
    WHERE
       job.job_id = NEW.job_id;

    IF l_status = 'U' THEN
        RAISE EXCEPTION 'Cannot update address after job has been uploaded to Landonline';
    END IF;

    -- Valid forms of numbers accepted by this re and from which range low
    -- and high are extracted

    -- Note the number validation and number range extraction is also implemented   -- in AddressEditorWidget.extractNumberRange, and that code should match this.

    l_numberre = E'^(?:' ||
        -- 12-23, 15A-23B
        E'(\\d+)[A-Z]*(?:\\-(\\d+)[A-Z]*)?|' ||
        -- 1/44-5/44 , 1A/83C-5B/83C
        E'[A-Z]{0,2}\\d+[A-Z]*\\/((\\d+)[A-Z]*)(?:\\-[A-Z]{0,2}\\d+[A-Z]*\\/\\3)?|' ||
        -- R/1234A
        E'R\\/(\\d+)[A-Z]' ||
        -- If all else fails match anything so that regexp_matches always
        -- returns a row.
        E'|.*)$';

    SELECT * INTO l_match FROM regexp_matches(NEW.housenumber,l_numberre) LIMIT 1;
    NEW.range_low := COALESCE(l_match[1],l_match[4],l_match[5])::INT;
    NEW.range_high := l_match[2]::INT;

    -- Check that the range if valid - reset range_high to null if same
    -- as range low, set both to NULL (ie invalid address) if high is less
    -- than low

    IF NEW.range_high = NEW.range_low THEN NEW.range_high := NULL; END IF;

    IF NEW.range_high < NEW.range_low THEN
        NEW.range_low := NULL;
        NEW.range_high := NULL;
    END IF;

    NEW.status := 
        CASE 
            WHEN NEW.status = 'IGNR' THEN 'IGNR'
            WHEN NEW.shape IS NULL THEN 'BADG'
            WHEN NEW.rna_id IS NULL THEN 'BADR'
            WHEN NEW.range_low IS NULL THEN 'BADN'
            WHEN NEW.merge_adr_id IS NOT NULL THEN 'MERG'
            WHEN NEW.src_status = 'DELE' AND NEW.sad_id IS NULL THEN 'UNKN'
            WHEN NEW.src_status = 'DELE' AND NEW.sad_id IS NOT NULL THEN 'DELE'
            WHEN NEW.status = 'NEWA' THEN 'NEWA'
            WHEN NEW.status = 'REPL' AND NEW.sad_id IS NULL THEN 'UNKN'
            WHEN NEW.status = 'REPL' AND NEW.sad_id IS NOT NULL THEN 'REPL'
            -- Default action is to replace if we've already defined a matched address point
            -- otherwise no action - up to user to set to set to NEWA explicitly
            ELSE 'UNKN'
        END;

    -- Set warning codes
    
    l_warning := '';
    IF NEW.status <> 'MERG' AND NEW.status <> 'IGNR' THEN

        IF NEW.status = 'BADG' THEN
            l_warning = 'BADG';
        END IF;

        IF NEW.warnings_accepted NOT LIKE '%BADR%' AND NEW.shape IS NULL THEN
           l_warning := l_warning || ' BADR';
        END IF;

        IF NEW.warnings_accepted NOT LIKE '%BADN%' AND NEW.range_low IS NULL THEN
           l_warning := l_warning || ' BADN';
        END IF;

        IF NEW.warnings_accepted NOT LIKE '%MDIF%' AND NEW.sad_par_id <> NEW.par_id AND NEW.status = 'REPL' THEN
            l_warning := 'MDIF';
        END IF;

        IF NEW.warnings_accepted NOT LIKE '%MSAD%' AND NEW.par_sad_count > 1 AND NEW.status = 'REPL' THEN
            l_warning := l_warning || ' MSAD';
        END IF;

        IF NEW.warnings_accepted NOT LIKE '%MSAD%' AND NEW.par_sad_count > 0 AND NEW.status = 'NEWA' THEN
            l_warning := l_warning || ' MSAD';
        END IF;

        IF NEW.warnings_accepted NOT LIKE '%SHPM%' AND NOT (NEW.src_shape = NEW.shape) THEN
            l_warning := l_warning || ' SHPM';
        END IF;

        IF NEW.warnings_accepted NOT LIKE '%NUMM%' AND NOT (NEW.src_housenumber = NEW.housenumber) THEN
            -- If manually updated then accept modified number
            IF TG_OP='UPDATE' THEN
                IF  NEW.housenumber <> OLD.housenumber THEN
                    NEW.warnings_accepted = NEW.warnings_accepted || ' NUMM';
                ELSE
                    l_warning := l_warning || ' NUMM';
                END IF;
            ELSE
                l_warning := l_warning || ' NUMM';
            END IF;
        END IF;

        IF NEW.range_low IS NOT NULL AND NEW.par_range_low IS NOT NULL AND NEW.warnings_accepted NOT LIKE '%RNGI%' THEN
            IF NEW.range_low < NEW.par_range_low-l_range_tolerance OR
               (COALESCE(NEW.range_high,NEW.range_low)) > NEW.par_range_high+l_range_tolerance THEN
                l_warning := l_warning || ' RNGI';
            END IF;
        END IF;
    
        IF NEW.mbk_id IS NOT  NULL THEN
            IF NEW.warnings_accepted NOT LIKE '%BDTA%' AND 
                elc_MeshblockTA(NEW.mbk_id) != l_stt_id THEN
                l_warning := l_warning || ' BDTA';
            END IF;
        END IF;
    END IF;

    NEW.warning_codes := TRIM(l_warning);
    
    NEW.warnings_accepted := TRIM(REPLACE(REPLACE(NEW.warnings_accepted,'BDTA',''),'  ',' '));

    IF TG_OP = 'UPDATE' THEN
        IF NOT (NEW.shape = OLD.shape) THEN
            NEW.linked = FALSE;
        END IF;
    END IF;

    RETURN NEW;
END
$body$
LANGUAGE plpgsql
SET search_path FROM CURRENT;


CREATE TRIGGER address_status_trigger BEFORE INSERT OR UPDATE ON address
    FOR EACH ROW EXECUTE PROCEDURE _elc_trg_SetAddressStatus();
