
import pandapower as pp
import pandapower.networks as nw
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import http.client
import pandas as pd





host =""

# conn = http.client.HTTPSConnection("ptc.abujaelectricity.com")

# conn.request("GET", "/getpolse/all")

# res = conn.getresponse()


# data  =  res.read()

# ld =  list(data)



custom_trafo = {
    "sn_mva": 0.5,        # Transformer power rating in MVA
    "vn_hv_kv": 33.0,      # High-voltage side voltage in kV
    "vn_lv_kv": 0.4,       # Low-voltage side voltage in kV
    "vk_percent": 4.0,     # Short-circuit voltage in %
    "vkr_percent": 0.4,    # Copper losses in %
    "pfe_kw": 1.0,         # Iron losses in kW
    "i0_percent": 0.1,     # No-load current in %
    "shift_degree": 0,     # Phase shift in degrees
    "vector_group": "Dyn5" # Winding connection type
}




net  = pp.create_empty_network()

bu1 = pp.create_bus(net, vn_kv=20, name="Bus1", index=40)
node1 = pp.create_bus(net, vn_kv=0.4, name="node1", index=41)
node2 = pp.create_bus(net, vn_kv=0.4, name="node2", index=43)
pp.create_ext_grid(net,bu1,vm_pu=1.02, name="External Grid")
net.bus_geodata = pd.DataFrame(columns=["x", "y"])
pp.create_std_type(net, custom_trafo, name ="custtrans", element ="trafo")
   
for i in range(1, 10):
    dbus=   pp.create_bus(net, vn_kv=33, name="Bus{}".format(i), index=i)

    pp.create_transformer(net, bu1, dbus, std_type="custtrans")
    pp.create_load(net, dbus, p_mw=1.0,  q_mvar=0.5, name="Load{}".format(i))
   
    net.bus_geodata.loc[dbus] = [i, i] 

   



bu2 = pp.create_bus(net, vn_kv =0.4, name="Bus 2", index=42)

pp.create_transformer(net, bu1, bu2, std_type="custtrans")



net.bus_geodata.loc[bu1] = [0, 0]  
net.bus_geodata.loc[bu2] = [11, 11]  
net.bus_geodata.loc[node1] = [12, 12]  
net.bus_geodata.loc[node2] = [13, 13]  

pp.create_load(net, bu2, p_mw=1.0,  q_mvar=0.5, name="Load")

pp.create_gen(net, bu2, p_mw=0.5, vm_pu=1.0, name="Generator")


pp.runpp(net)


pp.to_excel(net, "test.xlsx")



print(net.res_bus)

print(net.res_trafo)
print(net.bus_geodata)


print(net.res_line)

plot.simple_plot(net)
plt.show()

