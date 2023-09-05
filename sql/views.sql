begin;
/*Симметричное внутреннее соединение с условием (два запроса с условием отбора по внешнему ключу, два – по датам)*/
drop function orders_between_dates;
create or replace function orders_between_dates(date1 date, date2 date)
    returns table
            (
                id        int,
                name       varchar,
                type varchar,
                meatplant   varchar,
                city           varchar,
                volume     pos_decimal,
                "date"  date
            )
as
$$
begin
 return query select o.id,pn.name,pt.name,m.name,c.name,o.volume,o.date 
 from orders o join products_of_plants pop on pop.id = o.product_id 
 join products p on pop.product_id = p.id join product_names pn on pn.id = p.name_id 
 join product_types pt on pt.id = p.type_id join clients c on c.id = o.client_id 
 join meatplants m on m.id = pop.meatplant_id
where o.date between date1 and date2 
order by o.date DESC;
end;
$$ language plpgsql security definer;

revoke execute on function orders_between_dates(date, date) from public;
grant execute on function orders_between_dates(date, date) to client;



drop function plants_opened_after_year; 
create or replace function plants_opened_after_year(cyear int)
    returns table
            (
                id        int,
                name       varchar,
                city varchar,
                year   history_year,
                prop_type           varchar,
                phone     varchar
            )
as
$$
begin
 return query select m.id,m.name,c.name,m.year,pt.name,m.phone 
 from meatplants m join cities c on c.id = m.city_id join property_types pt 
 on pt.id = m.property_type_id 
where m.year >= cyear order by m.year,c.name,m.name;
end;
$$ language plpgsql security definer;
revoke execute on function plants_opened_after_year(int) from public;
grant execute on function plants_opened_after_year(int) to client;


drop function products_of_choosed_plant; 
create or replace function products_of_choosed_plant(cid int)
    returns table
            (
            	id int,
            	"type"       varchar,
                name       varchar,
                price_per_kg pos_decimal,
                volume   pos_decimal
            )
as
$$
begin
 return query select pop.id,pt.name,pn.name,pop.price_per_kg,pop.volume 
 from products_of_plants pop 
 join products p on p.id = pop.product_id
 join product_types pt on pt.id = p.type_id join product_names pn on pn.id = p.name_id 
 join meatplants m on m.id = pop.meatplant_id
where m.id = cid
order by pt.name,pn.name;
end;
$$ language plpgsql security definer;

revoke execute on function products_of_choosed_plant(int) from public;
grant execute on function products_of_choosed_plant(int) to client;


drop function product_clients; create or replace function product_clients(id int)
    returns table
            (
                name       varchar,
                city varchar,
                address          varchar,
                phone     varchar
            )
as
$$
begin
 return query select cl.name,c.name,cl.address,cl.phone from clients cl join cities c on c.id = cl.city_id join orders o on o.client_id = cl.id
where o.product_id = id
order by c.name,cl.name;
end;
$$ language plpgsql security definer;

revoke execute on function product_clients(int) from public;
grant execute on function product_clients(int) to manager;


drop function clients_orders;

create or replace function clients_orders(cid int)
    returns table
            (
                id       int,
                typ  varchar,
                name          varchar,
                volume  pos_decimal,
                "date" date
            )
as
$$
begin
 return query select o.id,pt.name,pn.name,o.volume,o.date 
			from orders o join products_of_plants pop on o.product_id = pop.id 
			join products p on pop.product_id = p.id 
			join product_types pt on pt.id = p.type_id 
			join product_names pn on pn.id = p.name_id 
			where o.client_id = cid
			order by o.date desc;
end;
$$ language plpgsql security definer;

revoke execute on function clients_orders(int) from public;
grant execute on function clients_orders(int) to manager;

/*симметричное внутреннее соединение без условия (три запроса)*/

drop view if exists meatplants_view; create view meatplants_view as
select m.id,m.name,c.name as city,m.year,m.phone,pt.name as prop_type from meatplants m join cities c on c.id = m.city_id join property_types pt on pt.id = m.property_type_id
order by m.name,city;

grant select on meatplants_view to client;

drop view if exists clients_view; create view clients_view as
select c.id,c.name,ci.name as city,c.phone,c.address from clients c join cities ci on ci.id = c.city_id
order by city,c.name;

grant select on clients_view to manager;

drop view if exists managers_view; create view managers_view as
select ma.id,m.name,c.name as city,ma.user_name from meatplants_managers ma join meatplants m on m.id = ma.meatplant_id join cities c on m.city_id = c.id
order by ma.user_name;

grant select on managers_view to admin;

/*левое внешнее соединение;*/
drop view if exists clients_in_cities; 
create view clients_in_cities as
select c.name as city, cl.name, cl.phone from cities c 
left join clients cl on c.id = cl.city_id
order by city,cl.name;

grant select on clients_in_cities to manager;

/*правое внешнее соединение*/ 
drop view if exists meatplants_by_prop_type; 

create view meatplants_by_prop_type as
select m.id,pt.name as prop_type,m.name,c.name as city 
from meatplants m 
right join property_types pt on pt.id = m.property_type_id 
join cities c on c.id = m.city_id 
order by prop_type,city,m.name; 

grant select on meatplants_by_prop_type to client;

/*запрос на запросе по принципу левого соединения;*/ 
drop view if exists meatplants_in_cities; 

create view meatplants_in_cities as 
select m.name,(select name from cities where id = m.city_id) as city 
from meatplants m 
order by city,m.name;

grant select on meatplants_in_cities to client;

/*итоговый запрос без условия; */
drop view if exists avg_prod_type_price; 
create view avg_prod_type_price as 
select pt.name, avg(pop.price_per_kg) 
from products_of_plants pop join products p on pop.product_id = p.id 
join product_types pt on pt.id = p.type_id
group by pt.name order by pt.name;

grant select on avg_prod_type_price to manager;

/*итоговый запрос без условия c итоговыми данными вида: «всего», «в том числе»;*/

drop view if exists orders_count_all_and_cur_month; 
create view orders_count_all_and_cur_month as 
select count(*) as all, 
count(case when o.date >= date_trunc('month', CURRENT_DATE) then id end) as month 
from orders o;

grant select on orders_count_all_and_cur_month to manager;

/*итоговые запросы с условием на данные (по значению, по маске, с использованием индекса, без использования индекса);*/ 
drop function avg_volume_by_type;
create or replace function avg_volume_by_type(cname text)
    returns table
            (
                "type"       varchar,
                volume decimal
            )
as
$$
begin
 return query select pt.name, avg(o.volume) from clients c 
 join orders o on o.client_id = c.id join products_of_plants pop 
 on pop.id = o.product_id join products p on p.id = pop.product_id 
 join product_types pt on pt.id = p.type_id where c.name = cname group by pt.name order by pt.name;
end;
$$ language plpgsql security definer;

revoke execute on function avg_volume_by_type(text) from public;
grant execute on function avg_volume_by_type(text) to manager;


drop function avg_order_price_for_clients;
create or replace function avg_order_price_for_clients(pattern text)
    returns table
            (
                name       varchar,
                price decimal
            )
as
$$
begin
 return query select c.name, avg(o.volume*pop.price_per_kg) from clients c 
 join orders o on o.client_id = c.id join products_of_plants pop on pop.id = o.product_id
where c.name like pattern
group by c.name order by c.name;
end;
$$ language plpgsql security definer;

revoke execute on function avg_order_price_for_clients(text) from public;
grant execute on function avg_order_price_for_clients(text) to manager;

/*итоговый запрос с условием на группы; */

drop function clients_max_order_price_greater_than;
create or replace function clients_max_order_price_greater_than(cprice decimal)
    returns table
            (
                name       varchar,
                city varchar,
                price decimal
            )
as
$$
begin
 return query select c.name,ci.name,max(o.volume*pop.price_per_kg) as mp 
 from orders o join clients c on c.id = o.client_id join cities ci on ci.id = c.city_id 
 join products_of_plants pop on pop.id = o.product_id
group by c.name,ci.name having max(o.volume*pop.price_per_kg) >= cprice order by mp;
end;
$$ language plpgsql security definer;

revoke execute on function clients_max_order_price_greater_than(decimal) from public;
grant execute on function clients_max_order_price_greater_than(decimal) to manager;

/*итоговый запрос с условием на данные и на группы;*/

drop function meatplants_volume_greater_than;
create or replace function meatplants_volume_greater_than(ccity text, ctype text, cvol decimal)
    returns table
            (
            	name varchar,
                volume decimal
            )
as
$$
begin
 return query select m.name, sum(pop.volume) as vol from meatplants m 
 join products_of_plants pop on pop.meatplant_id = m.id 
 join cities c on c.id = m.city_id join products p on pop.product_id = p.id
  join product_types pt on pt.id = p.type_id
where c.name = ccity and pt.name = ctype
group by m.name,c.name having sum(pop.volume) >= cvol order by vol;
end;
$$ language plpgsql security definer;

revoke execute on function meatplants_volume_greater_than(text, text, decimal) from public;
grant execute on function meatplants_volume_greater_than(text, text, decimal) to client;

/*запрос на запросе по принципу итогового запроса;*/
drop view if exists clients_orders_count; 
create view clients_orders_count as
select cl.name, 
coalesce((select count(id) from orders where client_id = cl.id),0) as co 
from clients cl 
order by cl.name;

grant select on clients_orders_count to manager;

/*запрос с использованием объединения*/

drop view if exists prod_count_per_type_and_all; 
create view prod_count_per_type_and_all as 
with res as (select pt.name as name, 
	count(*) as co from products_of_plants pop 
	join products p on p.id = pop.product_id 
	join product_types pt on pt.id = p.type_id 
group by name order by name)
select * from res
union all
select 'Всего'::text, sum(co) from res;

grant select on prod_count_per_type_and_all to manager;

/*запросы с подзапросами (с использованием  in, not in, case, операциями над итоговыми данными). */
drop view if exists client_cur_month; 

create view client_cur_month as
select cl.id,cl.name,c.name as city,cl.phone,cl.address 
from clients cl join cities c on c.id = cl.city_id 
where cl.id in (select distinct clients.id from clients 
	join orders o on o.client_id = clients.id 
	where o.date >= date_trunc('month', CURRENT_DATE))
order by cl.name;

grant select on client_cur_month to manager;

drop function products_price_greater_avg;

create or replace function products_price_greater_avg(cid int)
    returns table
            (
                name varchar,
                price pos_decimal,
                meatplant varchar,
                city varchar
            )
as
$$
begin
 return query select pn.name,pop.price_per_kg,m.name,c.name 
 from products_of_plants pop join meatplants m on m.id = pop.meatplant_id 
 join cities c on c.id = m.city_id join products p on p.id = pop.product_id
  join product_names pn on pn.id = p.name_id
where p.type_id = cid and pop.price_per_kg > (select avg(price_per_kg) 
	from products_of_plants join products 
	on products.id = products_of_plants.product_id where products.type_id = cid)
order by pop.price_per_kg,pn.name;
end;
$$ language plpgsql security definer;

revoke execute on function products_price_greater_avg(int) from public;
grant execute on function products_price_greater_avg(int) to client;


drop view if exists cities_without_meatplants; 

create view cities_without_meatplants as 
select c.name from cities c 
where c.id not in (select distinct m.city_id from meatplants m) 
order by c.name;

grant select on cities_without_meatplants to client;

drop view if exists regular_cur_year_clients;

create view regular_cur_year_clients as
select cl.name as name,
 case
		when cl.id in (select o.client_id from orders o 
			join clients on clients.id = o.client_id 
			where o.date >= date_trunc('year',CURRENT_DATE) 
			group by o.client_id 
			having 
count(distinct date_part('year',"date")*100 + date_part('month',"date")) = date_part('month',CURRENT_DATE)) 
		then true
		else false
 end as status  
 from clients cl order by status,name;

grant select on regular_cur_year_clients to manager;

commit;
