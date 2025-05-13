import re
import ipaddress
import json
from datetime import datetime

ARCHIVO = "Dispositivos_Guardados.json"

def validar_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def solicitar_input(mensaje, validacion=None):
    while True:
        dato = input(mensaje).strip()
        if not dato:
            print("\u26a0\ufe0f No puede estar vac\u00edo. Intente de nuevo.")
            continue
        if validacion and not validacion(dato):
            print("\u26a0\ufe0f Dato inv\u00e1lido. Intente de nuevo.")
            continue
        return dato

def seleccionar_servicios():
    servicios = ["OSPF", "VLANs", "DHCP", "DNS", "NTP", "SSH", "SNMP", "Syslog"]
    print("\n\U0001f6f0\ufe0f Seleccione los servicios habilitados en este dispositivo:")
    seleccionados = []
    for servicio in servicios:
        respuesta = input(f"\u00bf{servicio}? (s/n): ").strip().lower()
        if respuesta == "s":
            seleccionados.append(servicio)
    return seleccionados

def cargar_dispositivos():
    try:
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def guardar_dispositivos(dispositivos):
    with open(ARCHIVO, "w") as f:
        json.dump(dispositivos, f, indent=4)

def guardar_dispositivo(dispositivo):
    dispositivos = cargar_dispositivos()
    dispositivos.append(dispositivo)
    guardar_dispositivos(dispositivos)

def ingresar_dispositivo():
    print("\n➕ Registro de Nuevo Dispositivo")

    nombre = solicitar_input("✏️  Nombre: ")
    tipo = solicitar_input("🔌 Tipo (Switch, Router, Access Point, Dispositivo Final, Servidor, Cloud): ",
                            lambda t: t.lower() in ["switch", "router", "access point", "dispositivo final", "servidor", "cloud"])
    ip = solicitar_input("🌐 Direcci\u00f3n IP: ", validar_ip)
    ubicacion = solicitar_input("📍 Ubicaci\u00f3n F\u00edsica: ")

    vlans = input("\n📶 Ingrese las VLANs configuradas: ").strip()
    servicios = seleccionar_servicios()
    capa = solicitar_input("\n📡 Ingrese la capa de red (Acceso, Distribuci\u00f3n, N\u00facleo): ",
                            lambda c: c.lower() in ["acceso", "distribuci\u00f3n", "n\u00facleo"])

    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dispositivo = {
        "Nombre": nombre,
        "Tipo": tipo,
        "IP": ip,
        "Ubicacion": ubicacion,
        "VLANs": vlans,
        "Servicios de Red": servicios,
        "Capa de Red": capa,
        "Fecha": fecha_registro
    }

    guardar_dispositivo(dispositivo)
    print("✅ Dispositivo guardado exitosamente.\n")

def buscar_dispositivo():
    dispositivos = cargar_dispositivos()
    if not dispositivos:
        print("⚠️ No existen registros guardados.\n")
        return
    criterio = input("\n🔎 Buscar dispositivo por Nombre o IP: ").strip().lower()
    encontrados = [d for d in dispositivos if criterio in d["Nombre"].lower() or criterio in d["IP"]]
    if encontrados:
        for d in encontrados:
            print("\n📄 Dispositivo encontrado:")
            for clave, valor in d.items():
                print(f"{clave}: {valor}")
    else:
        print("❌ No se encontraron coincidencias.\n")

def limpiar_registros():
    confirmacion = input("\n🗑️ \u00bfEliminar todos los registros? (s/n): ").strip().lower()
    if confirmacion == "s":
        guardar_dispositivos([])
        print("✅ Todos los registros fueron eliminados.\n")
    else:
        print("❌ Cancelado.\n")

def mostrar_menu():
    opciones = {
        "1": ingresar_dispositivo,
        "2": buscar_dispositivo,
        "3": limpiar_registros,
        "4": salir
    }
    while True:
        print("\n📋 MEN\u00da PRINCIPAL")
        print("1️⃣  📲 Ingresar Nuevo Dispositivo")
        print("2️⃣  🔍 Buscar Dispositivo")
        print("3️⃣  🧹 Limpiar Todos Los Registros")
        print("4️⃣  🚪 Salir")

        eleccion = input("Seleccione Una Opción (1-4): ").strip()
        accion = opciones.get(eleccion)
        if accion:
            accion()
        else:
            print("⚠️ Opción inválida. Intente de nuevo.\n")

def salir():
    print("\n👋 Cerrando el programa. ¡Hasta Luego, Nos Vemos Pronto 😎👍!")
    exit()

if __name__ == "__main__":
    mostrar_menu()
