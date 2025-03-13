import pandapower as pp
import pandapower.networks as nw
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import http.client
import pandas as pd
import json







host ="ptc.abujaelectricity.com/"

conn = http.client.HTTPSConnection("ptc.abujaelectricity.com")

conn.request("GET", "/getbus/all")

res = conn.getresponse()


data  =  res.read()

bus=  data



conn = http.client.HTTPSConnection("ptc.abujaelectricity.com")

conn.request("GET", "/getlines/all")

resline = conn.getresponse()


dataline  =  resline.read()




conn = http.client.HTTPSConnection("ptc.abujaelectricity.com")

conn.request("GET", "/gettransformers/all")

restrans = conn.getresponse()


datatran  =  restrans.read()


conn = http.client.HTTPSConnection("ptc.abujaelectricity.com")

conn.request("GET", "/listfeeder")

restrans = conn.getresponse()


listfeeder  =  restrans.read()







net = pp.create_empty_network()

main_bus = pp.create_bus(net, vn_kv =33,name ="Feeder L36")


pp.create_ext_grid(net, bus=main_bus, vm_pu=1.02)

pp.create_gen(net, bus=main_bus, p_mw=13.0, vm_pu=1.02, sn_mva=500, min_q_mvar=0.1, max_q_mvar =13, min_q_var=0.21, max_q_var =14, name="Generator-Feeder L36")


tee_off_bus =[]









tee_off_bus =[]
# Step 1: Decode to string
json_str = bus.decode("utf-8")
# Step 2: Convert JSON string to Python list
bus_list = json.loads(json_str)



jline = dataline.decode("utf-8")

linelist = json.loads(jline)




jtrans = datatran.decode("utf-8")
tranlist = json.loads(jtrans)


listfeeders = listfeeder.decode("utf-8")
feederlist = json.loads(listfeeders)


feeders = feederlist['data']


df = pd.DataFrame(feeders)

df_unique = df.drop_duplicates(subset=["feeders"])
fdata =df_unique.to_dict(orient="records")





i =0




for da in fdata:

    for line in linelist:   
        
        if da['feeders'].strip() == line['feeder'].strip():
         i =i+1
     
        


         pp.create_std_type(net, {
         "q_mm2": line['c_size'],
         "voltage_rating": 'HV',
         "r_ohm_per_km": line['r_ohm_per_km'],
         "x_ohm_per_km": line['x_ohm_per_km'],
         "c_nf_per_km": line['c_nf_per_km'],
         "max_i_ka": line['max_i_ka']
          
         
         }, name=f"{line['feeder']}-{line['tee_off']}-{i}", element="line")
    
         from_bus =main_bus

         if i >1:
             f_bus = next((bus for bus in bus_list if bus['busname'] == line['from_bus']), None)
             from_bus = pp.create_bus(net, vn_kv =f_bus['vn_kv'], name= f_bus['busname'])
    
         t_bus = next((bus for bus in bus_list if bus['busname'] == line['to_bus']), None)
         to_bus = pp.create_bus(net, vn_kv =t_bus['vn_kv'], name= t_bus['busname'])

         pp.create_line(net, from_bus =from_bus, to_bus =to_bus, length_km=line['length_km'], std_type=f"{line['feeder']}-{line['tee_off']}-{i}", name =f"{line['feeder']}-{i}-{line['tee_off']}")
     

         dh = next((bus for bus in tranlist if bus['hv_bus'] == line['to_bus']), None)
     
     
         # custom_trafo = {
         # "sn_mva": dh['sn_mva'],        # Transformer power rating in MVA
         # "vn_hv_kv": dh['vn_hv_kv'],      # High-voltage side voltage in kV
         # "vn_lv_kv": dh['vn_lv_kv'],       # Low-voltage side voltage in kV
         # "vk_percent": dh['vk_percent'],     # Short-circuit voltage in %
         # "vkr_percent": dh['vkr_percent'],    # Copper losses in %
         # "pfe_kw": dh['pfe_kw'],         # Iron losses in kW
         # "i0_percent": dh['i0_percent'],     # No-load current in %
         # "shift_degree": dh['shift_degree'],     # Phase shift in degrees
         # "vector_group": dh['vector_group'] # Winding connection type
         # }

         custom_trafo = {
         "sn_mva": dh['sn_mva'],        # Transformer power rating in MVA
         "vn_hv_kv": dh['vn_hv_kv'],      # High-voltage side voltage in kV
         "vn_lv_kv": dh['vn_lv_kv'],       # Low-voltage side voltage in kV
         "vk_percent": 12,     # Short-circuit voltage in %
         "vkr_percent": 0.2,    # Copper losses in %
         "pfe_kw": 0.1,         # Iron losses in kW
         "i0_percent": 0.5,     # No-load current in %
         "shift_degree": 0,     # Phase shift in degrees
         "vector_group": dh['vector_group'] # Winding connection type
         }

         #hv_bus = pp.create_bus(net, vn_kv =dh['vn_hv_kv'], name= dh['hv_bus'])
         pp.create_std_type(net, custom_trafo, name =dh['lv_bus'], element ="trafo")
         lv_busi = pp.create_bus(net, vn_kv=dh['vn_lv_kv'], name =f"{dh['lv_bus']}-Load Bus")
         pp.create_transformer(net, hv_bus=to_bus, lv_bus =lv_busi, std_type=dh['lv_bus'], name =f"Transformer-{dh['lv_bus']}")

         load_mw =dh['loadmw']

         pp.create_load(net, bus=lv_busi, p_mw=load_mw, q_mvar=0.02, name =f"Load-{dh['lv_bus']}")








pp.runpp(net)


pp.to_excel(net, "Feeder L36.xlsx")

print(net.res_bus)
# print(net.res_line)


