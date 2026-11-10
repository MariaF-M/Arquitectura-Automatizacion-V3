package co.edu.farmacia.vencimientos.aplicacion.comandos;

import java.util.Map;

/** Comando «Bloquear Lote Vencido» sobre AlertaVencimiento (Application Process en V6). */
public record BloquearLoteVencido(String id, Map<String, Object> datos) { }
