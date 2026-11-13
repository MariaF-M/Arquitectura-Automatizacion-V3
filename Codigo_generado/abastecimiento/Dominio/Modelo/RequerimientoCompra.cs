using Co.Edu.Farmacia.Abastecimiento.Dominio.Eventos;

namespace Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;

/// <summary>Memento (GoF): foto inmutable del estado de RequerimientoCompra.</summary>
public sealed record RequerimientoCompraMemento(string Id, string? PrincipioActivo, string? Concentracion, int? Cantidad, string? NivelUrgencia, string? Estado, string? AutorizadoPor);

/// <summary>
/// Agregado raíz «RequerimientoCompra» del contexto Abastecimiento (D-04). Generado desde V6.
/// Comando «Generar Requisición» -> GenerarRequisicion() emite «Requisición Sugerida».
/// Comando «Autorizar Requisición» -> AutorizarRequisicion() emite «Requerimiento Autorizado».
/// Invariantes:
/// - El requerimiento contiene principio activo (DCI), concentración, cantidad y nivel de urgencia.
/// - Ningún requerimiento viaja a Compras (ERP) sin autorización técnica previa del Químico Farmacéutico.
/// </summary>
public class RequerimientoCompra
{
    public static readonly HashSet<string> NivelUrgenciaPermitidos = ["Baja", "Media", "Alta", "Critica"];
    public static readonly HashSet<string> EstadoPermitidos = ["Sugerido", "Autorizado"];

    public string Id { get; }
    public string? PrincipioActivo { get; private set; }
    public string? Concentracion { get; private set; }
    public int? Cantidad { get; private set; }
    public string? NivelUrgencia { get; private set; }
    public string? Estado { get; private set; }
    public string? AutorizadoPor { get; private set; }
    private readonly List<EventoDominio> _eventos = [];

    public RequerimientoCompra(string? id, IDictionary<string, object?> datos)
    {
        Id = string.IsNullOrWhiteSpace(id) ? Guid.NewGuid().ToString() : id;
        Aplicar(new Dictionary<string, object?> { ["estado"] = "Sugerido" });
        Aplicar(datos);
    }

    // ------------------------------------------------------------ comandos (V6)
    /// <summary>Comando «Generar Requisición»: crea el agregado.</summary>
    public static RequerimientoCompra GenerarRequisicion(IDictionary<string, object?> datos)
    {
        var agregado = new RequerimientoCompra(null, datos.Where(kv => kv.Key != "id").ToDictionary(kv => kv.Key, kv => kv.Value));
        agregado.Validar();
        agregado._eventos.Add(new RequisicionSugerida(agregado.Id, agregado.AMapa()));
        return agregado;
    }

    /// <summary>Comando «Autorizar Requisición».</summary>
    public void AutorizarRequisicion(IDictionary<string, object?> datos)
    {
        if (!new[] { "Sugerido" }.Contains(Estado))
            throw new ReglaNegocioException($"«Autorizar Requisición» no se permite con estado '{Estado}'");
        if (!datos.TryGetValue("autorizado_por", out var v1) || string.IsNullOrWhiteSpace(v1?.ToString()))
            throw new ReglaNegocioException("«Autorizar Requisición» requiere 'autorizado_por'");
        Aplicar(datos.Where(kv => kv.Key != "id").ToDictionary(kv => kv.Key, kv => kv.Value));
        Estado = "Autorizado";
        Validar();
        _eventos.Add(new RequerimientoAutorizado(Id, AMapa()));
    }

    // ------------------------------------------------------------ invariantes
    public void Validar()
    {
        ValidarFormatos();
        if (PrincipioActivo is null || string.IsNullOrWhiteSpace(PrincipioActivo))
            throw new ReglaNegocioException("El campo 'principio_activo' es obligatorio en RequerimientoCompra");
        if (Concentracion is null || string.IsNullOrWhiteSpace(Concentracion))
            throw new ReglaNegocioException("El campo 'concentracion' es obligatorio en RequerimientoCompra");
        if (Cantidad is null)
            throw new ReglaNegocioException("El campo 'cantidad' es obligatorio en RequerimientoCompra");
        if (NivelUrgencia is null || string.IsNullOrWhiteSpace(NivelUrgencia))
            throw new ReglaNegocioException("El campo 'nivel_urgencia' es obligatorio en RequerimientoCompra");
        if (Cantidad < 0)
            throw new ReglaNegocioException($"'cantidad' no puede ser negativo (valor: {Cantidad})");
        if (NivelUrgencia is not null && !NivelUrgenciaPermitidos.Contains(NivelUrgencia))
            throw new ReglaNegocioException($"'nivel_urgencia' = '{NivelUrgencia}' no es válido. Permitidos: {string.Join(", ", NivelUrgenciaPermitidos)}");
        if (Estado is not null && !EstadoPermitidos.Contains(Estado))
            throw new ReglaNegocioException($"'estado' = '{Estado}' no es válido. Permitidos: {string.Join(", ", EstadoPermitidos)}");
    }

    /// <summary>Reglas de formato por atributo (spec.yaml -> formatos): patrón, rango y largo máximo.</summary>
    private void ValidarFormatos()
    {
        if (PrincipioActivo is not null && PrincipioActivo.Length > 255)
            throw new ReglaNegocioException("'principio_activo' admite máximo 255 caracteres");
        if (PrincipioActivo is not null && !System.Text.RegularExpressions.Regex.IsMatch(PrincipioActivo, "^[A-Za-z\u00c1\u00c9\u00cd\u00d3\u00da\u00dc\u00d1\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1 ]{3,100}$"))
            throw new ReglaNegocioException("'principio_activo' " + "debe tener solo letras y espacios, entre 3 y 100 caracteres (ej: Cefazolina)" + $" (recibido: '{PrincipioActivo}')");
        if (Concentracion is not null && Concentracion.Length > 255)
            throw new ReglaNegocioException("'concentracion' admite máximo 255 caracteres");
        if (Concentracion is not null && !System.Text.RegularExpressions.Regex.IsMatch(Concentracion, "^[0-9]+([.,][0-9]+)? ?[A-Za-z\u00b5%/]+$"))
            throw new ReglaNegocioException("'concentracion' " + "debe ser un n\u00famero seguido de su unidad (ej: 500 mg, 1 g, 5%)" + $" (recibido: '{Concentracion}')");
        if (Cantidad < 1)
            throw new ReglaNegocioException($"'cantidad' debe ser mayor o igual a 1 (recibido: {Cantidad})");
        if (Cantidad > 1000000)
            throw new ReglaNegocioException($"'cantidad' debe ser menor o igual a 1e+06 (recibido: {Cantidad})");
        if (NivelUrgencia is not null && NivelUrgencia.Length > 255)
            throw new ReglaNegocioException("'nivel_urgencia' admite máximo 255 caracteres");
        if (Estado is not null && Estado.Length > 255)
            throw new ReglaNegocioException("'estado' admite máximo 255 caracteres");
        if (AutorizadoPor is not null && AutorizadoPor.Length > 255)
            throw new ReglaNegocioException("'autorizado_por' admite máximo 255 caracteres");
        if (AutorizadoPor is not null && !System.Text.RegularExpressions.Regex.IsMatch(AutorizadoPor, "^[A-Za-z\u00c1\u00c9\u00cd\u00d3\u00da\u00dc\u00d1\u00e1\u00e9\u00ed\u00f3\u00fa\u00fc\u00f1 .]{3,100}$"))
            throw new ReglaNegocioException("'autorizado_por' " + "debe tener solo letras, espacios y puntos (ej: QF Laura G\u00f3mez)" + $" (recibido: '{AutorizadoPor}')");
    }

    // ------------------------------------------------------------ memento
    public RequerimientoCompraMemento CrearMemento() => new(Id, PrincipioActivo, Concentracion, Cantidad, NivelUrgencia, Estado, AutorizadoPor);

    public void Restaurar(RequerimientoCompraMemento m)
    {
        PrincipioActivo = m.PrincipioActivo;
        Concentracion = m.Concentracion;
        Cantidad = m.Cantidad;
        NivelUrgencia = m.NivelUrgencia;
        Estado = m.Estado;
        AutorizadoPor = m.AutorizadoPor;
    }

    // ------------------------------------------------------------ utilidades
    private void Aplicar(IDictionary<string, object?> datos)
    {
        foreach (var (campo, valor) in datos)
        {
            switch (campo)
            {
                case "principio_activo": PrincipioActivo = Conversion.Texto(campo, valor); break;
                case "concentracion": Concentracion = Conversion.Texto(campo, valor); break;
                case "cantidad": Cantidad = Conversion.Entero(campo, valor); break;
                case "nivel_urgencia": NivelUrgencia = Conversion.Texto(campo, valor); break;
                case "estado": Estado = Conversion.Texto(campo, valor); break;
                case "autorizado_por": AutorizadoPor = Conversion.Texto(campo, valor); break;
            }
        }
    }

    public IReadOnlyList<EventoDominio> ExtraerEventos()
    {
        var r = _eventos.ToList();
        _eventos.Clear();
        return r;
    }

    public Dictionary<string, object?> AMapa() => new()
    {
        ["id"] = Id,
        ["principio_activo"] = PrincipioActivo,
        ["concentracion"] = Concentracion,
        ["cantidad"] = Cantidad,
        ["nivel_urgencia"] = NivelUrgencia,
        ["estado"] = Estado,
        ["autorizado_por"] = AutorizadoPor,
    };

    public static RequerimientoCompra DesdeMapa(IDictionary<string, object?> m) =>
        new(m["id"]?.ToString(), m.Where(kv => kv.Key != "id").ToDictionary(kv => kv.Key, kv => kv.Value));
}
