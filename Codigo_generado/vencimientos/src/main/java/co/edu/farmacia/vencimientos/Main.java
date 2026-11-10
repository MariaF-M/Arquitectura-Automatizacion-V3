package co.edu.farmacia.vencimientos;

import co.edu.farmacia.vencimientos.api.ServidorHttp;
import co.edu.farmacia.vencimientos.infraestructura.clientes.ClienteHttp;
import co.edu.farmacia.vencimientos.infraestructura.clientes.ClienteSeguridadYAuditoriaHttp;
import co.edu.farmacia.vencimientos.infraestructura.clientes.ClienteInventarioHttp;
import co.edu.farmacia.vencimientos.infraestructura.clientes.ClienteAnticorrupcionHttp;
import co.edu.farmacia.vencimientos.aplicacion.memento.Caretaker;
import co.edu.farmacia.vencimientos.aplicacion.comandos.ManejadorAlertaVencimiento;
import co.edu.farmacia.vencimientos.infraestructura.persistencia.RepositorioAlertaVencimientoBaseDatos;
import co.edu.farmacia.vencimientos.infraestructura.persistencia.RepositorioAlertaVencimientoCache;
import co.edu.farmacia.vencimientos.infraestructura.persistencia.RepositorioAlertaVencimientoMemoria;
import co.edu.farmacia.vencimientos.aplicacion.servicios.GestionDeAlertasDeVencimientoServicio;
import co.edu.farmacia.vencimientos.aplicacion.eventos.BusEventos;
import co.edu.farmacia.vencimientos.infraestructura.transversal.Cifrador;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

/**
 * Punto de entrada de Vencimientos — raíz de composición.
 * Contexto: D-02 Gestión de vencimientos y priorización (CORE) · Arquitectura: microservicios · Puerto: 8002
 * <br>Consume a Seguridad y Auditoría: «Open Host Service»
 * <br>Consume a Inventario: «Shared Kernel (núcleo compartido: Lote)»
 * <br>INT-06 Entidad de vigilancia farmacéutica (entrada) vía ACL-01
 * Generado automáticamente desde el modelo ArchiMate.
 */
public class Main {
    private static String env(String clave, String defecto) { return System.getenv().getOrDefault(clave, defecto); }

    public static void main(String[] args) throws Exception {
        BusEventos bus = new BusEventos();
        Cifrador cifrador = new Cifrador();
        boolean usarBd = env("PERSISTENCIA", "memoria").equals("bd");
        Map<String, Object> manejadores = new LinkedHashMap<>();
        Map<String, Object> caches = new LinkedHashMap<>();

        RepositorioAlertaVencimientoCache repoAlertaVencimiento = new RepositorioAlertaVencimientoCache(
                usarBd ? new RepositorioAlertaVencimientoBaseDatos(cifrador) : new RepositorioAlertaVencimientoMemoria(cifrador));
        caches.put("alerta-vencimiento", repoAlertaVencimiento);
        manejadores.put("alerta-vencimiento", new ManejadorAlertaVencimiento(repoAlertaVencimiento, bus, new Caretaker<>()));
        Map<String, Object> clientes = new LinkedHashMap<>();
        // open-host-service: «Open Host Service»
        clientes.put("Seguridad y Auditoría", new ClienteSeguridadYAuditoriaHttp(new ClienteHttp(env("SEGURIDAD_Y_AUDITORIA_URL", "http://localhost:8005"))));
        // shared-kernel: «Shared Kernel (núcleo compartido: Lote)»
        clientes.put("Inventario", new ClienteInventarioHttp(new ClienteHttp(env("INVENTARIO_URL", "http://localhost:8001"))));
        ClienteAnticorrupcionHttp acl = new ClienteAnticorrupcionHttp(new ClienteHttp(env("ACL_URL", "http://localhost:8010")));
        clientes.put("ACL-01", acl);

        Map<String, Object> arquitectura = new LinkedHashMap<>();
        arquitectura.put("contexto", "Vencimientos");
        arquitectura.put("dominio", "D-02 Gestión de vencimientos y priorización");
        arquitectura.put("clasificacion", "CORE");
        arquitectura.put("arquitectura", "microservicios");
        arquitectura.put("componentes", List.of(GestionDeAlertasDeVencimientoServicio.NOMBRE));
        arquitectura.put("funciones", List.of("prioridad-de-uso-de-lotes-fefo", "validacion-de-restricciones-de-uso", "notificacion-de-lotes-criticos"));
        arquitectura.put("clientes", List.copyOf(clientes.keySet()));

        int puerto = Integer.parseInt(env("PUERTO", "8002"));
        new ServidorHttp(bus, manejadores, () -> {
            Map<String, Object> r = new LinkedHashMap<>(arquitectura);
            Map<String, Object> cache = new LinkedHashMap<>();
            cache.put("alerta-vencimiento", repoAlertaVencimiento.estadisticas());
            r.put("cache", cache);
            return r;
        }).iniciar(puerto);
        Logger.getLogger("main").info("Vencimientos escuchando en el puerto " + puerto);
    }
}
