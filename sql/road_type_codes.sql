set search_path to electoral_address, public;

delete from code where code_type='lookup_road_type1';
delete from code where code_type='code_type' and code='lookup_road_type1';

insert into code (code_type, code, value ) values
('code_type','lookup_road_type1','Lookup values to replace the road type abbreviations - DDC'),
('lookup_road_type1','ALY','ALLEY'),
('lookup_road_type1','AVE','AVENUE'),
('lookup_road_type1','CLSE','CLOSE'),
('lookup_road_type1','CRES','CRESCENT'),
('lookup_road_type1','DRV','DRIVE'),
('lookup_road_type1','GDNS','GARDENS'),
('lookup_road_type1','LN','LANE'),
('lookup_road_type1','PDE','PARADE'),
('lookup_road_type1','PL','PLACE'),
('lookup_road_type1','RD','ROAD'),
('lookup_road_type1','RD EAST','ROAD EAST'),
('lookup_road_type1','RD WEST','ROAD WEST'),
('lookup_road_type1','RD NORTH','ROAD NORTH'),
('lookup_road_type1','RD SOUTH','ROAD SOUTH'),
('lookup_road_type1','ST','STREET'),
('lookup_road_type1','ST EAST','STREET EAST'),
('lookup_road_type1','ST WEST','STREET WEST'),
('lookup_road_type1','ST NORTH','STREET NORTH'),
('lookup_road_type1','ST SOUTH','STREET SOUTH'),
('lookup_road_type1','STPS','STEPS'),
('lookup_road_type1','TCE','TERRACE');
