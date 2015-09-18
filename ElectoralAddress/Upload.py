
from getpass import getuser
from Job import Job
from datetime import datetime
import os.path
import time
import re
import Database


class Upload( object ):

    @classmethod
    def CreateUpload( cls, filename=None ):
        if not filename:
            filename = Upload.defaultNewFilename()
        id = Database.executeScalar('elc_CreateUpload',getuser(),filename)
        return Upload(id)

    @classmethod
    def list( cls ):
        uploads=[]
        for r in Database.execute('select upl_id, created_by, creation_time, filename, n_insert, n_delete from elc_GetUploadDetails(NULL)'):
            created_date = r[2].strftime('%d-%b-%Y')
            uploads.append(dict(
                upl_id=r[0],
                created_by=r[1],
                creation_time=r[2],
                created_date=created_date,
                filename=r[3],
                n_insert=r[4],
                n_delete=r[5]
                ))
        return uploads
        
    def __init__( self, id ):
        r = Database.executeRow('select created_by, creation_time, filename, n_insert, n_delete from elc_GetUploadDetails(%s)',id)
        self._id = id
        self._created_by = r[0]
        self._creation_time = r[1]
        self._filename = r[2]
        self._n_insert = r[3]
        self._n_delete = r[4]

    @classmethod
    def defaultNewFilename( cls, upload_date=None ):
        if not isinstance(upload_date,datetime):
            upload_date = datetime.now()
        return 'sad_'+upload_date.strftime('%d%b%y')+'.sql'

    def id( self ): return self._id
    def created_by( self ): return self._created_by
    def creation_time( self ): return self._creation_time
    def filename( self ): return self._filename
    def n_insert( self ): return self._n_insert
    def n_delete( self ): return self._n_delete

    def defaultFilename( self ):
        return Upload.defaultNewFilename( self._creation_time )

    def addJob( self, job ):
        if type(job) == int:
            job = Job(job)
        job.addToUpload( self )
        job.save()

    def writeSql( self, filename ):
        sqlfile = open(filename,'w')
        basename = os.path.splitext(os.path.basename(filename))[0]

        txtfilename = os.path.splitext(filename)[0] + '.txt'
        if txtfilename == filename:
            txtfilename = txtfilename + '.txt'
        txtfile = open(txtfilename,'w')

        # Header
        sqlfile.write("-- Bulk update of crs_street_address\n")
        sqlfile.write("-- Upload id: %d\n" % (self._id,))
        sqlfile.write("-- Created by: %s\n" % (self._created_by,))
        sqlfile.write("-- Created on: %s\n" % 
                      (self._creation_time.strftime('%d %B %Y at %H:%M'),))
        sqlfile.write("\n")

        # Insertions
        sqlfile.write("\n")
        nins = 0
        for r in Database.execute('SELECT housenumber, range_low, range_high, status, rcl_id, rna_id, wkt, sufi from elc_UploadNewAddresses(%s)',self._id):
            m = re.search(r"(\d+)(\.?\d*)\s+(\-\d+\.?\d*)",r[6])
            wkt = '1 POINT(%d%s %s)'%(int(m.group(1))-160,m.group(2),m.group(3))
            range_high = r[2] if r[2] != None else 'null'       
            if r[3] == "DELE": status = "HIST" 
            else: status = "CURR"
            if r[3] == 'NEWA': sufi = 'null'
            else: sufi = r[7] 
            unofficial_flag = "N"

            sqlfile.write('''
       INSERT INTO crs_street_address_stage(house_number, range_low, range_high, status, unofficial_flag, rcl_id, rna_id, shape, sufi) VALUES
          ('%s',%s,%s,'%s','%s',%d,%d,'%s', %s);''' % (r[0],r[1], range_high,status,unofficial_flag,r[4],r[5],wkt, sufi))
            nins += 1
        sqlfile.write("\n")

        sqlfile.write("\n")
        sqlfile.write("       EXECUTE PROCEDURE cp_cel_AddressStageUpdate();\n")
        sqlfile.write("\n")
        sqlfile.close()

        txtfile.write('''
FTP the attached "%s" file to the production database server (crsprd1).
As the user "crsprd" run the script as follows:

sqf %s

The expected output is:

Database selected.

(constant)


Bulk insert of street addresses: id %d

1 row(s) retrieved.

1 row(s) inserted.            ... repeated %d times

(constant)

Bulk update completed: id %d

1 row(s) retrieved.

Database closed.
''' % (basename,basename,self._id,nins,self._id))
        txtfile.close()
        Database.execute('elc_SetUploadFilename',self._id,basename)
