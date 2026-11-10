package co.edu.farmacia.vencimientos.contratos;

/**
 * Lenguaje publicado de Vencimientos: evento de integración «Lote Bloqueado», versión 1.
 * Solo tipos primitivos y sin dependencias del dominio, para que otro contexto lo use sin arrastrarlo.
 */
public record LoteBloqueadoV1(String eventoId, String ocurridoEn, String alertaVencimientoId, String loteCodigo, String fechaVencimiento, Integer diasParaVencer, Integer prioridadFefo, String semaforo, String estado, String motivo) { }
