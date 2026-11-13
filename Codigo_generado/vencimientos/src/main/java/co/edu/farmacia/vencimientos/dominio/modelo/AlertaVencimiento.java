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
        if (datos.get("motivo") == null || String.valueOf(datos.get("motivo")).isBlank())
            throw new ReglaNegocioException("«Bloquear Lote Vencido» requiere 'motivo'");
        Map<String, Object> d = new LinkedHashMap<>(datos);
        d.remove("id");
        aplicar(d);
        estado = "LoteBloqueado";
        validar();
        eventos.add(new LoteBloqueado(id, aMapa()));
    }

    // ------------------------------------------------------------------ invariantes
    public void validar() {
        validarFormatos();
        if (loteCodigo == null || loteCodigo.isBlank())
            throw new ReglaNegocioException("El campo 'lote_codigo' es obligatorio en AlertaVencimiento");
        if (fechaVencimiento == null)
            throw new ReglaNegocioException("El campo 'fecha_vencimiento' es obligatorio en AlertaVencimiento");
        if (prioridadFefo == null)
            throw new ReglaNegocioException("El campo 'prioridad_fefo' es obligatorio en AlertaVencimiento");
        if (semaforo == null || semaforo.isBlank())
            throw new ReglaNegocioException("El campo 'semaforo' es obligatorio en AlertaVencimiento");
        if (prioridadFefo != null && prioridadFefo < 0)
            throw new ReglaNegocioException("'prioridad_fefo' no puede ser negativo (valor: " + prioridadFefo + ")");
        if (semaforo != null && !SEMAFORO_PERMITIDOS.contains(semaforo))
            throw new ReglaNegocioException("'semaforo' = '" + semaforo + "' no es válido. Permitidos: " + SEMAFORO_PERMITIDOS);
        if (estado != null && !ESTADO_PERMITIDOS.contains(estado))
            throw new ReglaNegocioException("'estado' = '" + estado + "' no es válido. Permitidos: " + ESTADO_PERMITIDOS);
    }

    /** Reglas de formato por atributo (spec.yaml -> formatos): patrón, rango y largo máximo. */
    private void validarFormatos() {
        if (loteCodigo != null && loteCodigo.length() > 255)
            throw new ReglaNegocioException("'lote_codigo' admite máximo 255 caracteres");
        if (loteCodigo != null && !java.util.regex.Pattern.matches("^[0-9]{3,20}$", loteCodigo))
            throw new ReglaNegocioException("'lote_codigo' " + "debe tener solo n\u00fameros, entre 3 y 20 d\u00edgitos (el c\u00f3digo del lote en Inventario)" + " (recibido: '" + loteCodigo + "')");
        if (diasParaVencer != null && diasParaVencer < -3650)
            throw new ReglaNegocioException("'dias_para_vencer' debe ser mayor o igual a -3650 (recibido: " + diasParaVencer + ")");
        if (diasParaVencer != null && diasParaVencer > 3650)
            throw new ReglaNegocioException("'dias_para_vencer' debe ser menor o igual a 3650 (recibido: " + diasParaVencer + ")");
        if (prioridadFefo != null && prioridadFefo < 1)
            throw new ReglaNegocioException("'prioridad_fefo' debe ser mayor o igual a 1 (recibido: " + prioridadFefo + ")");
        if (prioridadFefo != null && prioridadFefo > 1000)
            throw new ReglaNegocioException("'prioridad_fefo' debe ser menor o igual a 1000 (recibido: " + prioridadFefo + ")");
        if (semaforo != null && semaforo.length() > 255)
            throw new ReglaNegocioException("'semaforo' admite máximo 255 caracteres");
        if (estado != null && estado.length() > 255)
            throw new ReglaNegocioException("'estado' admite máximo 255 caracteres");
        if (motivo != null && motivo.length() > 200)
            throw new ReglaNegocioException("'motivo' admite máximo 200 caracteres");
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

    /** Texto sin espacios al inicio/final; "   " cuenta como vacío. */
    private static String aTexto(String c, Object v) {
        if (v == null) return null;
        String t = String.valueOf(v).strip();
        return t.isEmpty() ? null : t;
    }

    private static Integer aEntero(String c, Object v) {
        if (v == null) return null;
        if (v instanceof Boolean) throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v + " (se esperaba un número entero)");
        if (v instanceof Number n && n.doubleValue() % 1 != 0)
            throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v + " (se esperaba un número entero)");
        if (v instanceof String s && s.isBlank()) return null;
        try { return v instanceof Number n ? n.intValue() : Integer.parseInt(String.valueOf(v).strip()); }
        catch (NumberFormatException e) { throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v + " (se esperaba un número entero)"); }
    }

    private static Double aDecimal(String c, Object v) {
        if (v == null) return null;
        if (v instanceof Boolean) throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v + " (se esperaba un número)");
        if (v instanceof String s && s.isBlank()) return null;
        try { return v instanceof Number n ? n.doubleValue() : Double.parseDouble(String.valueOf(v).strip().replace(',', '.')); }
        catch (NumberFormatException e) { throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v + " (se esperaba un número)"); }
    }

    private static LocalDate aFecha(String c, Object v) {
        if (v == null) return null;
        if (v instanceof String s && s.isBlank()) return null;
        try { return v instanceof LocalDate f ? f : LocalDate.parse(String.valueOf(v).strip()); }
        catch (RuntimeException e) { throw new ReglaNegocioException("Valor inválido para '" + c + "': " + v + " (se esperaba una fecha AAAA-MM-DD)"); }
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
