import xml.etree.ElementTree as ET
import os
import shutil

def generar_proyecto():
    ruta_xml = '../Modelo_archimate/Modelo_Farmacia_mejorado.archimate'
    ruta_salida = '../Codigo_generado'
    
    # Borrar la carpeta vieja para no mezclar si se ejecuta varias veces
    if os.path.exists(ruta_salida):
        shutil.rmtree(ruta_salida)
        
    tree = ET.parse(ruta_xml)
    root = tree.getroot()
    xsi_type = '{http://www.w3.org/2001/XMLSchema-instance}type'
    
    componentes = set()
    for elemento in root.iter('element'):
        if elemento.attrib.get(xsi_type) == 'archimate:ApplicationComponent':
            componentes.add(elemento.attrib.get('name').strip())
            
    # Lista excluidos
    ignorar = [
        'INVIMA (Vigilancia)', 'Sistema ERP (Compras)', 'Servicio de Urgencias', 
        'Proveedores Externos', 'Historia Clínica (HCE)', 
        'Contexto delimitado: lenguaje ubicuo y decisiones',
        'Aplicación de gestión de medicamentos (solución)',
        'Programación Quirúrgica', 
        'V11 — Gestión de Vencimientos y Priorización',
        'Seguridad y Auditoría',
        'Abastecimiento y requerimientos de compra',
        'Gestión de medicamentos' # Agrupador general
    ]
    
    # Reglas de negocio
    config_dominios = {
        'Inventario': {'lang': 'Python', 'arch': 'Hexagonal'},
        'Vencimientos': {'lang': 'Java', 'arch': 'Microservicios'},
        'Abastecimiento': {'lang': 'C#', 'arch': 'Hexagonal'},
        'Planificación_de_Demanda': {'lang': 'Python', 'arch': 'Microservicios'},
        'ACL-01_Adaptador_anticorrupción_e_interoperabilidad': {'lang': 'Java', 'arch': 'Hexagonal'}
    }
    
    print("Generando proyecto final automatizado...\n")
    
    for comp in componentes:
        if comp not in ignorar:
            # Limpiar nombre
            nombre = comp.replace(' ', '_').replace(':', '').replace('—', '').replace(',', '').strip()
            ruta_carpeta = os.path.join(ruta_salida, nombre)
            os.makedirs(ruta_carpeta, exist_ok=True)
            
            # Obtener configuración (si no está, por defecto es Python/Microservicios)
            conf = config_dominios.get(nombre, {'lang': 'Python', 'arch': 'Microservicios'})
            
            # Crear carpetas internas según la arquitectura elegida
            if conf['arch'] == 'Hexagonal':
                subcarpetas = ['domain', 'application', 'infrastructure']
            else:
                subcarpetas = ['controllers', 'services', 'repositories']
                
            for sub in subcarpetas:
                os.makedirs(os.path.join(ruta_carpeta, sub), exist_ok=True)
                
            # Crear archivo de código fuente según el lenguaje
            if conf['lang'] == 'Python':
                with open(os.path.join(ruta_carpeta, 'main.py'), 'w', encoding='utf-8') as f:
                    f.write(f"# Microservicio: {comp}\n# Arquitectura: {conf['arch']}\n")
            elif conf['lang'] == 'Java':
                with open(os.path.join(ruta_carpeta, 'Main.java'), 'w', encoding='utf-8') as f:
                    f.write(f"// Microservicio: {comp}\n// Arquitectura: {conf['arch']}\npublic class Main {{}}\n")
            elif conf['lang'] == 'C#':
                with open(os.path.join(ruta_carpeta, 'Program.cs'), 'w', encoding='utf-8') as f:
                    f.write(f"// Microservicio: {comp}\n// Arquitectura: {conf['arch']}\nclass Program {{}}\n")
                    
            print(f" [OK] {nombre} -> {conf['lang']} ({conf['arch']})")

if __name__ == "__main__":
    generar_proyecto()