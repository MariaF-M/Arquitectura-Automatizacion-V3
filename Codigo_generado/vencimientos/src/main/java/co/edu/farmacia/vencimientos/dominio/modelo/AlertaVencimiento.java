package co.edu.farmacia.vencimientos.dominio.modelo;

import co.edu.farmacia.vencimientos.dominio.eventos.PrioridadFefoCalculada;
import co.edu.farmacia.vencimientos.dominio.eventos.LoteBloqueado;
import co.edu.farmacia.vencimientos.dominio.eventos.EventoDominio;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Agregado raíz «AlertaVencimiento» del contexto Vencimientos (D-02). Generado desde V6.
 * <br>Comando «Evaluar Prioridad FEFO» -> evaluarPrioridadFefo() emite «Prioridad FEFO Calculada»
 * <br>Comando «Bloquear Lote Vencido» -> bloquearLoteVencido() emite «Lote Bloqueado»
 *
 * Invariantes:
 * <br>- Regla FEFO innegociable: primero se usa lo que vence primero.
 * <br>- Lotes Vencidos o en Cuarentena no suman al inventario disponible y se bloquean automáticamente (hard stop).
 */
public class AlertaVencimiento {
    public static final Set<String> SEMAFORO_PERMITIDOS = Set.of("Verde", "Amarillo", "Rojo");
    public static final Set<String> ESTADO_PERMITIDOS = Set.of("Activa", "Atendida", "LoteBloqueado");

    private final String id;
    private String loteCodigo;
    private LocalDate fechaVencimiento;
    private Integer diasParaVencer;
    private Integer prioridadFefo;
    private String semaforo;
    private String estado;
    private String motivo;
    private final List<EventoDominio> eventos = new ArrayList<>();

    public AlertaVencimiento(String id, Map<String, Object> datos) {
        this.id = (id == null || id.isBlank()) ? UUID.randomUUID().toString() : id;
        aplicar(Map.of("estado", "Activa"));
        aplicar(datos);
    }

    // ------------------------------------------------------------------ comandos (V6)
    /** Comando «Evaluar Prioridad FEFO»: crea el agregado. */
    public static AlertaVencimiento evaluarPrioridadFefo(Map<String, Object> datos) {
        Map<String, Object> d = new LinkedHashMap<>(datos);
        d.remove("id");
        AlertaVencimiento agregado = new AlertaVencimiento(null, d);
        agregado.validar();
        agregado.eventos.add(new PrioridadFefoCalculada(agregado.id, agregado.aMapa()));
        return agregado;
    }

    /** Comando «Bloquear Lote Vencido». */
    public void bloquearLoteVencido(Map<String, Object> datos) {
        if (!Set.of("Activa").contains(estado))
            throw new ReglaNegocioException("«Bloquear Lote Vencido» no se permite con estado '" + estado + "'");
        Map<String, Object> d = new LinkedHashMap<>(datos);
        d.remove("id");
        aplicar(d);
        estado = "LoteBloqueado";
        validar();
        eventos.add(new LoteBloqueado(id, aMapa()));
    }

    // ------------------------------------------------------------------ invariantes
    public void validar() {
        if (loteCodigo == null || loteCodigo.isBlank())
            throw new ReglaNegocioException("El campo 'lote_codigo' es obligatorio en AlertaVencimiento");
        if (fechaVencimiento == null)
            throw new ReglaNegocioException("El campo 'fecha_vencimiento' es obligatorio en AlertaVencimiento");
        if (prioridadFefo != null && prioridadFefo < 0)
            throw new ReglaNegocioException("'prioridad_fefo' no puede ser negativo (valor: " + prioridadFefo + ")");
        if (semaforo != null && !SEMAFORO_PERMITIDOS.contains(semaforo))
            throw new ReglaNegocioException("'semaforo' = '" + semaforo + "' no es válido. Permitidos: " + SEMAFORO_PERMITIDOS);
        if (estado != null && !ESTADO_PERMITIDOS.contains(estado))
            throw new ReglaNegocioException("'estado' = '" + estado + "' no es válido. Permitidos: " + ESTADO_PERMITIDOS);
    }

    // ------------------------------------------------------------------ memento
    public AlertaVencimientoMemento crearMemento() {
        return new AlertaVencimientoMemento(id, loteCodigo, fechaVencimiento, diasParaVencer, prioridadFefo, semaforo, estado, motivo);
    }

    public void restaurar(AlertaVencimientoMemento m) {
        this.loteCodigo = m.loteCodigo();
        this.fechaVencimiento = m.fechaVencimiento();
        this.diasParaVencer = m.diasParaVencer();
        this.prioridadFefo = m.prioridadFefo();
        this.semaforo = m.semaforo();
        this.estado = m.estado();
        this.motivo = m.motivo();
    }

    // ------------------------------------------------------------------ utilidades
    private void aplicar(Map<String, Object> datos) {
        for (Map.Entry<String, Object> e : datos.entrySet()) {
            Object v = e.getValue();
            switch (e.getKey()) {
                case "lote_codigo" -> loteCodigo = aTexto("lote_codigo", v);
                case "fecha_vencimiento" -> fechaVencimiento = aFecha("fecha_vencimiento", v);
                case "dias_para_vencer" -> diasParaVencer = aEntero("dias_para_vencer", v);
                case "prioridad_fefo" -> prioridadFefo = aEntero("prioridad_fefo", v);
                case "semaforo" -> semaforo = aTexto("semaforo", v);
                case "estado" -> estado = aTexto("estado", v);
                case "motivo" -> motivo = aTexto("motivo", v);
                default -> { }
            }
        }
    }

    private static String aTexto(String c, Object v) { return v == null ? null : String.valueOf(v); }

    private static Integer aEntero(String c, Object v) {
        if (v == null) return null;
        try { return v instanceof Number n ? n.intValue() : Integer.parseInt(String.valueOf(v)); }
        catch (NumberFormatException e) { throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v); }
    }

    private static Double aDecimal(String c, Object v) {
        if (v == null) return null;
        try { return v instanceof Number n ? n.doubleValue() : Double.parseDouble(String.valueOf(v)); }
        catch (NumberFormatException e) { throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v); }
    }

    private static LocalDate aFecha(String c, Object v) {
        if (v == null) return null;
        try { return v instanceof LocalDate f ? f : LocalDate.parse(String.valueOf(v)); }
        catch (RuntimeException e) { throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v); }
    }

    private static Boolean aBooleano(String c, Object v) {
        return v == null ? null : (v instanceof Boolean b ? b : Boolean.parseBoolean(String.valueOf(v)));
    }

    public List<EventoDominio> extraerEventos() {
        List<EventoDominio> r = List.copyOf(eventos);
        eventos.clear();
        return r;
    }

    public String getId() { return id; }

    public Map<String, Object> aMapa() {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", id);
        m.put("lote_codigo", loteCodigo);
        m.put("fecha_vencimiento", fechaVencimiento == null ? null : fechaVencimiento.toString());
        m.put("dias_para_vencer", diasParaVencer);
        m.put("prioridad_fefo", prioridadFefo);
        m.put("semaforo", semaforo);
        m.put("estado", estado);
        m.put("motivo", motivo);
        return m;
    }

    public static AlertaVencimiento desdeMapa(Map<String, Object> m) {
        Map<String, Object> d = new LinkedHashMap<>(m);
        Object id = d.remove("id");
        return new AlertaVencimiento(id == null ? null : String.valueOf(id), d);
    }
}
