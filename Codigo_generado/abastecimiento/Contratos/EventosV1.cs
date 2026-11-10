namespace Co.Edu.Farmacia.Abastecimiento.Contratos;

// Lenguaje publicado de Abastecimiento: eventos de integración versionados (V1).
// Solo tipos primitivos y sin dependencias del dominio, para que otro contexto los use sin arrastrarlo.

/// <summary>Evento de integración «Requisición Sugerida», versión 1.</summary>
public sealed record RequisicionSugeridaV1(Guid EventoId, DateTimeOffset OcurrioEn, string RequerimientoCompraId, string? PrincipioActivo, string? Concentracion, int? Cantidad, string? NivelUrgencia, string? Estado, string? AutorizadoPor);

/// <summary>Evento de integración «Requerimiento Autorizado», versión 1.</summary>
public sealed record RequerimientoAutorizadoV1(Guid EventoId, DateTimeOffset OcurrioEn, string RequerimientoCompraId, string? PrincipioActivo, string? Concentracion, int? Cantidad, string? NivelUrgencia, string? Estado, string? AutorizadoPor);
