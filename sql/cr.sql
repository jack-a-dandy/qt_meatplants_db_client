begin;
drop domain if exists pos_decimal cascade; 
create domain  pos_decimal as decimal check(value > 0);
drop domain if exists history_year cascade; 
create domain  history_year as int check(value > 0 and value <= date_part('year',current_date));
drop domain if exists username cascade; 
create domain  username as varchar(16) check(value ~ '^[a-z0-9](([-_a-z0-9]{1,14})?[a-z0-9])?$');
/*drop domain if exists phone_number cascade; create domain  phone_number as varchar check(value ~ '^\(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5} ?-?[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?$');
*/
drop table if exists cities cascade; create table cities(
id int not null primary key,
name varchar not null unique check(ltrim(name)<>'')
);

drop table if exists property_types cascade; create table property_types(
id int not null primary key,
name varchar not null unique check(ltrim(name)<>'')
);

drop table if exists meatplants cascade; create table meatplants(
id int not null primary key,
name varchar not null unique check(ltrim(name)<>''),
city_id int not null references cities(id) ON DELETE CASCADE ON UPDATE CASCADE,
phone varchar not null unique check(ltrim(name)<>''),
year history_year not null,
property_type_id int not null references property_types(id) ON DELETE CASCADE ON UPDATE CASCADE
);

drop table if exists meatplants_managers cascade; create table meatplants_managers(
id int not null primary key,
meatplant_id int not null references meatplants(id) ON DELETE CASCADE ON UPDATE CASCADE,
user_name username not null,
unique(user_name)
);

drop table if exists product_types cascade; create table product_types(
id int not null primary key,
name varchar not null unique check(ltrim(name)<>'')
);

drop table if exists product_names cascade; create table product_names(
id int not null primary key,
name varchar not null unique check(ltrim(name)<>'')
);

drop table if exists products cascade; create table products(
id int not null primary key,
type_id int not null references product_types(id) ON DELETE CASCADE ON UPDATE CASCADE,
name_id int not null references product_names(id) ON DELETE CASCADE ON UPDATE CASCADE,
unique(type_id,name_id)
);

drop table if exists products_of_plants cascade; create table products_of_plants(
	id int not null primary key,
	meatplant_id int not null references meatplants(id) ON DELETE CASCADE ON UPDATE CASCADE,
	product_id int not null references products(id) ON DELETE CASCADE ON UPDATE CASCADE,
	volume pos_decimal not null,
	price_per_kg pos_decimal not null,
  unique(meatplant_id,product_id)
);

drop table if exists clients cascade; create table clients(
id int not null primary key,
name varchar not null unique check(ltrim(name)<>''),
phone varchar not null unique check(ltrim(name)<>''),
address varchar not null unique check(ltrim(name)<>''),
city_id int not null references cities(id) ON DELETE CASCADE ON UPDATE CASCADE,
login username not null unique
);

drop table if exists orders cascade; create table orders(
 id int not null primary key,
 "date" date not null DEFAULT CURRENT_DATE check("date" <= CURRENT_DATE),
 volume pos_decimal not null,
 client_id int not null references clients(id) ON DELETE CASCADE ON UPDATE CASCADE,
 product_id int not null references products_of_plants(id) ON DELETE CASCADE ON UPDATE CASCADE
);

 drop sequence if exists cities_sequence; 

 create sequence cities_sequence start 1;

 CREATE OR REPLACE FUNCTION cities_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('cities_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists cities_before_insert_trigger on cities cascade; 
 create trigger cities_before_insert_trigger
 BEFORE INSERT
 ON cities
 FOR EACH ROW
 EXECUTE PROCEDURE cities_before_insert();

 drop sequence if exists prop_types_sequence; create sequence prop_types_sequence start 1;

 CREATE OR REPLACE FUNCTION prop_types_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('prop_types_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists prop_types_before_insert_trigger on property_types cascade; create trigger prop_types_before_insert_trigger
 BEFORE INSERT
 ON property_types
 FOR EACH ROW
 EXECUTE PROCEDURE prop_types_before_insert();

 drop sequence if exists meatplants_sequence; create sequence meatplants_sequence start 1;

 CREATE OR REPLACE FUNCTION meatplants_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('meatplants_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists meatplants_before_insert_trigger on meatplants cascade; create trigger meatplants_before_insert_trigger
 BEFORE INSERT
 ON meatplants
 FOR EACH ROW
 EXECUTE PROCEDURE meatplants_before_insert();

 drop sequence if exists meatplants_managers_sequence; create sequence meatplants_managers_sequence start 1;

 CREATE OR REPLACE FUNCTION meatplants_managers_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('meatplants_managers_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists meatplants_managers_before_insert_trigger on meatplants_managers cascade; create trigger meatplants_managers_before_insert_trigger
 BEFORE INSERT
 ON meatplants_managers
 FOR EACH ROW
 EXECUTE PROCEDURE meatplants_managers_before_insert();

 drop sequence if exists product_types_sequence; create sequence product_types_sequence start 1;

 CREATE OR REPLACE FUNCTION product_types_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('product_types_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists product_types_before_insert_trigger on product_types cascade; create trigger product_types_before_insert_trigger
 BEFORE INSERT
 ON product_types
 FOR EACH ROW
 EXECUTE PROCEDURE product_types_before_insert();

 drop sequence if exists product_names_sequence; create sequence product_names_sequence start 1;

 CREATE OR REPLACE FUNCTION product_names_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('product_names_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists product_names_before_insert_trigger on product_names cascade; create trigger product_names_before_insert_trigger
 BEFORE INSERT
 ON product_names
 FOR EACH ROW
 EXECUTE PROCEDURE product_names_before_insert();

 drop sequence if exists products_sequence; create sequence products_sequence start 1;

 CREATE OR REPLACE FUNCTION products_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('products_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists products_before_insert_trigger on products cascade; create trigger products_before_insert_trigger
 BEFORE INSERT
 ON products
 FOR EACH ROW
 EXECUTE PROCEDURE products_before_insert();

 drop sequence if exists products_of_plants_sequence; create sequence products_of_plants_sequence start 1;

 CREATE OR REPLACE FUNCTION products_of_plants_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('products_of_plants_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists products_of_plants_before_insert_trigger on products_of_plants cascade; create trigger products_of_plants_before_insert_trigger
 BEFORE INSERT
 ON products_of_plants
 FOR EACH ROW
 EXECUTE PROCEDURE products_of_plants_before_insert();

 drop sequence if exists clients_sequence; create sequence clients_sequence start 1;

 CREATE OR REPLACE FUNCTION clients_before_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
   New.id:=nextval('clients_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists clients_before_insert_trigger on clients cascade; create trigger clients_before_insert_trigger
 BEFORE INSERT
 ON clients
 FOR EACH ROW
 EXECUTE PROCEDURE clients_before_insert();

 drop sequence if exists orders_sequence; create sequence orders_sequence start 1;

 CREATE OR REPLACE FUNCTION orders_before_insert()
 RETURNS "trigger" AS
 $BODY$
 DECLARE myear integer;
 BEGIN
   myear := (select m.year from meatplants m join products_of_plants pop on pop.meatplant_id = m.id where pop.id = new.product_id);
   if myear > date_part('year',new.date) then
   	raise exception 'Дата заказа не может быть раньше года открытия комбината.' using detail='Ошибочный заказ: ('||
   	concat_ws(',',cast(new.date as text),cast(new.volume as text),coalesce(cast(new.client_id as text), 'null'::text),cast(new.product_id as text))
   	||')';
   end if;
   New.id:=nextval('orders_sequence');
   Return NEW;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists orders_before_insert_trigger on orders cascade; 
 create trigger orders_before_insert_trigger
 BEFORE INSERT
 ON orders
 FOR EACH ROW
 EXECUTE PROCEDURE orders_before_insert();

 CREATE OR REPLACE FUNCTION orders_after_update()
 RETURNS "trigger" AS
 $BODY$
 DECLARE myear integer;
 BEGIN
 	myear := (select m.year from meatplants m join products_of_plants pop on pop.meatplant_id = m.id where pop.id = new.product_id);
   if myear > date_part('year',new.date) then
    /*alter table orders DISABLE TRIGGER orders_after_update_trigger;*/
    update orders set date = old.date where id = new.id;
    /*alter table orders ENABLE TRIGGER orders_after_update_trigger;*/
   	raise exception 'Дата заказа не может быть раньше года открытия комбината.' using detail='Ошибочный заказ: ('||
   	concat_ws(',',cast(new.id as text),cast(new.date as text),cast(new.volume as text),coalesce(cast(new.client_id as text), 'null'::text),cast(new.product_id as text))
   	||')';
   end if;
   return null;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists orders_after_update_trigger on orders cascade; create trigger orders_after_update_trigger
 after UPDATE
 ON orders
 FOR EACH ROW
 EXECUTE PROCEDURE orders_after_update();

 CREATE OR REPLACE FUNCTION managers_after_insert()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
 	if (SELECT 1 FROM pg_roles WHERE rolname=new.user_name) <> 1 then
 		delete from meatplants_managers where id = new.id;
 	end if;
 	return null;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists managers_after_insert_trigger on meatplants_managers cascade; create trigger managers_after_insert_trigger
 after INSERT
 ON meatplants_managers
 FOR EACH ROW
 EXECUTE PROCEDURE managers_after_insert();

 CREATE OR REPLACE FUNCTION meatplants_before_update()
 RETURNS "trigger" AS
 $BODY$
 DECLARE older integer;
 BEGIN
 	older := (select count(1) from orders o join products_of_plants pop on pop.id = o.product_id where pop.meatplant_id = new.id and date_part('year',o.date)<new.year);
   if older > 0 then
   	raise exception 'Год открытия комбината не может быть позже года одного из заказов.' using detail='Ошибочный комбинат: ('||
   	concat_ws(',',cast(new.id as text),cast(new.name as text))
   	||')';
   end if;
   return new;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists meatplants_before_update_trigger on meatplants cascade; create trigger meatplants_before_update_trigger
 BEFORE update
 ON meatplants
 FOR EACH ROW
 EXECUTE PROCEDURE meatplants_before_update();


CREATE OR REPLACE FUNCTION clients_delete()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
	begin
 	execute 'set role admin; drop user if exists ' || old.login || ';';
	exception when others then
		return old;
	end;
 	return old;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;
 
 drop trigger if exists сlients_delete_trigger on clients cascade; create trigger сlients_delete_trigger
 before delete
 ON clients
 FOR EACH ROW
 EXECUTE PROCEDURE clients_delete();


 CREATE OR REPLACE FUNCTION clients_after_update()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
 	execute 'set role admin; alter user ' || old.login || ' rename to ' || new.login || ';';
 	return new;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists сlients_after_update_trigger on clients cascade; 
 create trigger сlients_after_update_trigger
 after update
 ON clients
 FOR row when(old.login <> new.login)
 EXECUTE PROCEDURE clients_after_update();

 CREATE OR REPLACE FUNCTION managers_delete()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
    if (select count(*) from meatplants_managers where user_name = old.user_name) = 0 then
 	execute 'set role admin; drop user if exists ' || old.user_name || ';';
 	end if;
 	return null;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists managers_delete_trigger on meatplants_managers cascade; create trigger managers_delete_trigger
 after delete
 ON meatplants_managers
 FOR EACH ROW
 EXECUTE PROCEDURE managers_delete();

 CREATE OR REPLACE FUNCTION managers_after_update()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
 	execute 'set role admin; alter user ' || old.user_name || ' rename to ' || new.user_name || ';';
 	return new;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists managers_after_update_trigger on meatplants_managers cascade; 
 create trigger managers_after_update_trigger
 after update
 ON meatplants_managers
 FOR row when(old.user_name <> new.user_name)
 EXECUTE PROCEDURE managers_after_update();

 /*CREATE OR REPLACE FUNCTION products_of_plants_delete()
 RETURNS "trigger" AS
 $BODY$
 BEGIN
    if (select count(*) from products_of_plants pop join products p on p.id = pop.product_id where p.id = old.product_id) = 0 then
 	delete from products where id = old.product_id;

 	end if;
 END;
 $BODY$
 LANGUAGE 'plpgsql' VOLATILE;

 drop trigger if exists  cascade; create trigger managers_delete_trigger
 after delete
 ON meatplants_managers
 FOR EACH ROW
 EXECUTE PROCEDURE managers_delete();
 */
 commit;