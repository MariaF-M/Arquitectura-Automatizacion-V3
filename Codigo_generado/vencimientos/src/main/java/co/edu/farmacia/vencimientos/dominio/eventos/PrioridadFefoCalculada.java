package co.edu.farmacia.vencimientos.dominio.eventos;

import java.util.Map;

/** Evento «Prioridad FEFO Calculada» del agregado AlertaVencimiento (V6). */
public class PrioridadFefoCalculada extends EventoDominio {
    public PrioridadFefoCalculada(String agregadoId, Map<String, Object> datos) { super(agregadoId, datos); }
}
