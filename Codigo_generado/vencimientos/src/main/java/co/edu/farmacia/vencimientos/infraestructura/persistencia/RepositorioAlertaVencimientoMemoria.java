package co.edu.farmacia.vencimientos.infraestructura.persistencia;

import co.edu.farmacia.vencimientos.dominio.modelo.AlertaVencimiento;
import co.edu.farmacia.vencimientos.dominio.puertos.RepositorioAlertaVencimiento;
import co.edu.farmacia.vencimientos.infraestructura.transversal.Cifrador;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** Persistencia en memoria (por defecto). Cifra en reposo: ["motivo"]. */
public class RepositorioAlertaVencimientoMemoria implements RepositorioAlertaVencimiento {
    private static final List<String> CAMPOS_CIFRADOS = List.of("motivo");
    private final Map<String, Map<String, Object>> datos = new ConcurrentHashMap<>();
    private final Cifrador cifrador;

    public RepositorioAlertaVencimientoMemoria(Cifrador cifrador) { this.cifrador = cifrador; }

    @Override
    public void guardar(AlertaVencimiento agregado) {
        datos.put(agregado.getId(), cifrador.cifrarCampos(agregado.aMapa(), CAMPOS_CIFRADOS));
    }

    @Override
    public AlertaVencimiento obtener(String id) {
        Map<String, Object> fila = datos.get(id);
        return fila == null ? null : AlertaVencimiento.desdeMapa(cifrador.descifrarCampos(fila, CAMPOS_CIFRADOS));
    }

    @Override
    public List<AlertaVencimiento> listar() { return datos.keySet().stream().map(this::obtener).toList(); }
}
