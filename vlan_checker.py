vlan = int(input("Ingrese número de VLAN: "))
if 1 <= vlan <= 1005:
    print("VLAN del rango normal.")
elif 1006 <= vlan <= 4094:
    print("VLAN del rango extendido.")
else:
    print("Número de VLAN inválido.")
