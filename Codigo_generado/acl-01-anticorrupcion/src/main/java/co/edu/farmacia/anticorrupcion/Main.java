package co.edu.farmacia.anticorrupcion;

import co.edu.farmacia.anticorrupcion.infraestructura.adaptadores.AdaptadorContextoHttp;
import co.edu.farmacia.anticorrupcion.infraestructura.adaptadores.AdaptadorSistemaExternoHttp;
import co.edu.farmacia.anticorrupcion.infraestructura.api.ServidorHttp;
import co.edu.farmacia.anticorrupcion.aplicacion.ServicioIntegracion;

import java.util.logging.Logger;

/**
 * ACL-01 Adaptador anticorrupción e interoperabilidad — raíz de composición. Arquitectura hexagonal:
 * dominio (DTO + traductores) · aplicación (ServicioIntegracion) · infraestructura (HTTP).
 * <br>INT-01 Programación quirúrgica: Programación Quirúrgica → Planificación de Demanda
 * <br>INT-02 Historia clínica electrónica: Historia Clínica (HCE) → Inventario
 * <br>INT-03 Servicio de urgencias: Servicio de Urgencias → Inventario
 * <br>INT-04 ERP de compras y contabilidad: Sistema ERP (Compras) ← Abastecimiento
 * <br>INT-05 Proveedor de medicamentos: Proveedores Externos → Inventario
 * <br>INT-06 Entidad de vigilancia farmacéutica: INVIMA (Vigilancia) → Vencimientos
 */
public class Main {
    public static void main(String[] args) throws Exception {
        ServicioIntegracion servicio = new ServicioIntegracion(new AdaptadorContextoHttp(), new AdaptadorSistemaExternoHttp());
        int puerto = Integer.parseInt(System.getenv().getOrDefault("PUERTO", "8010"));
        new ServidorHttp(servicio).iniciar(puerto);
        Logger.getLogger("main").info("ACL-01 escuchando en el puerto " + puerto);
    }
}
