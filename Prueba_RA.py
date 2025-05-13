import re
import ipaddress
import json
from datetime import datetime
import shutil
import sys

# Constantes
ARCHIVO = "Dispositivos_Guardados.json"
TIPOS_DISPOSITIVOS = ["switch", "router", "access point", "dispositivo final", "servidor", "cloud"]
CAPAS_RED = ["acceso", "distribución", "núcleo"]
SERVICIOS_DISPONIBLES = ["OSPF", "VLANs", "DHCP", "DNS", "NTP", "SSH", "SNMP", "Syslog"]

# Funciones de utilidad
def validar_ip(ip):
    """Valida si una cadena es una dirección IP válida (IPv4 o IPv6)."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def hacer_backup():
    """Crea un backup del archivo de datos con timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{ARCHIVO}.backup_{timestamp}"
    try:
        shutil.copyfile(ARCHIVO, backup_file)
        print(f"✅ Backup creado: {backup_file}")
        return True
    except Exception as e:
        print(f"⚠️ Error al crear backup: {e}")
        return False

def solicitar_input(mensaje, validacion=None, valor_por_defecto=None):
    """
    Solicita entrada al usuario con validación opcional.
    
    Args:
        mensaje: El mensaje a mostrar al usuario
        validacion: Función de validación (retorna bool)
        valor_por_defecto: Valor a retornar si la entrada está vacía
    
    Returns:
        La entrada validada del usuario
    """
    while True:
        dato = input(mensaje).strip()
        if not dato and valor_por_defecto is not None:
            return valor_por_defecto
        if not dato:
            print("⚠️ No puede estar vacío. Intente de nuevo.")
            continue
        if validacion and not validacion(dato):
            print("⚠️ Dato inválido. Intente de nuevo.")
            continue
        return dato

def seleccionar_servicios():
    """Permite al usuario seleccionar servicios de una lista predefinida."""
    print("\n🛰️ Seleccione los servicios habilitados en este dispositivo (s/n):")
    
    seleccionados = []
    for servicio in SERVICIOS_DISPONIBLES:
        while True:
            respuesta = input(f"¿{servicio}? (s/n): ").strip().lower()
            if respuesta in ['s', 'n', '']:  # Enter cuenta como 'no'
                break
            print("⚠️ Por favor ingrese 's' o 'n'")
        if respuesta == 's':
            seleccionados.append(servicio)
    return seleccionados

# Funciones de manejo de datos
def cargar_dispositivos():
    """Carga los dispositivos desde el archivo JSON."""
    try:
        with open(ARCHIVO, "r", encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ El archivo de datos está corrupto. Se creará uno nuevo.")
                return []
    except FileNotFoundError:
        return []

def guardar_dispositivos(dispositivos):
    """Guarda la lista de dispositivos en el archivo JSON."""
    try:
        with open(ARCHIVO, "w", encoding='utf-8') as f:
            json.dump(dispositivos, f, indent=4, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"⚠️ Error al guardar: {e}")
        return False

def guardar_dispositivo(dispositivo):
    """Agrega un nuevo dispositivo y guarda la lista actualizada."""
    dispositivos = cargar_dispositivos()
    dispositivos.append(dispositivo)
    return guardar_dispositivos(dispositivos)

# Funciones principales
def ingresar_dispositivo():
    """Registra un nuevo dispositivo en el sistema."""
    print("\n➕ Registro de Nuevo Dispositivo")

    nombre = solicitar_input("✏️  Nombre: ")
    tipo = solicitar_input(
        "🔌 Tipo (Switch, Router, Access Point, Dispositivo Final, Servidor, Cloud): ",
        lambda t: t.lower() in TIPOS_DISPOSITIVOS
    ).lower()
    ip = solicitar_input("🌐 Dirección IP: ", validar_ip)
    ubicacion = solicitar_input("📍 Ubicación Física: ")

    vlans = input("\n📶 Ingrese las VLANs configuradas: ").strip()
    servicios = seleccionar_servicios()
    capa = solicitar_input(
        "\n📡 Ingrese la capa de red (Acceso, Distribución, Núcleo): ",
        lambda c: c.lower() in CAPAS_RED
    ).lower()

    dispositivo = {
        "Nombre": nombre,
        "Tipo": tipo,
        "IP": ip,
        "Ubicacion": ubicacion,
        "VLANs": vlans,
        "Servicios de Red": servicios,
        "Capa de Red": capa,
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    if guardar_dispositivo(dispositivo):
        print("✅ Dispositivo guardado exitosamente.\n")
    else:
        print("❌ Error al guardar el dispositivo.\n")

def buscar_dispositivo():
    """Busca dispositivos por diferentes criterios."""
    dispositivos = cargar_dispositivos()
    if not dispositivos:
        print("⚠️ No existen registros guardados.\n")
        return
    
    criterio = input("\n🔎 Buscar dispositivo por Nombre, IP, Tipo o Ubicación: ").strip().lower()
    
    encontrados = [
        d for d in dispositivos 
        if (criterio in d["Nombre"].lower() or 
            criterio in d["IP"].lower() or 
            criterio in d["Tipo"].lower() or 
            criterio in d["Ubicacion"].lower())
    ]
    
    if not encontrados:
        print("❌ No se encontraron coincidencias.\n")
        return
    
    print(f"\n🔍 Se encontraron {len(encontrados)} dispositivos:")
    for i, d in enumerate(encontrados, 1):
        print(f"\n📄 Dispositivo {i}:")
        for clave, valor in d.items():
            print(f"  {clave}: {valor}")

def eliminar_dispositivo():
    """Elimina un dispositivo específico."""
    dispositivos = cargar_dispositivos()
    if not dispositivos:
        print("⚠️ No existen registros guardados.\n")
        return
    
    criterio = input("\n🗑️ Ingrese el Nombre o IP del dispositivo a eliminar: ").strip().lower()
    original_count = len(dispositivos)
    dispositivos = [d for d in dispositivos if criterio not in d["Nombre"].lower() and criterio not in d["IP"]]
    
    if len(dispositivos) == original_count:
        print("❌ No se encontró ningún dispositivo con ese criterio.\n")
        return
    
    if hacer_backup():
        if guardar_dispositivos(dispositivos):
            print(f"✅ Se eliminaron {original_count - len(dispositivos)} dispositivos.\n")
        else:
            print("❌ Error al guardar los cambios.\n")

def editar_dispositivo():
    """Edita un dispositivo existente."""
    dispositivos = cargar_dispositivos()
    if not dispositivos:
        print("⚠️ No existen registros guardados.\n")
        return
    
    criterio = input("\n📝 Ingrese el Nombre o IP del dispositivo a editar: ").strip().lower()
    encontrados = [i for i, d in enumerate(dispositivos) 
                  if criterio in d["Nombre"].lower() or criterio in d["IP"]]
    
    if not encontrados:
        print("❌ No se encontró ningún dispositivo con ese criterio.\n")
        return
    
    if len(encontrados) > 1:
        print("\n⚠️ Se encontraron múltiples dispositivos:")
        for idx in encontrados:
            print(f"  {dispositivos[idx]['Nombre']} - {dispositivos[idx]['IP']}")
        print("Por favor, sea más específico en su búsqueda.")
        return
    
    idx = encontrados[0]
    dispositivo = dispositivos[idx]
    
    print("\n📄 Dispositivo encontrado. Deje en blanco para mantener el valor actual.")
    
    # Edición genérica para campos simples
    campos_editables = {
        "Nombre": None,
        "Tipo": lambda x: x.lower() in TIPOS_DISPOSITIVOS,
        "IP": validar_ip,
        "Ubicacion": None,
        "VLANs": None,
        "Capa de Red": lambda x: x.lower() in CAPAS_RED
    }
    
    for campo, validacion in campos_editables.items():
        while True:
            nuevo_valor = input(f"{campo} ({dispositivo[campo]}): ").strip()
            if not nuevo_valor:
                break
            if validacion and not validacion(nuevo_valor):
                print(f"⚠️ Valor inválido para {campo}")
                continue
            dispositivo[campo] = nuevo_valor if campo != "Tipo" and campo != "Capa de Red" else nuevo_valor.lower()
            break
    
    if input("¿Actualizar servicios de red? (s/n): ").strip().lower() == 's':
        dispositivo["Servicios de Red"] = seleccionar_servicios()
    
    dispositivo["Fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if hacer_backup():
        if guardar_dispositivos(dispositivos):
            print("✅ Dispositivo actualizado.\n")
        else:
            print("❌ Error al guardar los cambios.\n")

def limpiar_registros():
    """Elimina todos los registros de dispositivos."""
    confirmacion = input("\n🧹 ¿Está seguro que desea eliminar TODOS los registros? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("❌ Operación cancelada.\n")
        return
    
    if hacer_backup():
        if guardar_dispositivos([]):
            print("✅ Todos los registros fueron eliminados.\n")
        else:
            print("❌ Error al eliminar los registros.\n")

def generar_reporte():
    """Genera un reporte estadístico detallado de los dispositivos."""
    dispositivos = cargar_dispositivos()
    if not dispositivos:
        print("⚠️ No existen registros guardados.\n")
        return
    
    print("\n" + "="*50)
    print("📊 REPORTE ESTADÍSTICO DETALLADO".center(50))
    print("="*50)
    
    # 1. Resumen general
    print("\n📌 RESUMEN GENERAL")
    print(f"📅 Total de dispositivos registrados: {len(dispositivos)}")
    print(f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 2. Conteo por tipo con detalles
    print("\n🔢 DISTRIBUCIÓN POR TIPO:")
    tipos = {}
    for d in dispositivos:
        tipos[d["Tipo"]] = tipos.get(d["Tipo"], 0) + 1
    
    for tipo, cantidad in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
        print(f"\n  {tipo.upper()} ({cantidad} dispositivos):")
        for d in [d for d in dispositivos if d["Tipo"] == tipo][:3]:  # Muestra 3 ejemplos
            print(f"    - {d['Nombre']} ({d['IP']}) en {d['Ubicacion']}")
        if cantidad > 3:
            print(f"    ...y {cantidad-3} más")
    
    # 3. Conteo por capa con detalles
    print("\n📡 DISTRIBUCIÓN POR CAPA DE RED:")
    capas = {}
    for d in dispositivos:
        capas[d["Capa de Red"]] = capas.get(d["Capa de Red"], 0) + 1
    
    for capa, cantidad in sorted(capas.items(), key=lambda x: x[1], reverse=True):
        print(f"\n  {capa.upper()} ({cantidad} dispositivos):")
        for d in [d for d in dispositivos if d["Capa de Red"] == capa][:3]:
            print(f"    - {d['Nombre']} ({d['Tipo']}) con servicios: {', '.join(d['Servicios de Red'])}")
        if cantidad > 3:
            print(f"    ...y {cantidad-3} más")
    
    # 4. Servicios más comunes con dispositivos que los usan
    print("\n🛠️ SERVICIOS MÁS UTILIZADOS:")
    servicios = {}
    for d in dispositivos:
        for servicio in d["Servicios de Red"]:
            servicios[servicio] = servicios.get(servicio, 0) + 1
    
    for servicio, cantidad in sorted(servicios.items(), key=lambda x: x[1], reverse=True):
        print(f"\n  {servicio} ({cantidad} dispositivos):")
        usuarios = [d for d in dispositivos if servicio in d["Servicios de Red"]]
        for d in usuarios[:3]:
            print(f"    - {d['Nombre']} ({d['IP']})")
        if cantidad > 3:
            print(f"    ...usado por {cantidad-3} dispositivos más")
    
    # 5. Listado completo de dispositivos (resumido)
    print("\n" + "="*50)
    print("📋 LISTADO COMPLETO DE DISPOSITIVOS".center(50))
    print("="*50)
    
    for i, d in enumerate(dispositivos, 1):
        print(f"\n🔹 Dispositivo {i}: {d['Nombre'].upper()}")
        print(f"  🔌 Tipo: {d['Tipo'].capitalize()}")
        print(f"  🌐 IP: {d['IP']}")
        print(f"  📍 Ubicación: {d['Ubicacion']}")
        print(f"  📶 VLANs: {d['VLANs']}")
        print(f"  📡 Capa: {d['Capa de Red'].capitalize()}")
        print(f"  🛠️ Servicios: {', '.join(d['Servicios de Red']) or 'Ninguno'}")
        print(f"  📅 Registrado: {d['Fecha']}")
    
    print("\n" + "="*50)
    print(f"🎉 Reporte generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")

def salir():
    """Cierra la aplicación."""
    print("\n👋 Cerrando el programa. ¡Hasta Luego, Nos Vemos Pronto 😎👍!")
    sys.exit(0)

def mostrar_menu():
    """Muestra el menú principal con emojis y maneja las opciones."""
    opciones = {
        "1": ("📲 Ingresar Nuevo Dispositivo", ingresar_dispositivo),
        "2": ("🔍 Buscar Dispositivo", buscar_dispositivo),
        "3": ("📊 Generar Reporte Estadístico", generar_reporte),
        "4": ("✏️  Editar Dispositivo", editar_dispositivo),
        "5": ("🗑️  Eliminar Dispositivo", eliminar_dispositivo),
        "6": ("🧹 Limpiar Todos Los Registros", limpiar_registros),
        "7": ("🚪 Salir del Sistema", salir)
    }

    while True:
        print("\n" + "="*50)
        print("📋 MENÚ PRINCIPAL".center(50))
        print("="*50)
        
        # Mostrar opciones con emojis y formato mejorado
        for key, (desc, _) in opciones.items():
            print(f"{key} {desc}")
        
        print("="*50)
        eleccion = input("\n👉 Seleccione una opción (1-7): ").strip()
        
        if eleccion in opciones:
            print("\n" + "="*50)  # Separador visual antes de cada acción
            opciones[eleccion][1]()
        else:
            print("\n⚠️ Opción inválida. Por favor ingrese un número del 1 al 7.")
mostrar_menu()
    
