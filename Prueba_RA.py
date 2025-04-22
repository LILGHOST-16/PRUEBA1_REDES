import re
import ipaddress
from datetime import datetime

ARCHIVO = "Dispositivos_Guardados.txt"

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
            print("⚠️ No puede estar vacío. Intente de nuevo.")
            continue
        if validacion and not validacion(dato):
            print("⚠️ Dato inválido. Intente de nuevo.")
            continue
        return dato

def seleccionar_servicios():
    servicios = [
        "OSPF",
        "VLANs",
        "DHCP",
        "DNS",
        "NTP",
        "SSH",
        "SNMP",
        "Syslog"
    ]
    print("\n🛰️ Seleccione los servicios habilitados en este dispositivo:")
    seleccionados = []
    for servicio in servicios:
        respuesta = input(f"¿{servicio}? (s/n): ").strip().lower()
        if respuesta == "s":
            seleccionados.append(servicio)
    return seleccionados

def ingresar_dispositivo():
    print("\n➕ Registro de Nuevo Dispositivo")

    nombre = solicitar_input("🖋️ Nombre: ")
    tipo = solicitar_input("🔌 Tipo (Switch, Router, Access Point, Impresora, Servidor, Cloud): ", 
                            lambda t: t.lower() in ["switch", "router", "access point", "servidor", "cloud"])
    ip = solicitar_input("🌐 Dirección IP: ", validar_ip)
    ubicacion = solicitar_input("📍 Ubicación Física: ")

    # VLANs
    vlans = input("\n📶 Ingrese las VLANs configuradas: ").strip()

    # Servicios de red
    servicios = seleccionar_servicios()

    # Capa de red
    capa = solicitar_input("\n📡 Ingrese la capa de red (Acceso, Distribución, Núcleo): ", 
                            lambda c: c.lower() in ["acceso", "distribución", "núcleo"])

    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dispositivo = {
        "Nombre": nombre,
        "Tipo": tipo,
        "IP": ip,
        "Ubicación": ubicacion,
        "VLANs": vlans,
        "Servicios de Red": ", ".join(servicios),
        "Capa de Red": capa,
        "Fecha": fecha_registro
    }

    guardar_dispositivo(dispositivo)
    print("✅ Dispositivo guardado exitosamente.\n")

def guardar_dispositivo(dispositivo):
    with open(ARCHIVO, "a") as f:
        for clave, valor in dispositivo.items():
            f.write(f"{clave}: {valor}\n")
        f.write("-" * 60 + "\n")

def buscar_dispositivo():
    if not verificar_existencia_archivo():
        return
    criterio = input("\n🔎 Buscar dispositivo por Nombre o IP: ").strip().lower()
    encontrado = False
    bloque = ""

    with open(ARCHIVO, "r") as f:
        for linea in f:
            bloque += linea
            if linea.strip() == "-" * 60:
                if criterio in bloque.lower():
                    print("\n📄 Dispositivo encontrado:\n" + bloque)
                    encontrado = True
                bloque = ""
    if not encontrado:
        print("❌ No se encontraron coincidencias.\n")

def limpiar_registros():
    confirmacion = input("\n🗑️ ¿Eliminar todos los registros? (s/n): ").strip().lower()
    if confirmacion == "s":
        open(ARCHIVO, "w").close()
        print("✅ Todos los registros fueron eliminados.\n")
    else:
        print("❌ Cancelado.\n")

def verificar_existencia_archivo():
    try:
        with open(ARCHIVO, "r") as f:
            if not f.read().strip():
                print("⚠️ No existen registros guardados.\n")
                return False
            return True
    except FileNotFoundError:
        print("⚠️ Archivo de registros no encontrado.\n")
        return False

def mostrar_menu():
    opciones = {
        "1": ingresar_dispositivo,
        "2": buscar_dispositivo,
        "3": limpiar_registros,
        "4": salir
    }
    while True:
        print("\n📋 MENÚ PRINCIPAL")
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
