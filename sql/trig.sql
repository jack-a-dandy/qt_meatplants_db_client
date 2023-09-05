CREATE OR REPLACE FUNCTION remove_unused_city()
  RETURNS trigger as
$$
BEGIN
 if (select count(*) from meatplants where city_id = old.city_id) = 0 and  (select count(*) from clients where city_id = old.city_id) = 0 then
 	delete from cities where id = old.city_id;
 end if;
 return NEW;
END;
$$
LANGUAGE 'plpgsql';

create trigger meatplants_city_update_trigger before update of year on editions for row when (old.city_id is distinct from new.city_id) execute procedure remove_unused_city();
