from PyP100 import PyP110

p110 = PyP110.P110("192.168.x.x", "email@gmail.com", "password") 

p110.handshake() #Creates the cookies required for further methods
p110.login() #Sends credentials to the plug and creates AES Key and IV for further methods

#The P110 has all the same basic functions as the plugs and additionally allow for energy monitoring.
print(p110.getEnergyUsage()) #Returns dict with all of the energy usage of the connected plu
# {'today_runtime': 27, 'month_runtime': 27, 'today_energy': 2, 'month_energy': 2, 'local_time': '2024-05-15 12:28:35', 'electricity_charge': [0, 0, 0], 'current_power': 1601933}