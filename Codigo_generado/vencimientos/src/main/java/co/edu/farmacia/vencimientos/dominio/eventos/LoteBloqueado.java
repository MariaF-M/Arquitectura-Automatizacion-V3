package co.edu.farmacia.vencimientos.dominio.eventos;

import java.util.Map;

/** Evento «Lote Bloqueado» del agregado AlertaVencimiento (V6). */
public class LoteBloqueado extends EventoDominio {
    public LoteBloqueado(String agregadoId, Map<String, Object> datos) { super(agregadoId, datos); }
}
