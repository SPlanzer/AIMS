set search_path = electoral_address, public;

delete from supplier;

insert into  supplier (name, stp_id, stt_id)
values 
('MDC_supplier',(SELECT stp_id FROM source_type where name='MDC format'), 930),
('DCC_supplier',(SELECT stp_id FROM source_type where name='DDC format'), 961);
