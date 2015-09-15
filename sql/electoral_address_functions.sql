SET SEARCH_PATH TO electoral_address, bde, public;
SET client_min_messages=WARNING;

CREATE OR REPLACE FUNCTION _dropFunctions()
RETURNS integer
AS
$body$
DECLARE
   pcid text;
BEGIN
    FOR pcid IN 
        SELECT proname || '(' || pg_get_function_identity_arguments(oid) || ')'
        FROM pg_proc 
        WHERE pronamespace=(SELECT oid FROM pg_namespace WHERE nspname ILIKE 'electoral_address')  
        AND proname NOT ILIKE '_dropFunctions'
        AND proname NOT ILIKE '_elc_trg_%'
    LOOP
        EXECUTE 'DROP FUNCTION ' || pcid;
    END LOOP;
    RETURN 1;
END
$body$
LANGUAGE plpgsql;

SELECT _dropFunctions();

DROP FUNCTION _dropFunctions();

-- Update the point geometry for an address

CREATE OR REPLACE FUNCTION electoral_address.elc_CreateAddressPoint
(
    p_id int,
    p_pointwkt varchar(100)
)
RETURNS BOOLEAN
AS
$body$
DECLARE
    l_point GEOMETRY;
BEGIN

    l_point := ST_PointFromText( p_pointwkt, 4167 );

    IF ST_IsValid(l_point) THEN
        UPDATE address SET shape = l_point WHERE adr_id = p_id;
        RETURN elc_RefreshAddressLinks(p_id);
    ELSE
        RAISE EXCEPTION 'elc_CreateAddressPoint: Invalid geometry %', p_pointwkt;
    END IF;
END
$body$
LANGUAGE plpgsql;


-- Clean appellation

CREATE OR REPLACE FUNCTION electoral_address.elc_cleanappellation
(
    appellation text
)
RETURNS text
AS
$body$
DECLARE
    str text;
BEGIN
    str = regexp_replace(
                 trim(upper($1)),
                 E'(\\W|^)(DEPOSITED PLAN|DEPOSIT PLAN||DEPOSIT PLAN|DEP PLN|DEP PLAN|DEPOSIT|DPSTPLN|DPLN|DEPO|DEP)(\\W|$)', E'\\1DP\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(DEPOSITED SURVEY|DEPSUR|DEPS|SP)(\\W|$)', E'\\1DPS\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(SURVEY OFFICE|SURVOFF)(\\W|$)', E'\\1SO\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(LOTS|LTS|LT)(\\W|$)', E'\\1LOT\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(SECTION|SECTIONS|SECTN|SCTN|SECTN|SEC)(\\W|$)', E'\\1SECT\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(FLT|FLATS)(\\W|$)', E'\\1FLAT\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(AREAS|ARE)(\\W|$)', E'\\1AREA\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(UNIT|UNT)(\\W|$)', E'\\1UNIT\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(ALLOTMENT|ALLOT|ALLTMNT|ALLOTMNT)(\\W|$)', E'\\1ALLT\\3', 'g'
             );
    str = regexp_replace(
                 trim(upper(str)),
                 E'(\\W|^)(GARAGE|GRG)(\\W|$)', E'\\1GRGE\\3', 'g'
             );                
    RETURN str;
END
$body$
LANGUAGE plpgsql;

-- Extract appellation parts

CREATE OR REPLACE FUNCTION electoral_address.elc_getappellationparceltype
(
    appellation text
)
RETURNS text
AS
$body$
DECLARE
    array text[];
BEGIN
    array := regexp_matches(
                 trim(upper(electoral_address.elc_cleanappellation($1))),
                 E'(\\W|^)(SECT|LOT|AREA|FLAT|AU|UNIT|ALLT|GRGE|SHED|EASM|CARP|PRIN|FDU)(\\W)(\\w*)'
             );
    if array_length(array, 1) > 2 then
        if array[2] is not null then
            RETURN array[2];
        else
            RETURN NULL;
        end if;
    else
        RETURN NULL;
    end if;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_getappellationparcelvalue
(
    appellation text
)
RETURNS text
AS
$body$
DECLARE
    array text[];
BEGIN
    array := regexp_matches(
                 trim(upper(electoral_address.elc_cleanappellation($1))),
                 E'(\\W|^)(SECT|LOT|AREA|FLAT|AU|UNIT|ALLT|GRGE|SHED|EASM|CARP|PRIN|FDU)(\\W)(\\w*)'
             );
    if array_length(array, 1) > 3 then
        if array[4] is not null then
            RETURN array[4];
        else
            RETURN NULL;
        end if;
    else
        RETURN NULL;
    end if;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_getappellationsubtype
(
    appellation text
)
RETURNS text
AS
$body$
DECLARE
    array text[];
BEGIN
    array := regexp_matches(
                 trim(upper(electoral_address.elc_cleanappellation($1))),
                 E'(\\W|^)(DP|DPS|SO|SURD|TOWO|PARO|DEED|RS|DIST|PARH|HUND|SETT|TOSO|RES|SUBS|SQUE|VILO|CITO|BLK|BLOCK)(\\W)(\\w*)'
             );
    if array_length(array, 1) > 1 then
        if array[2] is not null then
            RETURN array[2];
        else
            RETURN NULL;
        end if;
    else
        RETURN NULL;
    end if;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_getappellationvalue
(
    appellation text
)
RETURNS text
AS
$body$
DECLARE
    array text[];
BEGIN
    array := regexp_matches(
                 trim(upper(electoral_address.elc_cleanappellation($1))),
                 E'(\\W|^)(DP|DPS|SO|SURD|TOWO|PARO|DEED|RS|DIST|PARH|HUND|SETT|TOSO|RES|SUBS|SQUE|VILO|CITO|BLK|BLOCK)(\\W)(\\w*)'
             );
    if array_length(array, 1) > 3 then
        if array[4] is not null then
           RETURN array[4];
        else
           RETURN NULL;
        end if;
    else
        RETURN NULL;
    end if;
END
$body$
LANGUAGE plpgsql;

-- TODO: Function to retrieve a unique land district from a TA code (if possible). ST_Intersect performance poor for such large polys (simplify?)

-- Function to retrieve the parcel id for an appellation and land district

CREATE OR REPLACE FUNCTION electoral_address.elc_findparcelid
(
    appellation text,
    ld_code int
) 
RETURNS TABLE
(
    par_id int
) AS 
$body$
DECLARE 
    parcel_type text;
    parcel_value text;
    sub_type text;
    appellation_value text;
BEGIN
    appellation_value = electoral_address.elc_getappellationvalue(appellation);
    parcel_type = electoral_address.elc_getappellationparceltype(appellation);
    parcel_value = electoral_address.elc_getappellationparcelvalue(appellation);
    sub_type = electoral_address.elc_getappellationsubtype(appellation);
    
    IF $2 IS NOT NULL THEN  
        RETURN QUERY
            select 
               a.par_id
            from 
               crs_appellation a,
               crs_parcel p
            where
               a.par_id = p.id
            and
               a.status = 'CURR'
            and
               a.parcel_type = parcel_type
            and 
               a.parcel_value = parcel_value
            and 
               a.sub_type = sub_type
            and 
               a.appellation_value = appellation_value
            and
               p.ldt_loc_id = $2
    	    limit 1
            ;
    ELSE
        RETURN QUERY
            select 
               a.par_id
            from 
               crs_appellation a,
               crs_parcel p
            where
               a.par_id = p.id
            and
               a.status = 'CURR'
            and
               a.parcel_type = parcel_type
            and 
               a.parcel_value = parcel_value
            and 
               a.sub_type = sub_type
            and 
               a.appellation_value = appellation_value
    	    limit 1
            ;
    END IF;
    
    RETURN;

END
$body$
LANGUAGE plpgsql;

-- Function to retrieve the centroid for a parcel ID.

CREATE OR REPLACE FUNCTION electoral_address.elc_findparcelpoint
(
    par_id int
) 
RETURNS TABLE
(
    point text
) AS 
$body$
select 
   ST_AsText(ST_Transform(ST_PointOnSurface(shape), 4167)) as point 
from 
   crs_parcel
where 
   id = $1
limit 1;
$body$
LANGUAGE sql;

-- Function to retrieve a list of NZ spatial reference systems

CREATE OR REPLACE FUNCTION electoral_address.elc_GetSpatialReferenceSystems
(
)
RETURNS TABLE
(
    srid integer,
    name text
)    
AS
$body$
select 
   srid,
   substring(srtext,E'\\"([^\\"]+)') as name 
from 
   spatial_ref_sys 
where 
   srtext like '%GEOGCS["NZGD49"%' 
   or srtext like '%GEOGCS["NZGD2000"%'
order by
   name
$body$
LANGUAGE sql;

-- Function to retrieve a list of code values for a given code type

CREATE OR REPLACE FUNCTION electoral_address.elc_GetCodeList
(
    p_code_type code.code_type%TYPE
)
RETURNS TABLE
(
    code code.code%TYPE,
    value text
)
AS
$body$
select 
   code,
   value
from 
   code 
where 
   UPPER(code_type) = UPPER($1)
$body$
LANGUAGE sql;


-- Function retrieve details for a source type, or all source types
-- if a null type is specified

CREATE OR REPLACE FUNCTION electoral_address.elc_GetSourceTypeDetail
(
    p_stp_id int
)
RETURNS TABLE
(
    stp_id int,
    name source_type.name%TYPE,
    fileext source_type.fileext%TYPE,
    srsid int,
    reader_type source_type.reader_type%TYPE,
    reader_params source_type.reader_params%TYPE
)
AS
$body$
select 
   stp_id,
   name,
   fileext,
   srsid,
   reader_type,
   reader_params
from 
   source_type 
where 
   stp_id = $1 or 
   ($1 is null and active = 't')
$body$
LANGUAGE sql;


CREATE OR REPLACE FUNCTION electoral_address.elc_CreateSourceType
(
    p_name source_type.name%TYPE,
    p_fileext source_type.fileext%TYPE,
    p_srsid int,
    p_reader_type source_type.reader_type%TYPE,
    p_reader_params source_type.reader_params%TYPE
)
RETURNS INT
AS
$body$
BEGIN
    IF EXISTS (SELECT * FROM source_type WHERE name=p_name AND active) THEN
        RAISE EXCEPTION 'Cannot create source type "%" as there is already one with that name', p_name;
    END IF;

    INSERT INTO source_type( name, fileext, srsid, reader_type, reader_params)
    VALUES ( p_name, p_fileext, p_srsid, p_reader_type, p_reader_params);

    RETURN lastval();
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_UpdateSourceType
(
    p_stp_id INT,
    p_name source_type.name%TYPE,
    p_fileext source_type.fileext%TYPE,
    p_srsid int,
    p_reader_type source_type.reader_type%TYPE,
    p_reader_params source_type.reader_params%TYPE
)
RETURNS INT
AS
$body$
DECLARE
    l_new_id INT;
BEGIN
    IF EXISTS (SELECT * FROM source_type
        WHERE 
            stp_id = p_stp_id AND
            name = p_name AND
            fileext = p_fileext AND
            srsid = p_srsid AND
            reader_type = p_reader_type AND 
            reader_params = p_reader_params
        ) THEN
        RETURN p_stp_id;
    END IF;

    IF NOT EXISTS (SELECT * FROM source_type WHERE stp_id=p_stp_id ) THEN
        RAISE EXCEPTION 'Cannot update source type "%" as it doesn''t exist!', p_stp_id;
    END IF;

    IF EXISTS (SELECT * FROM source_type WHERE name=p_name AND active and stp_id<> p_stp_id ) THEN
        RAISE EXCEPTION 'Cannot update source type "%" name as there is another with the same name', p_stp_id;
    END IF;

    -- If this source type hasn't been used in a job yet, then can just
    -- update it. Also if it has only been used in jobs that have not yet
    -- been loaded (as when loaded will update job status)

    IF NOT EXISTS (SELECT * FROM job WHERE stp_id=p_stp_id AND status != 'N') THEN
        UPDATE source_type
        SET
            name=p_name,
            fileext=p_fileext,
            srsid = p_srsid,
            reader_type=p_reader_type,
            reader_params=p_reader_params
        WHERE
            stp_id=p_stp_id;
        RETURN p_stp_id;
    END IF;

    UPDATE source_type SET active=FALSE WHERE stp_id=p_stp_id;
    
    l_new_id = elc_CreateSourceType( p_name, p_fileext, p_srsid, p_reader_type, p_reader_params );

    UPDATE supplier SET stp_id=l_new_id WHERE stp_id=p_stp_id;
    UPDATE job SET stp_id=l_new_id WHERE stp_id=p_stp_id AND status='N';


    RETURN l_new_id;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_DeleteSourceType
(
    p_stp_id INT
)
RETURNS BOOLEAN
AS
$body$
BEGIN
    IF EXISTS (SELECT * FROM supplier WHERE stp_id = p_stp_id ) THEN
        UPDATE source_type SET active=FALSE WHERE stp_id=p_stp_id;
    ELSE
        DELETE FROM source_type WHERE stp_id=p_stp_id;
    END IF;
    RETURN TRUE;
END
$body$
LANGUAGE plpgsql;


-- Retrieve supplier details, or a list of active suppliers if no 
-- id is supplied

CREATE OR REPLACE FUNCTION electoral_address.elc_GetSupplier
(
    p_sup_id INT
)
RETURNS TABLE
(
    sup_id int,
    stp_id int,
    stt_id int,
    name supplier.name%TYPE
)
AS
$body$
SELECT 
   sup_id,
   stp_id,
   stt_id,
   name
FROM 
   supplier 
WHERE
   sup_id = $1 OR (active AND $1 IS NULL)

$body$
LANGUAGE sql;

-- Create a new supplier

CREATE OR REPLACE FUNCTION electoral_address.elc_CreateSupplier
(
    p_name supplier.name%TYPE,
    p_stp_id INT,
    p_stt_id INT
)
RETURNS INT
AS
$body$
BEGIN
    IF EXISTS (SELECT sup_id FROM supplier WHERE active AND name=p_name) THEN
        RAISE EXCEPTION 'Cannot create supplier with name "%" as there is already one', p_name;
    END IF;

    INSERT INTO supplier( name, stp_id, stt_id )
    VALUES (p_name, p_stp_id, p_stt_id );

    RETURN lastval();
END
$body$
LANGUAGE plpgsql;

-- Update a supplier, actually just delete and create if not already active

CREATE OR REPLACE FUNCTION electoral_address.elc_UpdateSupplier
(
    p_sup_id INT,
    p_name supplier.name%TYPE,
    p_stp_id INT,
    p_stt_id INT
)
RETURNS INT
AS
$body$
DECLARE
    l_old_stp_id INT;
BEGIN
    IF EXISTS (
        SELECT sup_id 
        FROM supplier 
        WHERE 
            active AND 
            sup_id=p_sup_id AND
            name=p_name AND
            stp_id = p_stp_id AND
            stt_id = p_stt_id
        ) THEN
        RETURN p_sup_id;
    END IF;

    IF EXISTS (SELECT sup_id FROM supplier WHERE active AND name=p_name AND sup_id != p_sup_id) THEN
        RAISE EXCEPTION 'Cannot rename supplier to "%" as there is already one with that name', p_name;
    END IF;

    IF NOT EXISTS (SELECT sup_id FROM supplier WHERE sup_id=p_sup_id) THEN
        RAISE EXCEPTION 'Cannot update supplier "%" as it doesn''t exist!', p_name;
    END IF;

    -- Record the old source type id

    SELECT stp_id INTO l_old_stp_id FROM supplier WHERE sup_id=p_sup_id;

    -- Update the supplier

    UPDATE supplier
    SET name=p_name, stp_id=p_stp_id, stt_id=p_stt_id
    WHERE sup_id=p_sup_id;
    
    -- Update the source type for any unloaded jobs

    IF l_old_stp_id = p_stp_id THEN
        UPDATE job SET stp_id=p_stp_id WHERE stp_id=l_old_stp_id AND status='N';
    END IF;

    RETURN p_sup_id;
END
$body$
LANGUAGE plpgsql;

-- Delete a supplier (just deactivate if referenced)

CREATE OR REPLACE FUNCTION electoral_address.elc_DeleteSupplier
(
    p_sup_id INT
)
RETURNS BOOLEAN
AS
$body$
BEGIN
    IF EXISTS (SELECT * FROM job WHERE sup_id = p_sup_id ) THEN
        UPDATE supplier SET active=FALSE WHERE sup_id=p_sup_id;
    ELSE
        DELETE FROM supplier WHERE sup_id=p_sup_id;
    END IF;
    RETURN TRUE;
END
$body$
LANGUAGE plpgsql;

-- Create new upload

CREATE OR REPLACE FUNCTION electoral_address.elc_CreateUpload
(
    p_user upload.created_by%TYPE,
    p_filename upload.filename%TYPE
)
RETURNS INT
AS
$body$
BEGIN

    -- Insert the data into the job table
    INSERT INTO upload( created_by, filename)
    VALUES (p_user, p_filename);

    -- Return the id of the job
    RETURN lastval();
END
$body$
LANGUAGE plpgsql;

-- Create new upload

CREATE OR REPLACE FUNCTION electoral_address.elc_SetUploadFilename
(
    p_upl_id INT,
    p_filename upload.filename%TYPE
)
RETURNS BOOL
AS
$body$
    UPDATE upload
    SET filename = $2
    WHERE upl_id=$1;
    SELECT TRUE;
$body$
LANGUAGE SQL;

-- Get details of an upload (or all uploads if id is set to null

CREATE OR REPLACE FUNCTION electoral_address.elc_GetUploadDetails
(
    p_upl_id INT
)
RETURNS TABLE
(
    upl_id INT,
    created_by upload.created_by%TYPE,
    creation_time timestamp,
    filename upload.filename%TYPE,
    n_insert BIGINT,
    n_delete BIGINT
)
AS
$body$
    WITH 
    del ( upl_id, n_del ) AS 
    (
        SELECT
            upl.upl_id,
            COUNT( DISTINCT adr.sad_id )
        FROM
            address adr
            JOIN job ON job.job_id = adr.job_id
            JOIN upload upl on upl.upl_id = job.upl_id
        WHERE
            ($1 IS NULL OR upl.upl_id=$1) AND
            adr.sad_id IS NOT NULL AND
            adr.status IN ('REPL','DELE')
        GROUP BY
            upl.upl_id
    ),
    ins ( upl_id, n_new ) AS
    (
        SELECT
            upl.upl_id,
            COUNT(adr.adr_id)
        FROM
            address adr
            JOIN job ON job.job_id = adr.job_id
            JOIN upload upl on upl.upl_id = job.upl_id
        WHERE
            ($1 IS NULL OR upl.upl_id=$1) AND
            adr.housenumber IS NOT NULL AND
            adr.rna_id IS NOT NULL AND
            adr.rcl_id IS NOT NULL AND
            adr.status IN ('REPL','NEWA')
        GROUP BY
            upl.upl_id
    )
    SELECT
        upl.upl_id,
        upl.created_by,
        upl.creation_time,
        upl.filename,
        ins.n_new,
        del.n_del
    FROM
        upload upl
        LEFT OUTER JOIN ins ON ins.upl_id = upl.upl_id
        LEFT OUTER JOIN del ON del.upl_id = upl.upl_id
    WHERE
        $1 IS NULL OR upl.upl_id=$1;
$body$
LANGUAGE SQL;
    
    -- Get upload new addresses

CREATE OR REPLACE FUNCTION electoral_address.elc_UploadNewAddresses
(
    p_upl_id INT
)
RETURNS TABLE 
(
    housenumber address.housenumber%TYPE,
    range_low address.range_low%TYPE,
    range_high address.range_high%TYPE,
    status address.status%TYPE,
    rcl_id INT,      
    rna_id INT,    
    wkt TEXT,
    sufi INT
)
AS
$body$
    SELECT    
        adr.housenumber,
        adr.range_low,
        adr.range_high,
        adr.status, 
        adr.rcl_id,
        adr.rna_id,
        ST_AsText(adr.shape),
        adr.sad_sufi
    FROM
        address adr
        JOIN job ON job.job_id = adr.job_id
    WHERE
        job.upl_id=$1 AND
        adr.housenumber IS NOT NULL AND
        adr.rna_id IS NOT NULL AND
        adr.rcl_id IS NOT NULL AND
        adr.status IN ('REPL','NEWA','DELE');
$body$
LANGUAGE SQL;
    
    
-- Create a new job

CREATE OR REPLACE FUNCTION electoral_address.elc_CreateJob
(
    p_sup_id INT,
    p_description TEXT,
    p_source_name TEXT,
    p_user job.created_by%TYPE
)
RETURNS INT
AS
$body$
DECLARE
    l_stp_id INT;
    l_user job.created_by%TYPE;
BEGIN
    -- Lookup up the suppliers source type
    l_stp_id := (SELECT stp_id FROM supplier WHERE sup_id = p_sup_id);
    IF l_stp_id IS NULL THEN
        RAISE EXCEPTION 'Invalid supplier ID supplied with job';
    END IF;

    l_user := p_user;
    IF l_user IS NULL THEN
        l_user = current_user;
    END IF;

    -- Insert the data into the job table
    INSERT INTO job( sup_id, stp_id, created_by, description, source_name )
    VALUES (p_sup_id, l_stp_id, l_user, p_description, p_source_name );

    -- Return the id of the job
    RETURN lastval();
END
$body$
LANGUAGE plpgsql;

-- Delete a job

CREATE OR REPLACE FUNCTION electoral_address.elc_DeleteJob
(
    p_job_id INT
)
RETURNS INT
AS
$body$
DECLARE
    l_count INTEGER;
BEGIN
    DELETE FROM address WHERE job_id=p_job_id;
    DELETE FROM job  WHERE job_id=p_job_id;
    GET DIAGNOSTICS l_count=ROW_COUNT;
    RETURN l_count;
END
$body$
LANGUAGE plpgsql;

-- Retrieve job details either for a specific job,
-- or all active jobs if the parameter is NULL

CREATE OR REPLACE FUNCTION electoral_address.elc_GetJobDetails
(
    p_job_id INT
)
RETURNS TABLE 
(
    job_id INT,
    created_by NAME,
    description TEXT,
    notes TEXT,
    source_name TEXT,
    sup_id INT,
    stp_id INT,
    creation_time TIMESTAMP,
    completed_time TIMESTAMP,
    uploaded_time TIMESTAMP,
    status CHAR(1),
    n_address BIGINT,
    n_insert BIGINT,
    n_delete BIGINT,
    status_string VARCHAR(32),
    upl_id INT
)
AS
$body$
WITH nad( job_id, count, n_insert ) AS
(
    SELECT 
       job_id,
       COUNT(*),
       SUM(CASE WHEN status IN ('REPL','NEWA') THEN 1 ELSE 0 END)
    FROM
       address
    WHERE
       job_id=$1 OR $1 IS NULL
    GROUP BY
       job_id
),
ndl( job_id, n_delete ) AS
(
    SELECT
        job_id,
        COUNT(DISTINCT sad_id)
    FROM
       address
    WHERE
       job_id=$1 OR $1 IS NULL AND
       status IN ('REPL','DELE')
    GROUP BY
       job_id

)
SELECT
    job.job_id,
    job.created_by,
    job.description,
    job.notes,
    job.source_name,
    job.sup_id,
    job.stp_id,
    job.creation_time,
    job.completed_time,
    job.uploaded_time,
    job.status,
    nad.count,
    nad.n_insert,
    ndl.n_delete,
    code.value,
    job.upl_id
FROM
    job
    LEFT OUTER JOIN nad ON nad.job_id = job.job_id
    LEFT OUTER JOIN ndl ON ndl.job_id = job.job_id
    LEFT OUTER JOIN code ON code.code_type='job_status' AND code.code=job.status
WHERE
    job.job_id = $1 OR ($1 IS NULL AND job.status != 'U');
$body$
LANGUAGE SQL;


-- Update job details

CREATE OR REPLACE FUNCTION electoral_address.elc_UpdateJob
(
    p_job_id INT,
    p_description TEXT,
    p_notes TEXT,
    p_source_name TEXT,
    p_upl_id INT,
    p_status job.status%TYPE,
    p_force_status BOOLEAN
)
RETURNS BOOLEAN
AS
$body$
DECLARE
    l_status job.status%TYPE;
    l_new_status job.status%TYPE;
    l_completed_time TIMESTAMP;
    l_upl_id job.upl_id%TYPE;
    l_stp_id job.stp_id%TYPE;
    l_sup_id job.sup_id%TYPE;
    l_uploaded_time TIMESTAMP;
    l_description job.description%TYPE;
    l_notes job.notes%TYPE;
    l_source_name job.source_name%TYPE;
BEGIN
    IF NOT EXISTS(SELECT job_id FROM job WHERE job_id=p_job_id) THEN
        RAISE EXCEPTION 'Invalid job % in call to update job', p_job_id;
    END IF;

    IF p_status NOT IN (SELECT code FROM code WHERE code_type='job_status') THEN
        RAISE EXCEPTION 'Invalid job status % in call to update job %', p_status, p_job_id;
    END IF;

    SELECT status, description, notes, source_name, upl_id, stp_id, sup_id, completed_time, uploaded_time
    INTO l_status, l_description, l_notes, l_source_name, l_upl_id, l_stp_id, l_sup_id, l_completed_time, l_uploaded_time
    FROM job
    WHERE job_id = p_job_id;

    IF (l_status=p_status) AND
       (l_description=p_description OR (l_description IS NULL AND p_description IS NULL)) AND
       (l_notes=p_notes OR (l_notes IS NULL AND p_notes IS NULL)) AND
       (l_source_name=p_source_name OR (l_source_name IS NULL AND p_source_name IS NULL)) AND
       (l_upl_id=p_upl_id OR (l_upl_id IS NULL AND p_upl_id IS NULL)) 
    THEN
        RETURN TRUE;
    END IF;

    l_new_status = p_status;

    IF l_status = 'U' THEN
        RAISE EXCEPTION 'Job % cannot be updated as already uploaded to Landonline', p_job_id;
    END IF;

    IF p_upl_id IS NOT NULL THEN
        IF l_status != 'C' AND l_status != 'U' THEN
            RAISE EXCEPTION 'Job % cannot be uploaded as it is not completed',p_job_id;
        END IF;
        l_new_status = 'U';
    END IF;

    IF l_status <> l_new_status THEN
        -- Check for valid state changes
        IF NOT (
            (l_status = 'N' AND l_new_status = 'P') OR
            (l_status = 'N' AND l_new_status = 'D') OR
            (l_status = 'P' AND l_new_status = 'C') OR
            (l_status = 'P' AND l_new_status = 'D') OR
            (l_status = 'C' AND l_new_status = 'U') OR
            (l_status = 'C' AND l_new_status = 'D') OR
            FALSE
            )
            AND NOT 
            p_force_status
        THEN
            RAISE EXCEPTION 'Job % invalid state change from % to %', p_job_id, l_status, l_new_status;
        END IF;

        IF l_new_status = 'C' THEN
            IF EXISTS( SELECT adr_id FROM address WHERE job_id=p_job_id AND status IN ('UNKN','BADR','BADN','BADG')) THEN
                RAISE EXCEPTION 'Job % cannot be completed as there are still addresses with bad road names/numbers or undefined actions', p_job_id;
            END IF;
        END IF;

        IF (l_new_status = 'U' OR l_new_status = 'C') THEN
            IF l_completed_time IS NULL THEN
                l_completed_time = CURRENT_TIMESTAMP;
            END IF;
        ELSE
            l_completed_time = NULL;
        END IF;

        IF l_new_status = 'U' THEN
            IF l_uploaded_time IS NULL THEN
                l_uploaded_time =  CURRENT_TIMESTAMP;
            END IF;
        ELSE
            l_uploaded_time = NULL;
        END IF;
    END IF;

    -- If setting status to new, then clear out any addresses already loaded
    -- and reset the source type id
    IF l_new_status = 'N' THEN
        DELETE FROM address WHERE job_id = p_job_id;
        SELECT stp_id INTO l_stp_id FROM supplier WHERE sup_id = l_sup_id;
    END IF;

    UPDATE job
    SET
        description=p_description,
        notes = p_notes,
        source_name=p_source_name,
        completed_time=l_completed_time,
        upl_id = p_upl_id,
        stp_id = l_stp_id,
        uploaded_time=l_uploaded_time,
        status=l_new_status
    WHERE
        job_id = p_job_id;

    RETURN TRUE;
END
$body$
LANGUAGE plpgsql;

--

CREATE OR REPLACE FUNCTION electoral_address.elc_GetTAVersion()
RETURNS INT
AS
$body$
    SELECT
        MAX(version)
    FROM
        crs_stat_version
    WHERE
        area_class='TA' AND
        ((end_date IS NOT NULL AND end_date > CURRENT_DATE) 
             OR end_date IS NULL);

$body$
LANGUAGE SQL;

CREATE OR REPLACE FUNCTION electoral_address.elc_TAList()
RETURNS TABLE
(
    stt_id INT,
    name crs_statist_area.name%TYPE
)
AS
$body$
    SELECT
        -1,
        ''        
    UNION
    SELECT 
        id,
        name
    FROM
        crs_statist_area
    WHERE
        status='CURR' AND
        sav_area_class='TA' AND
        sav_version = elc_GetTAVersion();
$body$
LANGUAGE SQL;

CREATE OR REPLACE FUNCTION electoral_address.elc_MeshblockTA
( 
    p_mbk_id INT 
)
RETURNS INT
AS
$body$
    SELECT 
        stt.id
    FROM
        crs_mesh_blk_area mba
        JOIN crs_statist_area stt ON stt.id = mba.stt_id
    WHERE
        mba.mbk_id = $1 AND
        stt.status = 'CURR' AND
        stt.sav_area_class = 'TA' AND 
        stt.sav_version = elc_GetTAVersion()
$body$
LANGUAGE SQL;


CREATE OR REPLACE FUNCTION electoral_address.elc_CleanRoadname
(
    p_roadname address.src_roadname%TYPE
)
RETURNS address.src_roadname%TYPE
AS
$body$
DECLARE
    l_roadname address.src_roadname%TYPE;
BEGIN
    l_roadname := regexp_replace(trim(upper(p_roadname)),E'\\s+',' ');
    l_roadname := regexp_replace(trim(upper(l_roadname)),E'^STATE HIGHWAY ONE','SH 1');
    l_roadname := regexp_replace(trim(upper(l_roadname)),E'^STATE HIGHWAY ','SH ');
    return l_roadname;

END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_CleanHousenumber
(
    p_housenumber address.housenumber%TYPE
)
RETURNS address.housenumber%TYPE
AS
$body$
DECLARE
    l_housenumber address.housenumber%TYPE;
BEGIN
    l_housenumber := regexp_replace(trim(upper(p_housenumber)),E'\\s+',' ');
    -- Replace 1-5/23 with 1/23-5/23
    l_housenumber := regexp_replace(l_housenumber,
        E'^(\\d+[A-Z]*)\\-(\\d+[A-Z]*)\\/(\\d+[A-Z]*)$',
        E'\\1/\\3-\\2/\\3');
    -- Replace 123A-Z with 123A-123Z
    l_housenumber := regexp_replace(l_housenumber,
        E'^(\\d+)([A-Z]+)\\-([A-Z]+)$',
        E'\\1\\2-\\1\\3');
    return l_housenumber;
END
$body$
LANGUAGE plpgsql;

-- Add an address to a job

CREATE OR REPLACE FUNCTION electoral_address.elc_CreateAddress
(
    p_job_id int,
    p_src_id address.src_id%TYPE,
    p_src_status address.src_status%TYPE,
    p_roadname address.src_roadname%TYPE,
    p_housenumber address.housenumber%TYPE,
    p_src_comment TEXT,
    p_pointwkt VARCHAR(100),
    p_transform INT
)
RETURNS 
    INT
as
$body$
DECLARE
    l_src_status address.src_status%TYPE;
    l_srsid INT;
    l_point GEOMETRY;
    l_roadname address.src_roadname%TYPE;
    l_housenumber address.housenumber%TYPE;
BEGIN

    l_srsid := 4167;

    IF p_transform <> 0 THEN
        l_srsid := 
           (SELECT 
               srsid
           FROM 
               source_type
               JOIN job ON job.stp_id = source_type.stp_id
           WHERE
               job.job_id = p_job_id);
    
        If l_srsid IS NULL THEN
            RAISE EXCEPTION 'elc_LoadAddress: Invalid job id or missing srsid';
        END IF;
    END IF;

    l_point := ST_PointFromText( p_pointwkt, l_srsid );
    IF l_srsid != 4167 THEN
        l_point := ST_Transform(l_point, 4167 );
    END IF;


    IF p_src_status IS NULL OR p_src_status = '' THEN
        l_src_status = 'UNKN';
    ELSIF p_src_status NOT IN (SELECT code FROM code WHERE code_type = 'address_status') THEN
        RAISE EXCEPTION 'elc_LoadAddress: Invalid address status %',p_src_status;
    ELSE
        l_src_status := p_src_status;
    END IF;

    -- Note: fixes to the road name replace the source roadname, since
    -- currently there is nowhere else for them!

    l_housenumber := elc_CleanHousenumber(p_housenumber);
    l_roadname := elc_CleanRoadname( p_roadname );

    INSERT INTO address
    (
        job_id,
        housenumber,
        src_id,
        shape,
        src_status,
        src_roadname,
        src_housenumber,
        src_comment,
        src_shape
    )
    values
    (
        p_job_id,
        l_housenumber,
        p_src_id,
        l_point,
        l_src_status,
        l_roadname,
        p_housenumber,
        p_src_comment,
        l_point
    );

    RETURN lastval();
END
$body$
LANGUAGE plpgsql;

-- Create an address based on a Landonline address point ...

CREATE OR REPLACE FUNCTION electoral_address.elc_CreateAddressFromLandonline
(
    p_job_id int,
    p_sad_id address.sad_id%TYPE,
    p_src_status address.src_status%TYPE
)
RETURNS INT
AS
$body$
DECLARE 
    l_adr_id INT;
    l_rna_id INT;
    l_houseno crs_street_address.house_number%TYPE;
    l_roadname crs_road_name.name%TYPE;
    l_shape crs_street_address.shape%TYPE;
BEGIN
    IF NOT EXISTS (SELECT * FROM crs_street_address WHERE id=p_sad_id) THEN
        RAISE EXCEPTION 'Invalid crs_street_address id % in call to elc_CreateAddressFromLandonline', p_sad_id;
    END IF;
    IF (SELECT count(adr_id) FROM address WHERE job_id=p_job_id AND sad_id=p_sad_id) > 0 THEN
        RAISE EXCEPTION 'Landonline address point % is already linked to an address point', p_sad_id;
    END IF;
    SELECT 
       sad.house_number,
       sad.shape,
       rna.id,
       rna.name
    INTO
       l_houseno,
       l_shape,
       l_rna_id,
       l_roadname
    FROM
        crs_street_address sad
        LEFT OUTER JOIN crs_road_name rna ON rna.id = sad.rna_id
    WHERE
        sad.id = p_sad_id;
    l_adr_id := elc_CreateAddress( p_job_id, 'LINZ', p_src_status, l_roadname, l_houseno, '', ST_AsText(l_shape), 0);
    l_adr_id := elc_UpdateAddress( l_adr_id, p_src_status, l_houseno, p_sad_id, l_rna_id, '', FALSE );
    PERFORM elc_RefreshAddressLinks( l_adr_id );
    RETURN l_adr_id;
END    
$body$
LANGUAGE plpgsql;


-- Delete an address

CREATE OR REPLACE FUNCTION electoral_address.elc_DeleteAddress
(
    p_adr_id INT
)
RETURNS BOOLEAN
AS
$body$
BEGIN
    UPDATE address SET merge_adr_id=NULL WHERE merge_adr_id=p_adr_id;
    DELETE FROM address WHERE adr_id=p_adr_id;
    RETURN TRUE;
END
$body$
LANGUAGE plpgsql;

-- Get the details of an address

CREATE OR REPLACE FUNCTION electoral_address.elc_GetAddressDetails
(
    p_adr_id INT
)
RETURNS TABLE 
(
    adr_id INT,
    job_id INT,
    roadname crs_road_name.name%TYPE,
    housenumber address.housenumber%TYPE,
    range_low address.range_low%TYPE,
    range_high address.range_high%TYPE,
    src_id address.src_id%TYPE,
    src_roadname address.src_roadname%TYPE,
    src_housenumber address.src_housenumber%TYPE,
    src_status address.src_status%TYPE,
    src_comment address.src_comment%TYPE,
    sad_roadname crs_road_name.name%TYPE,
    sad_housenumber crs_street_address.house_number%TYPE,
    sad_offset DOUBLE PRECISION,
    ta_name crs_statist_area.name%TYPE,
    status address.status%TYPE,
    warning_codes address.warning_codes%TYPE,
    notes TEXT,
    rna_id INT,
    rcl_id INT,
    sad_id INT,
    sad_sufi INT,
    sad_par_id INT,
    par_id INT,
    par_sad_count INT,
    stt_id INT,
    merge_adr_id INT,
    ismerged BOOLEAN,
    cluster_id address.cluster_id%TYPE,
    location text

)
AS
$body$

    -- Using CTE to avoid sequential scan on crs_statist_area!
    WITH ta(stt_id) AS (SELECT elc_meshblockTA(mbk_id) FROM address WHERE adr_id=$1)
    SELECT
        adr.adr_id,
        adr.job_id,
        rna.name,
        adr.housenumber,
        adr.range_low,
        adr.range_high,
        adr.src_id,
        adr.src_roadname,
        adr.src_housenumber,
        adr.src_status,
        adr.src_comment,
        rna2.name,
        sad.house_number,
        ST_Distance(ST_Transform(adr.shape,2193),ST_Transform(sad.shape,2193)),
        stt.name,
        adr.status,
        adr.warning_codes,
        adr.notes,
        adr.rna_id,
        adr.rcl_id,
        adr.sad_id,
        adr.sad_sufi,
        adr.sad_par_id,
        adr.par_id,
        adr.par_sad_count,
        ta.stt_id,
        adr.merge_adr_id,
        adr.ismerged,
        adr.cluster_id,
        ST_AsText(adr.shape)
    FROM
        address adr
        LEFT OUTER JOIN crs_road_name rna ON rna.id = adr.rna_id
        LEFT OUTER JOIN crs_street_address sad ON sad.id = adr.sad_id
        LEFT OUTER JOIN crs_road_name rna2 ON rna2.id = sad.rna_id,
        ta
        LEFT OUTER JOIN crs_statist_area stt ON stt.id = ta.stt_id
    WHERE
        adr_id = $1
$body$
LANGUAGE sql;


-- Get a list of address ids for a job

CREATE OR REPLACE FUNCTION electoral_address.elc_GetJobAddressIds
(
    p_job_id INT
)
RETURNS TABLE
(
    adr_id INT
)
AS
$body$
    SELECT
        adr_id
    FROM
        address
    WHERE
        job_id = $1
    ORDER BY
        adr_id;
$body$
LANGUAGE sql;

-- Update the links with Landonline data if they are from a previous date
-- (ie may have been invalidated by a BDE extract)

CREATE OR REPLACE FUNCTION electoral_address.elc_RefreshJobLinks
(
    p_job_id INT
)
RETURNS
    INT[]
AS
$body$
DECLARE
    l_link_date DATE;
    l_status job.status%TYPE;
    l_result INT[];
BEGIN
    SELECT status, link_date INTO l_status, l_link_date FROM job WHERE job_id=p_job_id;

    IF l_status IN ('U','D') THEN
        RETURN TRUE;
    END IF;

    IF l_link_date IS NULL OR l_link_date <> CURRENT_DATE THEN
        UPDATE address
        SET linked = FALSE, sad_par_id=NULL, par_sad_count=NULL
        WHERE job_id = p_job_id;
    END IF;

    SELECT array_agg(adr_id) INTO l_result FROM address WHERE job_id=p_job_id AND NOT linked;

    PERFORM _elc_RefreshLinks( p_job_id );

    UPDATE job SET link_date=CURRENT_DATE WHERE job_id = p_job_id;
    RETURN l_result;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_RefreshAddressLinks
(
    p_adr_id INT
)
RETURNS
    BOOLEAN
AS
$body$
DECLARE
    l_job_id INT;
BEGIN
    UPDATE address SET linked=FALSE WHERE adr_id = p_adr_id; 

    SELECT job_id INTO l_job_id FROM address WHERE adr_id = p_adr_id;

    IF l_job_id IS NOT NULL THEN
        PERFORM _elc_RefreshLinks( l_job_id );
    END IF;

    RETURN TRUE;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address._elc_RefreshLinks
(
    p_job_id INT
)
RETURNS BOOLEAN
AS
$body$
BEGIN
    RAISE WARNING '_elc_RefreshLinks: %','Starting';
    RAISE WARNING '_elc_RefreshLinks: %','Unlinking street address';
    UPDATE address
    SET sad_id=NULL, sad_par_id=NULL
    WHERE job_id = p_job_id
    AND NOT linked
    AND sad_id IS NOT NULL
    AND NOT EXISTS (
        SELECT id FROM crs_street_address WHERE id=address.sad_id AND status='CURR'
        );

    RAISE WARNING '_elc_RefreshLinks: %','Unlinking road names';
    UPDATE address
    SET rna_id=NULL, rcl_id=NULL
    WHERE 
        job_id = p_job_id AND
        NOT linked AND
        rna_id IS NOT NULL AND
        adr_id NOT IN (
            SELECT 
               adr.adr_id
            FROM
               address adr
               JOIN crs_road_ctr_line rcl 
                    ON rcl.id = adr.rcl_id and rcl.status='CURR'
               JOIN crs_road_name rna 
                    ON rna.id = adr.rna_id and rna.status='CURR'
               JOIN crs_road_name_asc ras 
                    ON ras.rna_id=adr.rna_id AND ras.rcl_id=adr.rcl_id
            WHERE
               adr.job_id=p_job_id AND
               NOT adr.linked
            );


    RAISE WARNING '_elc_RefreshLinks: %','Unlinking parcels';
    UPDATE address
    SET par_id=NULL, par_sad_count=NULL
    WHERE
       job_id = p_job_id AND
       NOT linked AND
       par_id IS NOT NULL AND
       NOT EXISTS (
           SELECT id FROM crs_parcel par
           WHERE par.id=address.par_id AND 
               par.toc_code='PRIM' AND 
               par.status='CURR' AND
               ST_Intersects( address.shape, par.shape )
           );

    RAISE WARNING '_elc_RefreshLinks: %','Unlinking meshblocks';
    UPDATE address
    SET mbk_id=NULL
    WHERE
        job_id = p_job_id AND
        NOT linked AND
        mbk_id IS NOT NULL AND
        NOT EXISTS (
            SELECT 
                mbk.id
            FROM
                crs_mesh_blk mbk
            WHERE
                mbk.id = address.mbk_id AND
                mbk.end_datetime IS NULL AND
                ST_Intersects( mbk.shape, address.shape )
            );

    RAISE WARNING '_elc_RefreshLinks: %','Linking meshblocks';
    PERFORM elc_LinkAddressesToMeshblock( p_job_id );
    -- Need to link to roads and parcels before addresses 
    RAISE WARNING '_elc_RefreshLinks: %','Linking roads';
    PERFORM elc_LinkAddressesToRoads( p_job_id );
    RAISE WARNING '_elc_RefreshLinks: %','Linking parcels';
    PERFORM elc_LinkAddressesToParcels( p_job_id );
    RAISE WARNING '_elc_RefreshLinks: %','Linking addresses';
    PERFORM elc_LinkAddressesToLol( p_job_id );

    UPDATE address SET linked=TRUE WHERE job_id=p_job_id;
    RAISE WARNING '_elc_RefreshLinks: %','Complete';

    RETURN TRUE;
END
$body$
LANGUAGE plpgsql;

-- Ensure addresses are within the valid extents for the country

CREATE OR REPLACE FUNCTION electoral_address.elc_EnsureLocationsValid
(
    p_job_id INT
)
RETURNS INT
AS
$body$
DECLARE
    l_nbad INT;
    l_naddress INT;
    l_valid_extents GEOMETRY;
    l_default_shape GEOMETRY;
BEGIN
    l_valid_extents := (SELECT ST_GeomFromText(value,4167) FROM code WHERE code_type='system_data' AND code='valid_extents_polygon');
    IF l_valid_extents IS NULL THEN
        RETURN 0;
    END IF;
    l_naddress := (SELECT count(*) FROM address WHERE job_id=p_job_id);
    l_nbad := (SELECT count(*) FROM address WHERE job_id=p_job_id AND NOT ST_Intersects(shape,l_valid_extents));
    IF l_nbad = 0 THEN
        RETURN 0;
    END IF;

    l_default_shape := (
        SELECT ST_SetSRID(ST_Centroid(ST_Extent(shape)),4167) 
        FROM address
        WHERE job_id=p_job_id AND ST_Intersects(shape,l_valid_extents)
        );
    IF l_default_shape IS NULL OR NOT ST_intersects(l_default_shape,l_valid_extents) THEN
        l_default_shape := ST_Centroid(l_valid_extents);
    END IF;

    UPDATE address
    SET 
        shape=l_default_shape,
        notes = CASE WHEN notes IS NULL or notes='' THEN
                'Address location was invalid - shifted to an arbitrary location'
            ELSE
                notes ||
                '. Address location was invalid - shifted to an arbitrary location'
            END
    WHERE
        job_id = p_job_id AND 
        NOT ST_Intersects(shape,l_valid_extents);
    RETURN l_nbad;
END
$body$
LANGUAGE plpgsql;

-- Update the meshblock links for the addresses in a job (used to identify TAs)

CREATE OR REPLACE FUNCTION electoral_address.elc_LinkAddressesToMeshblock
(
    p_job_id INT
)
RETURNS INT
AS
$body$
DECLARE
    l_count INT;
    l_ambig INT;
BEGIN

    UPDATE
        address
    SET
        mbk_id = (
            SELECT
                id
            FROM
                crs_mesh_blk mbk
            WHERE
                mbk.end_datetime IS NULL AND
                ST_Intersects(mbk.shape, address.shape)
            LIMIT 1
            )
    WHERE
       job_id = p_job_id AND
       NOT linked AND
       mbk_id IS NULL;

    SELECT COUNT(*) INTO l_count
    FROM address
    WHERE job_id = p_job_id AND NOT linked AND mbk_id IS NULL;

    RETURN l_count;
END
$body$
LANGUAGE plpgsql;


-- Update the road centreline links for the addresses in a job

CREATE OR REPLACE FUNCTION electoral_address.elc_LinkAddressesToRoads
(
    p_job_id INT
)
RETURNS INT
AS
$body$
DECLARE
    l_count INT;
    l_max_dist DOUBLE PRECISION;
BEGIN

    SELECT road_search_radius INTO l_max_dist FROM job WHERE job_id = p_job_id;

    -- Set up common table expression to determine the nearest road
    -- matching the road name and within a specified distance of the 
    -- address point
    --
    -- To do this create an (approximately) circular buffer by
    -- transforming to NZTM (2193), buffering, and then transforming 
    -- back to NZGD2000.
    --
    -- Also use NZTM for distance calcs

    -- Make sure temp table isn't hanging around

    DROP TABLE IF EXISTS tmp_ad3;

    CREATE TEMP TABLE tmp_ad3 (
       adr_id INT NOT NULL PRIMARY KEY,
       rcl_id INT NOT NULL,
       rna_id INT NOT NULL
       );


    INSERT INTO tmp_ad3( adr_id, rcl_id, rna_id )
    
    -- Calculate buffer and transformed address point
    WITH 
    ad1 ( adr_id, roadname, point, buffer ) AS
    (
       SELECT
          adr_id,
          src_roadname,
          ST_Transform( shape, 2193),
          ST_Transform( ST_Buffer( ST_Transform( shape, 2193 ), l_max_dist, 4 ), 4167 )
       from 
          electoral_address.address
       WHERE 
          job_id=p_job_id AND
          NOT linked AND
          rna_id IS NULL
    ), 
    -- Match with road names/centrelines

    ad2( adr_id, rcl_id, rna_id, rank, dist ) AS
    (
    SELECT 
       ad1.adr_id,
       rcl.id,
       rna.id,
       row_number() OVER (
           PARTITION BY ad1.adr_id 
           ORDER BY ST_Distance(ad1.point, ST_Transform(rcl.shape,2193))
           ),
       ST_Distance(ad1.point, ST_Transform(rcl.shape,2193))
    FROM
       ad1,
       bde.crs_road_ctr_line rcl
       JOIN bde.crs_road_name_asc ras ON ras.rcl_id = rcl.id
       JOIN bde.crs_road_name rna ON rna.id = ras.rna_id
    WHERE
       -- Link road names, accounting for possible suburb or RD n suffix
       -- as well as removing spaces from hyphenated roadnames
       upper(rna.name) IN (
            ad1.roadname,
            regexp_replace(ad1.roadname,E'(\\w)\\s*\\-\\s*(\\w)',E'\\1-\\2'),
            regexp_replace(regexp_replace(ad1.roadname,E'(\\w)\\s*\\-\\s*(\\w)',E'\\1-\\2'),
                E'\\s+\\S+$',''), 
            regexp_replace(regexp_replace(ad1.roadname,E'(\\w)\\s*\\-\\s*(\\w)',E'\\1-\\2'),
                E'\\s+RD\\s+\\d+$',''),
            regexp_replace(
                regexp_replace(ad1.roadname,
                    E'^(?:STATE\\s+HIGHWAY\\s+|SH\\s*)(\\d+)$',E'SH \\1'),
                E'^SH\\s(\\d)$',E'SH  \\1')
        ) AND
       rna.status = 'CURR' AND
       rcl.status = 'CURR' AND
       ST_Intersects( rcl.shape, ad1.buffer )
    )
    -- Pick the nearest match
    SELECT
       adr_id,
       rcl_id,
       rna_id
    FROM
       ad2
    WHERE
       rank = 1;
       
    -- Update the address points
    UPDATE 
       address
    SET
       rcl_id = (SELECT rcl_id FROM tmp_ad3 WHERE adr_id = address.adr_id),
       rna_id = (SELECT rna_id FROM tmp_ad3 WHERE adr_id = address.adr_id)
    WHERE
        job_id = p_job_id AND
        adr_id IN (SELECT adr_id FROM tmp_ad3);

    -- Drop the temp table
    DROP TABLE tmp_ad3;

    SELECT COUNT(*) INTO l_count FROM address WHERE job_id=p_job_id AND rna_id IS NULL;
    RETURN l_count;
END
$body$
LANGUAGE plpgsql;


-- Update links to CRS address points where they are not already defined

CREATE OR REPLACE FUNCTION electoral_address.elc_LinkAddressesToLol
(
    p_job_id INT
)
RETURNS INT
AS
$body$
DECLARE
    l_count INT;
    l_max_unmoved_distance DOUBLE PRECISION;
    l_max_move_distance DOUBLE PRECISION;
BEGIN

    SELECT same_location_tolerance INTO l_max_unmoved_distance FROM job WHERE job_id = p_job_id;
    SELECT same_address_tolerance INTO l_max_move_distance FROM job WHERE job_id = p_job_id;

    -- Set up common table expression to determine the nearest 
    -- address point matching the TA address
    --
    -- To do this create an (approximately) circular buffer by
    -- transforming to NZTM (2193), buffering, and then transforming 
    -- back to NZGD2000.
    --
    -- Also use NZTM for distance calcs

    -- Make sure temp table isn't hanging around

    DROP TABLE IF EXISTS tmp_ad3;
    
    CREATE TEMP TABLE tmp_ad3 (
       adr_id INT NOT NULL PRIMARY KEY,
       sad_id INT NOT NULL,
       sad_sufi INT NOT NULL,
       status VARCHAR(4)
       );

    -- Will flag points within the required range as replacement if the same
    -- name and address, or just link the nearest, but not flag an action
    -- otherwise.  Preference is given first to same location, then same address, 
    -- then to same parcel, then by distance


    INSERT INTO tmp_ad3( adr_id, sad_id, sad_sufi, status )
    
    -- Calculate buffer and transformed address point

    WITH 
    ad1 ( adr_id, point, buffer, parcel ) AS
    (
       SELECT
          adr.adr_id,
          ST_Transform( adr.shape, 2193),
          ST_Transform( ST_Buffer( ST_Transform( adr.shape, 2193 ), l_max_move_distance, 4 ), 4167 ),
          par.shape
       from 
          address adr
          LEFT OUTER JOIN crs_parcel par ON par.id = adr.par_id
       WHERE 
          job_id=p_job_id AND
          NOT linked AND
          rna_id IS NOT NULL AND
          sad_id IS NULL
    ), 
    -- Match with street addresses
    ad2( adr_id, sad_id, sad_sufi, match, dist ) AS 
    (
    SELECT 
       ad1.adr_id,
       sad.id,
       sad.sufi,
       CASE 
       WHEN ST_Distance(ad1.point, ST_Transform(sad.shape,2193)) < l_max_unmoved_distance THEN
          CASE
            WHEN sad.house_number = adr.housenumber AND rna.name = rna2.name THEN 1
            ELSE 2
            END
       WHEN sad.house_number = adr.housenumber AND rna.name = rna2.name THEN 3
       WHEN ST_Intersects( sad.shape, ad1.parcel ) THEN 4
       ELSE 5
       END,
       ST_Distance(ad1.point, ST_Transform(sad.shape,2193))
    FROM
       ad1
       JOIN address adr ON adr.adr_id = ad1.adr_id
       JOIN bde.crs_road_name rna2 ON rna2.id = adr.rna_id,
       bde.crs_street_address sad
       JOIN bde.crs_road_name rna ON rna.id = sad.rna_id
    WHERE
       ST_Intersects( sad.shape, ad1.buffer ) AND
       sad.status = 'CURR'
    ),
    ad3( adr_id, sad_id, sad_sufi, match, rank ) AS 
    (
    SELECT
       adr_id,
       sad_id,
       sad_sufi,
       
       match,
       row_number() OVER (
           PARTITION BY adr_id 
           ORDER BY match, dist
           )
    FROM
       ad2
    WHERE
       match < 5 -- Don't link to points on different parcel if not same address
    )
    -- Pick the nearest match
    SELECT
       adr_id,
       sad_id,
       sad_sufi,
       CASE 
            WHEN match=1 THEN 'IGNR'
            WHEN match=2 OR MATCH = 3 THEN 'REPL'
            ELSE 'UNKN'
       END
    FROM
       ad3
    WHERE
       rank = 1;
       
    -- Update the address points
    UPDATE 
       address
    SET
       sad_id = (SELECT sad_id FROM tmp_ad3 WHERE adr_id = address.adr_id),
       sad_sufi = (SELECT sad_sufi FROM tmp_ad3 WHERE adr_id = address.adr_id),
       sad_par_id = NULL,
       status = CASE 
                    WHEN status='UNKN' THEN (SELECT status FROM tmp_ad3 WHERE adr_id = address.adr_id)
                    ELSE status END
    WHERE
       adr_id IN (SELECT adr_id FROM tmp_ad3);

    -- Drop the temp table
    DROP TABLE tmp_ad3; 

    -- Update the parcel ids for the linked address points ..

    UPDATE
        address
    SET
        sad_par_id = (
            SELECT 
                par.id
            FROM
                crs_parcel par
                join crs_street_address sad ON ST_Intersects(sad.shape,par.shape)
            WHERE
                sad.id = address.sad_id AND
                par.toc_code = 'PRIM' AND
                par.status = 'CURR'
            LIMIT 
                1
            )
    WHERE
        job_id = p_job_id AND
        NOT linked AND
        sad_id IS NOT NULL AND
        sad_par_id IS NULL;

    SELECT COUNT(*) INTO l_count FROM address WHERE job_id=p_job_id AND NOT linked AND sad_id IS NULL;
    RETURN l_count;
END
$body$
LANGUAGE plpgsql;


-- Update links to CRS parcels

CREATE OR REPLACE FUNCTION electoral_address.elc_LinkAddressesToParcels
(
    p_job_id INT
)
RETURNS INT
AS
$body$
DECLARE
    l_count INT;
BEGIN
    UPDATE 
        address
    SET
        par_id = (
            SELECT 
                par.id
            FROM
                crs_parcel par
            WHERE
                par.toc_code='PRIM' AND
                par.status='CURR' AND
                ST_Intersects(par.shape, address.shape)
            LIMIT
                1
            )
    WHERE
        job_id = p_job_id AND
        NOT linked AND
        par_id IS NULL;

    DROP TABLE IF EXISTS tmp_par_sad_data;

    CREATE TEMP TABLE tmp_par_sad_data
    (
            par_id INT,
            par_sad_count INT,
            par_range_low INT,
            par_range_high INT,
            PRIMARY KEY (par_id)
    );

    INSERT INTO tmp_par_sad_data
    WITH t( par_id, shape ) AS
    (
    SELECT
        par.id,
        par.shape
    FROM
        crs_parcel par
    WHERE
        par.id IN (
            SELECT par_id 
            FROM address 
            WHERE 
                job_id = p_job_id AND
                NOT linked AND
                par_id IS NOT null AND 
                par_sad_count IS NULL
            )
    )
    SELECT
        t.par_id,
        COALESCE(COUNT(sad.id),0),
        MIN(sad.range_low),
        MAX(COALESCE(sad.range_high,sad.range_low))
    FROM 
        crs_street_address sad
        JOIN t ON ST_Intersects(sad.shape, t.shape)
    GROUP BY
        t.par_id;

    UPDATE
        address
    SET
        par_sad_count = (
            SELECT t.par_sad_count 
            FROM tmp_par_sad_data t 
            WHERE t.par_id=address.par_id),
        par_range_low = (
            SELECT t.par_range_low 
            FROM tmp_par_sad_data t 
            WHERE t.par_id=address.par_id),
        par_range_high = (
            SELECT t.par_range_high 
            FROM tmp_par_sad_data t 
            WHERE t.par_id=address.par_id)
    WHERE
        job_id = p_job_id AND
        NOT linked AND
        par_id IS NOT NULL AND
        par_sad_count IS NULL;

    DROP TABLE tmp_par_sad_data;

    SELECT COUNT(*) INTO l_count FROM address WHERE job_id=p_job_id AND par_id IS NULL;
    RETURN l_count;
END
$body$
LANGUAGE plpgsql;

-- Function to create cluster ids on address

CREATE OR REPLACE FUNCTION electoral_address.elc_CreateAddressClusters
(
    p_job_id INT
)
RETURNS INT
AS
$body$
DECLARE
    l_tolerance DOUBLE PRECISION;
BEGIN
    SELECT same_location_tolerance INTO l_tolerance FROM job WHERE job_id = p_job_id;

    DROP TABLE IF EXISTS tmp_clusters;
    DROP TABLE IF EXISTS tmp_clusters_update;
    
    CREATE TEMP TABLE tmp_clusters
    (
        adr_id INT,
        buffer GEOMETRY,
        cluster_id INT
    );

    CREATE TEMP TABLE tmp_clusters_update
    (
        cluster_new INT,
        cluster_old INT
    );


    INSERT INTO tmp_clusters
    SELECT 
        adr_id,
        ST_Buffer(ST_Transform(shape,2193),l_tolerance/2.0),
        adr_id
    FROM
        address
    WHERE
        job_id = p_job_id;

    CREATE INDEX tmp_buff ON tmp_clusters USING gist(buffer);
    
    ANALYZE tmp_clusters;

    LOOP
        DELETE FROM tmp_clusters_update;
        
        INSERT INTO tmp_clusters_update
        SELECT
            MIN(c1.cluster_id),
            c2.cluster_id
        FROM
            tmp_clusters c1 
            JOIN tmp_clusters c2 
                ON c1.buffer && c2.buffer AND c1.cluster_id < c2.cluster_id
        GROUP BY
            c2.cluster_id;

        EXIT WHEN NOT EXISTS (SELECT * FROM tmp_clusters_update);

        UPDATE tmp_clusters
        SET cluster_id = (SELECT cluster_new FROM tmp_clusters_update WHERE cluster_old=tmp_clusters.cluster_id)
        WHERE cluster_id IN (SELECT cluster_old FROM tmp_clusters_update);
        
    END LOOP;

    -- Renumber clusters from 1
    
    DELETE FROM tmp_clusters_update;
    INSERT INTO tmp_clusters_update
    SELECT DISTINCT dense_rank() OVER (ORDER BY cluster_id), cluster_id FROM tmp_clusters;
    UPDATE tmp_clusters
    SET cluster_id = (SELECT cluster_new FROM tmp_clusters_update WHERE cluster_old=tmp_clusters.cluster_id)
    WHERE cluster_id IN (SELECT cluster_old FROM tmp_clusters_update);

    -- Set up a count of clusters - will only 

    DELETE FROM tmp_clusters_update;
    INSERT INTO tmp_clusters_update
    SELECT count(*), cluster_id FROM tmp_clusters GROUP BY cluster_id;

    -- Update the cluster id

    UPDATE 
        address
    SET 
        cluster_id = COALESCE((
           SELECT 
               lpad(tc.cluster_id::varchar,4,'0')||'/'||tu.cluster_new::varchar 
           FROM 
               tmp_clusters tc
               JOIN tmp_clusters_update tu ON tc.cluster_id=tu.cluster_old
           WHERE 
               tc.adr_id=address.adr_id and 
               tu.cluster_new>1),
           '')
    WHERE
        job_id =p_job_id;

    DROP TABLE tmp_clusters;
    DROP TABLE tmp_clusters_update;

    RETURN 0;
END
$body$
LANGUAGE plpgsql;

-- Update user modifiable address fields  

CREATE OR REPLACE FUNCTION electoral_address.elc_updateAddress
(
    p_adr_id INT,
    p_status address.status%TYPE,
    p_housenumber address.housenumber%TYPE,
    p_sad_id INT,
    p_rna_id INT,
    p_notes address.notes%TYPE,
    p_ignore_errors BOOLEAN
)
RETURNS
    INT
AS
$body$
DECLARE
    l_housenumber address.housenumber%type;
    l_warning_codes address.warning_codes%TYPE;
    l_warnings_accepted address.warnings_accepted%TYPE;
    l_sad_par_id INT;
    l_sad_id INT;
    l_sad_sufi INT;
    l_rna_id INT;
    l_rna_name crs_road_name.name%TYPE;
    l_rcl_id INT;
    l_point GEOMETRY;
BEGIN
    SELECT housenumber, sad_id, sad_sufi,  sad_par_id, rna_id, rcl_id, warning_codes, warnings_accepted   -- Remove sufi
    INTO l_housenumber, l_sad_id, l_sad_sufi, l_sad_par_id, l_rna_id, l_rcl_id, l_warning_codes, l_warnings_accepted
    FROM address
    WHERE adr_id = p_adr_id;

    -- If the user has edited the house number, then can accept number modified
    -- Warning is only for addresses modified by script on upload.

    IF l_housenumber <> p_housenumber AND l_warnings_accepted NOT LIKE '%NUMM%' THEN
        l_warnings_accepted := l_warnings_accepted || ' NUMM';
    END IF;

    -- Sort out the linkage from sad pt to parcel
    IF p_sad_id IS NULL THEN
        l_sad_par_id = NULL;
    ELSE
        IF l_sad_id IS NULL OR l_sad_id <> p_sad_id THEN
            SELECT 
                par.id
            INTO
                l_sad_par_id
            FROM
                crs_parcel par
                join crs_street_address sad ON ST_Intersects(sad.shape,par.shape)
            WHERE
                sad.id = p_sad_id AND
                par.toc_code = 'PRIM' AND
                par.status = 'CURR'
            LIMIT 
                1;
        END IF;
    END IF;

    -- Sort out the linkage road name to centreline

    IF p_rna_id IS NULL THEN
        l_rcl_id = NULL;
        l_rna_id = NULL;
    ELSIF l_rna_id IS NULL OR l_rna_id <> p_rna_id THEN
        SELECT
            id, name
        INTO
            l_rna_id, l_rna_name
        FROM
            crs_road_name
        WHERE
            id = p_rna_id;
    
        IF l_rna_id IS NOT NULL THEN
            SELECT 
                ST_Transform( shape, 2193 ) INTO l_point
            FROM
                address
            WHERE
                adr_id = p_adr_id;
                
            SELECT
                rcl.id INTO l_rcl_id
            FROM
                crs_road_ctr_line rcl
                JOIN crs_road_name_asc ras ON ras.rcl_id = rcl.id
            WHERE
                ras.rna_id = p_rna_id AND
                rcl.status = 'CURR'
            ORDER BY
                ST_Distance( ST_Transform(shape,2193), l_point )
            LIMIT 1;
        
            IF l_rcl_id IS NULL THEN
                RAISE EXCEPTION 'Invalid road id supplied to elc_UpdateAddressRoad';
            END IF;
    
        END IF;
    END IF;

    IF p_ignore_errors THEN
        l_warnings_accepted = TRIM(l_warnings_accepted || ' ' || l_warning_codes);
    END IF;

    -- get sufi related to sad_id
   
        SELECT 
            sufi
        INTO
            l_sad_sufi
        FROM
            crs_street_address
        WHERE
            id = p_sad_id AND
            status = 'CURR';

    UPDATE address
    SET
        status = p_status,
        housenumber = p_housenumber,
        notes = p_notes,
        sad_id = p_sad_id,
        sad_sufi = l_sad_sufi, 
        sad_par_id = l_sad_par_id,
        rcl_id = l_rcl_id,
        rna_id = l_rna_id,
        warnings_accepted = l_warnings_accepted
    WHERE
        adr_id = p_adr_id;

    RETURN p_adr_id;
END
$body$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION electoral_address.elc_GetRoadList
(
    p_adr_id INT,
    p_radius DOUBLE PRECISION
)
RETURNS TABLE
(
    rna_id INT,
    roadname crs_road_name.name%TYPE,
    distance DOUBLE PRECISION
)
AS
$body$
DECLARE
    l_point GEOMETRY;
    l_buffer GEOMETRY;
BEGIN
    SELECT ST_Transform(shape,2193) INTO l_point 
    FROM address 
    WHERE adr_id=p_adr_id;

    l_buffer := ST_Transform(ST_Buffer(l_point,p_radius,4), 4167 );
    RETURN QUERY

    -- Find the nearest instance of each road name around the 
    -- address point

    WITH rd1( rna_id1, roadname1, distance1 ) AS
    (
        SELECT
           rna.id,
           rna.name,
           MIN(ST_Distance( ST_Transform( rcl.shape, 2193 ), l_point))
        FROM
           crs_road_ctr_line rcl
           JOIN crs_road_name_asc ras ON ras.rcl_id = rcl.id
           JOIN crs_road_name rna ON rna.id = ras.rna_id,
           address adr
        WHERE
            ST_Intersects( rcl.shape, l_buffer ) AND
            rcl.status = 'CURR' AND
            rna.status = 'CURR'
        GROUP BY
           rna.id,
           rna.name
    ),
    rd2 (rna_id1, roadname1, distance1, rank ) AS
    (
        SELECT
           rna_id1,
           roadname1,
           distance1,
           row_number() OVER (PARTITION BY roadname1 ORDER BY distance1)
        FROM
           rd1
    )
    SELECT
       rna_id1,
       roadname1,
       distance1
    FROM 
       rd2
    WHERE
       rank = 1;
END
$body$
LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION electoral_address.elc_GetAddressList
(
    p_adr_id INT,
    p_radius DOUBLE PRECISION
)
RETURNS TABLE
(
    sad_id INT,
    housenumber crs_street_address.house_number%TYPE,
    roadname crs_road_name.name%TYPE,
    sameparcel BOOLEAN,
    distance DOUBLE PRECISION
)
AS
$body$
DECLARE
    l_point GEOMETRY;
    l_buffer GEOMETRY;
    l_pargeom GEOMETRY;
BEGIN
    SELECT 
        ST_Transform(adr.shape,2193),
        par.shape
    INTO 
        l_point,
        l_pargeom
    FROM 
        address adr
        LEFT OUTER JOIN crs_parcel par ON par.id = adr.par_id
    WHERE 
        adr.adr_id=p_adr_id;

    l_buffer := ST_Transform(ST_Buffer(l_point,p_radius,4), 4167 );

    RETURN QUERY
    SELECT
       sad.id,
       sad.house_number,
       rna.name,
       ST_Intersects( sad.shape, l_pargeom ),
       ST_Distance( ST_Transform( sad.shape, 2193 ), l_point)
    FROM
       crs_street_address sad
       JOIN crs_road_name rna ON rna.id = sad.rna_id
    WHERE
       ST_Intersects( sad.shape, l_buffer ) AND
       sad.status = 'CURR';
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_MergedAddresses
(
    p_mrg_id INT
)
RETURNS TABLE
(
    adr_id INT
)
AS
$body$
    SELECT adr_id FROM address WHERE merge_adr_id=$1
$body$
LANGUAGE SQL;

CREATE OR REPLACE FUNCTION electoral_address.elc_LinkMergedAddress
(
    p_mrg_id INT,
    p_adr_ids INT[]
)
RETURNS BOOLEAN
AS
$body$
DECLARE 
    l_cluster_id address.cluster_id%TYPE;
BEGIN
    UPDATE address 
    SET merge_adr_id=p_mrg_id 
    WHERE adr_id IN (SELECT unnest(p_adr_ids));

    SELECT
        CASE WHEN MIN(cluster_id)=MAX(cluster_id) THEN MIN(cluster_id) ELSE NULL END
        INTO l_cluster_id
        FROM ADDRESS
        WHERE merge_adr_id = p_mrg_id;

    UPDATE address SET ismerged=TRUE, cluster_id=l_cluster_id WHERE adr_id=p_mrg_id;



    RETURN TRUE;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_unmergedAddress
(
    p_mrg_id INT
)
RETURNS BOOLEAN
AS
$body$
BEGIN
    IF EXISTS (SELECT * FROM address WHERE adr_id=p_mrg_id AND ismerged) THEN
        UPDATE address SET merge_adr_id=NULL WHERE merge_adr_id=p_mrg_id;
        DELETE FROM address WHERE adr_id = p_mrg_id;
    END IF;
    RETURN TRUE;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_findAddressIds
(
    p_job_id INT,
    p_wkt TEXT
)
RETURNS TABLE 
(
    adr_id INT,
    poffset DOUBLE PRECISION
)
AS
$body$
DECLARE
    l_search GEOMETRY;
    l_srsid INT;
    l_point GEOMETRY;
BEGIN
    l_search := ST_GeomFromText( p_wkt, 4167 );
    l_point := ST_Transform( ST_Centroid(l_search),2193);
    RETURN QUERY
        SELECT
            address.adr_id,
            ST_Distance(l_point,ST_Transform(shape,2193))
        FROM
            address
        WHERE
            job_id = p_job_id AND
            shape && l_search;
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_findLandonlineAddresses
(
    p_wkt TEXT
)
RETURNS TABLE 
(
    sad_id INT,
    rna_id INT,
    roadname crs_road_name.name%TYPE,
    housenumber crs_street_address.house_number%TYPE,
    poffset DOUBLE PRECISION
)
AS
$body$
DECLARE
    l_search GEOMETRY;
    l_srsid INT;
    l_point GEOMETRY;
BEGIN
    l_search := ST_GeomFromText( p_wkt, 4167 );
    l_point := ST_Transform( ST_Centroid(l_search),2193);
    RETURN QUERY
        SELECT
            sad.id,
            rna.id,
            rna.name,
            sad.house_number,
            ST_Distance(l_point,ST_Transform(sad.shape,2193))
        FROM
            crs_street_address sad
            JOIN crs_road_name rna ON rna.id = sad.rna_id
        WHERE
            ST_Intersects(l_search,shape) AND
            sad.status='CURR';
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_findLandonlineRoads
(
    p_wkt TEXT
)
RETURNS TABLE 
(
    rna_id INT,
    rcl_id INT,
    roadname crs_road_name.name%TYPE,
    poffset DOUBLE PRECISION
)
AS
$body$
DECLARE
    l_search GEOMETRY;
    l_srsid INT;
    l_point GEOMETRY;
BEGIN
    l_search := ST_GeomFromText( p_wkt, 4167 );
    l_point := ST_Transform( ST_Centroid(l_search),2193);
    RETURN QUERY
        WITH rcl(id, loffset) AS
        (
            SELECT
                id,
                ST_Distance(l_point,ST_Transform(shape,2193))
            FROM
                crs_road_ctr_line
            WHERE
                ST_Intersects( l_search, shape ) AND
                status='CURR'
        )
        SELECT
            rna.id,
            rcl.id,
            rna.name,
            rcl.loffset
        FROM
            rcl
            JOIN crs_road_name_asc ras ON ras.rcl_id = rcl.id
            JOIN crs_road_name rna ON rna.id=ras.rna_id
        WHERE
            rna.status='CURR';
END
$body$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION electoral_address.elc_GetLandonlineAddressGeometry
(
    p_sad_id INTEGER
)
RETURNS
    text
AS
$body$
    SELECT
        ST_AsText( shape )
    FROM
        crs_street_address
    WHERE
        id = $1;
$body$
LANGUAGE SQL;


CREATE OR REPLACE FUNCTION electoral_address.elc_GetLandonlineRoadGeometry
(
    p_rcl_id INTEGER
)
RETURNS
    text
AS
$body$
    SELECT
        ST_AsText( shape )
    FROM
        crs_road_ctr_line
    WHERE
        id = $1;
$body$
LANGUAGE SQL;

---------------------------------------------------------------------------
-- Function to list the electoral address functions

CREATE OR REPLACE FUNCTION electoral_address.elc_ListFunctions() 
RETURNS TABLE
(
    signature TEXT,
    fcomment TEXT
)
AS
$body$
    SELECT
        proname || '(' || pg_get_function_identity_arguments(oid) || ')',
        obj_description(oid, 'pg_proc')
    FROM
        pg_proc
    WHERE
        pronamespace=(SELECT oid FROM pg_namespace WHERE nspname = 'electoral_address')  
    ORDER BY proname
$body$ 
LANGUAGE SQL;

---------------------------------------------------------------------------
-- Function to set common settings of functions, version comment, owner, 
-- search path

CREATE OR REPLACE FUNCTION _applyFunctionSettings() RETURNS BOOLEAN AS $body$
DECLARE
    v_comment TEXT;
    v_pcid    TEXT;
BEGIN
    FOR v_pcid, v_comment IN
        SELECT signature, fcomment FROM elc_ListFunctions()
    LOOP
        IF v_comment IS NULL THEN
            v_comment := '';
        ELSE
            v_comment := E'\n\n' || v_comment;
        END IF;
       
        v_comment := 'Version: ' ||  '$Id: ' || E'\n' ||
                     'Installed: ' || to_char(current_timestamp,'YYYY-MM-DD HH:MI') ||
                    v_comment;
       
        EXECUTE 'COMMENT ON FUNCTION ' || v_pcid || ' IS '
            || quote_literal( v_comment );

        EXECUTE 'ALTER FUNCTION ' || v_pcid || ' OWNER TO electoral_dba';
        EXECUTE 'ALTER FUNCTION ' || v_pcid || ' SET search_path FROM CURRENT';
    END LOOP;
   
    RETURN TRUE;
END
$body$ 
LANGUAGE plpgsql;

SELECT _applyFunctionSettings();
DROP FUNCTION _applyFunctionSettings();
