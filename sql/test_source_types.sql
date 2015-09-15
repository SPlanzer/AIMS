set search_path = electoral_address, public;

delete from source_type;
alter sequence source_type_stp_id_seq restart with 1;

insert into  source_type (name, fileext, srsid, reader_type, reader_params )
values 
('Manawatu DC format','tab',2193,'OgrReader',':roadname:Road_Name:number:Number_Issued'),
('Dunedin DC format','shp',2193,'OgrReader',':roadname:roadname roadtype/lookup_road_type1:number:address');
