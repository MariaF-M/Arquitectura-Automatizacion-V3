package co.edu.farmacia.anticorrupcion.aplicacion;

import co.edu.farmacia.anticorrupcion.dominio.puertos.PuertoContextoInterno;
import co.edu.farmacia.anticorrupcion.dominio.puertos.PuertoSistemaExterno;
import co.edu.farmacia.anticorrupcion.dominio.traductores.Traductor;
import co.edu.farmacia.anticorrupcion.dominio.traductores.TraductorInt01ProgramacionQuirurgica;
import co.edu.farmacia.anticorrupcion.dominio.traductores.TraductorInt02HistoriaClinicaElectronica;
import co.edu.farmacia.anticorrupcion.dominio.traductores.TraductorInt03ServicioDeUrgencias;
import co.edu.farmacia.anticorrupcion.dominio.traductores.TraductorInt04ErpDeComprasYContabilidad;
import co.edu.farmacia.anticorrupcion.dominio.traductores.TraductorInt05ProveedorDeMedicamentos;
import co.edu.farmacia.anticorrupcion.dominio.traductores.TraductorInt06EntidadDeVigilanciaFarmaceutica;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Caso de uso de la ACL «ACL-01 Adaptador anticorrupción e interoperabilidad»: recibir un mensaje, traducirlo y entregarlo al otro lado.
 * Ningún contexto interno conoce el formato de un sistema externo, ni al revés.
 */
public class ServicioIntegracion {
    private final Map<String, Traductor> traductores = new LinkedHashMap<>();
    private final Map<String, String[]> destinos = new LinkedHashMap<>();
    private final PuertoContextoInterno contextos;
    private final PuertoSistemaExterno externos;

    public ServicioIntegracion(PuertoContextoInterno contextos, PuertoSistemaExterno externos) {
        this.contextos = contextos;
        this.externos = externos;
        traductores.put("int-01", new TraductorInt01ProgramacionQuirurgica());
        destinos.put("int-01", new String[] {
                System.getenv().getOrDefault(TraductorInt01ProgramacionQuirurgica.VARIABLE_URL, TraductorInt01ProgramacionQuirurgica.URL_DEFECTO),
                TraductorInt01ProgramacionQuirurgica.RUTA_COMANDO});
        traductores.put("int-02", new TraductorInt02HistoriaClinicaElectronica());
        destinos.put("int-02", new String[] {
                System.getenv().getOrDefault(TraductorInt02HistoriaClinicaElectronica.VARIABLE_URL, TraductorInt02HistoriaClinicaElectronica.URL_DEFECTO),
                TraductorInt02HistoriaClinicaElectronica.RUTA_COMANDO});
        traductores.put("int-03", new TraductorInt03ServicioDeUrgencias());
        destinos.put("int-03", new String[] {
                System.getenv().getOrDefault(TraductorInt03ServicioDeUrgencias.VARIABLE_URL, TraductorInt03ServicioDeUrgencias.URL_DEFECTO),
                TraductorInt03ServicioDeUrgencias.RUTA_COMANDO});
        traductores.put("int-04", new TraductorInt04ErpDeComprasYContabilidad());
        traductores.put("int-05", new TraductorInt05ProveedorDeMedicamentos());
        destinos.put("int-05", new String[] {
                System.getenv().getOrDefault(TraductorInt05ProveedorDeMedicamentos.VARIABLE_URL, TraductorInt05ProveedorDeMedicamentos.URL_DEFECTO),
                TraductorInt05ProveedorDeMedicamentos.RUTA_COMANDO});
        traductores.put("int-06", new TraductorInt06EntidadDeVigilanciaFarmaceutica());
        destinos.put("int-06", new String[] {
                System.getenv().getOrDefault(TraductorInt06EntidadDeVigilanciaFarmaceutica.VARIABLE_URL, TraductorInt06EntidadDeVigilanciaFarmaceutica.URL_DEFECTO),
                TraductorInt06EntidadDeVigilanciaFarmaceutica.RUTA_COMANDO});
    }

    private Traductor traductor(String codigo, String direccion) {
        Traductor t = traductores.get(codigo);
        if (t == null || !t.direccion().equals(direccion))
            throw new IllegalArgumentException("No existe la integración " + direccion + " " + codigo);
        return t;
    }

    /** Externo -> contexto interno. */
    public Object recibirEntrante(String codigo, Map<String, Object> mensajeExterno) {
        Traductor t = traductor(codigo, "entrada");
        Map<String, Object> interno = t.traducir(mensajeExterno);
        String[] destino = destinos.get(codigo);
        String ruta = destino[1];
        if (ruta.contains("{id}")) {
            Object id = interno.remove("id");
            if (id == null) throw new IllegalArgumentException(t.codigo() + ": el mapeo no produce el campo 'id' que necesita el comando");
            ruta = ruta.replace("{id}", String.valueOf(id));
        }
        return contextos.ejecutarComando(destino[0], ruta, interno);
    }

    /** Contexto interno -> externo. */
    public Object recibirSaliente(String codigo, Map<String, Object> mensajeInterno) {
        Traductor t = traductor(codigo, "salida");
        return externos.enviar(t.codigo(), t.externo(), t.traducir(mensajeInterno));
    }

    public List<Map<String, Object>> catalogo() {
        return traductores.values().stream().map(t -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("codigo", t.codigo());
            m.put("nombre", t.nombre());
            m.put("direccion", t.direccion());
            m.put("contexto", t.contexto());
            m.put("externo", t.externo());
            m.put("mapeo", t.mapeo());
            return m;
        }).toList();
    }
}
