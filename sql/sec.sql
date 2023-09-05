begin;
create role admin createrole BYPASSRLS;
create role manager;
create role client;

grant connect on database meatplants to admin;

grant all on all tables in schema public to admin;
GRANT all ON ALL SEQUENCES IN SCHEMA public TO admin;

grant connect on database meatplants to manager;

grant select on meatplants_managers to manager;
grant select, update on meatplants to manager;
grant select(id,name,phone,address,city_id) on clients to manager;
grant all on products_of_plants, orders to manager;
grant select, insert on product_types, product_names, products to manager;
grant select, insert on cities, property_types to manager;

grant usage, select on SEQUENCE cities_sequence, prop_types_sequence, products_of_plants_sequence, 
	orders_sequence, product_types_sequence, product_names_sequence, products_sequence to manager;

grant connect on database meatplants to client;

grant select on meatplants,cities,property_types,
	products_of_plants,products,product_names,product_types,orders,clients to client;

ALTER TABLE meatplants_managers ENABLE ROW LEVEL SECURITY;
drop policy if exists meatplants_managers_policy on meatplants_managers; 
create policy meatplants_managers_policy ON meatplants_managers for select TO manager
	using(user_name=current_user);

ALTER TABLE meatplants ENABLE ROW LEVEL SECURITY;
drop policy if exists meatplants_policy on meatplants; 
create policy meatplants_policy ON meatplants for select, update TO manager
     using (id in (select meatplant_id from meatplants_managers where user_name = current_user))
     with check (id in (select meatplant_id from meatplants_managers where user_name = current_user));

drop policy if exists client_policy1 on meatplants;
create policy client_policy1 on meatplants for select to client using(true);
    
ALTER TABLE products_of_plants ENABLE ROW LEVEL SECURITY;
drop policy if exists products_of_plants_policy on products_of_plants; 
create policy products_of_plants_policy ON products_of_plants TO manager
	using(meatplant_id in (select meatplant_id from meatplants_managers where user_name = current_user))
    with check (meatplant_id in (select meatplant_id from meatplants_managers where user_name = current_user));

drop policy if exists client_policy2 on products_of_plants;
create policy client_policy2 on products_of_plants for select to client using(true);

ALTER TABLE orders ENABLE ROW LEVEL SECURITY; 
drop policy if exists orders_manager_policy on orders; 
create policy orders_manager_policy on orders to manager
	using(product_id in (select id from products_of_plants where meatplant_id in (select meatplant_id from meatplants_managers where user_name = current_user)))
	with check(product_id in (select id from products_of_plants where meatplant_id in (select meatplant_id from meatplants_managers where user_name = current_user)));

drop policy if exists orders_client_policy on orders; 
create policy orders_client_policy on orders for select to client
	using(client_id=(select id from clients where login = current_user));

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

drop policy if exists clients_client_policy on clients; 
create policy clients_client_policy on clients for select to client
	using(current_user=login);

drop policy if exists clients_manager_policy on clients;
create policy clients_manager_policy on clients for select to manager using(true);
    
commit;