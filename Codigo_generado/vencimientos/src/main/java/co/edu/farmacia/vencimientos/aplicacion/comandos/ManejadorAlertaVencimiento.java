package co.edu.farmacia.vencimientos.aplicacion.comandos;

import co.edu.farmacia.vencimientos.aplicacion.memento.Caretaker;
import co.edu.farmacia.vencimientos.dominio.modelo.AlertaVencimiento;
import co.edu.farmacia.vencimientos.dominio.modelo.AlertaVencimientoMemento;
import co.edu.farmacia.vencimientos.dominio.modelo.NoEncontradoException;
import co.edu.farmacia.vencimientos.dominio.modelo.ReglaNegocioException;
import co.edu.farmacia.vencimientos.dominio.puertos.RepositorioAlertaVencimiento;
import co.edu.farmacia.vencimientos.aplicacion.eventos.BusEventos;

import java.util.List;
import java.util.Map;

/**
 * Manejador de comandos de AlertaVencimiento: toma memento, ejecuta, valida invariantes;
 * si falla restaura el memento, si no guarda y publica eventos.
 */
public class ManejadorAlertaVencimiento {
    private final RepositorioAlertaVencimiento repo;
    private final BusEventos bus;
    private final Caretaker<AlertaVencimientoMemento> caretaker;

    public ManejadorAlertaVencimiento(RepositorioAlertaVencimiento repo, BusEventos bus, Caretaker<AlertaVencimientoMemento> caretaker) {
        this.repo = repo;
        this.bus = bus;
        this.caretaker = caretaker;
    }

    private AlertaVencimiento cargar(String id) {
        AlertaVencimiento a = repo.obtener(id);
        if (a == null) throw new NoEncontradoException("AlertaVencimiento " + id + " no existe");
        return a;
    }

    /** Atributos que no se pueden repetir (spec.yaml -> unicos). */
    private void verificarUnicos(AlertaVencimiento nuevo) {
    }

    private Map<String, Object> confirmar(AlertaVencimiento a) {
        repo.guardar(a);
        a.extraerEventos().forEach(bus::publicar);
        return a.aMapa();
    }

    public Map<String, Object> manejar(EvaluarPrioridadFefo comando) {
        AlertaVencimiento nuevo = AlertaVencimiento.evaluarPrioridadFefo(comando.datos());
        verificarUnicos(nuevo);
        return confirmar(nuevo);
    }

    public Map<String, Object> manejar(BloquearLoteVencido comando) {
        AlertaVencimiento a = cargar(comando.id());
        AlertaVencimientoMemento memento = a.crearMemento();
        try {
            a.bloquearLoteVencido(comando.datos());
        } catch (ReglaNegocioException e) {
            a.restaurar(memento);
            throw e;
        }
        caretaker.guardar(a.getId(), memento);
        return confirmar(a);
    }

    /** Deshace el último comando (patrón Memento). */
    public Map<String, Object> deshacer(String id) {
        AlertaVencimiento a = cargar(id);
        AlertaVencimientoMemento m = caretaker.ultimo(id);
        if (m == null) throw new ReglaNegocioException("No hay cambios para deshacer");
        a.restaurar(m);
        repo.guardar(a);
        return a.aMapa();
    }

    public Map<String, Object> obtener(String id) { return cargar(id).aMapa(); }

    public List<Map<String, Object>> listar() { return repo.listar().stream().map(AlertaVencimiento::aMapa).toList(); }
}
