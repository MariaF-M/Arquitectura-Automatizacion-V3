package co.edu.farmacia.vencimientos.dominio.puertos;

import co.edu.farmacia.vencimientos.dominio.modelo.AlertaVencimiento;

import java.util.List;

/** Puerto de persistencia de AlertaVencimiento: el dominio depende de esta abstracción (DIP). */
public interface RepositorioAlertaVencimiento {
    void guardar(AlertaVencimiento agregado);
    AlertaVencimiento obtener(String id);
    List<AlertaVencimiento> listar();
}
