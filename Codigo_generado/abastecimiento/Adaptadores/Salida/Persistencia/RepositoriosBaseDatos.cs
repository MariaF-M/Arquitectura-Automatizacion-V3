using Npgsql;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;
using Co.Edu.Farmacia.Abastecimiento.Puertos.Salida;
using Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Transversal;

namespace Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Persistencia;

/// <summary>
/// Adaptador de persistencia para postgresql (SQL). Se activa con PERSISTENCIA=bd.
/// Tabla «requerimiento_compra». Campos cifrados en reposo: autorizado_por.
/// Justificación: Un requerimiento pasa por estados controlados (sugerido, autorizado) y debe quedar auditable ante Compras/ERP; se necesita integridad referencial y transacciones.
/// </summary>
public class RepositorioRequerimientoCompraBaseDatos : IRepositorioRequerimientoCompra
{
    private static readonly string[] CamposCifrados = ["autorizado_por"];
    private readonly Cifrador _cifrador;
    private static readonly string[] Campos = ["principio_activo", "concentracion", "cantidad", "nivel_urgencia", "estado", "autorizado_por"];
    private const string Ddl = """
        CREATE TABLE IF NOT EXISTS requerimiento_compra (
            id VARCHAR(36) PRIMARY KEY,
            principio_activo VARCHAR(255) NOT NULL,
            concentracion VARCHAR(255) NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
            nivel_urgencia VARCHAR(255) NOT NULL CHECK (nivel_urgencia IN ('Baja', 'Media', 'Alta', 'Critica')),
            estado VARCHAR(255) CHECK (estado IN ('Sugerido', 'Autorizado')),
            autorizado_por TEXT
        )
        """;
    private readonly NpgsqlDataSource _fuente;

    public RepositorioRequerimientoCompraBaseDatos(Cifrador cifrador)
    {
        _cifrador = cifrador;
        // BD_URL en formato Npgsql: Host=postgres;Database=base;Username=u;Password=p
        var cadena = Environment.GetEnvironmentVariable("BD_URL") ?? "Host=localhost;Database=abastecimiento;Username=farmacia;Password=farmacia";
        _fuente = NpgsqlDataSource.Create(cadena);
        using var cmd = _fuente.CreateCommand(Ddl);
        cmd.ExecuteNonQuery();
    }

    public void Guardar(RequerimientoCompra agregado)
    {
        var fila = _cifrador.CifrarCampos(agregado.AMapa(), CamposCifrados);
        var sql = $"INSERT INTO requerimiento_compra (id, {string.Join(", ", Campos)}) VALUES (@id, {string.Join(", ", Campos.Select(c => "@" + c))}) "
                + $"ON CONFLICT (id) DO UPDATE SET {string.Join(", ", Campos.Select(c => $"{c} = EXCLUDED.{c}"))}";
        using var cmd = _fuente.CreateCommand(sql);
        cmd.Parameters.AddWithValue("id", agregado.Id);
        cmd.Parameters.AddWithValue("principio_activo", fila["principio_activo"] ?? DBNull.Value);
        cmd.Parameters.AddWithValue("concentracion", fila["concentracion"] ?? DBNull.Value);
        cmd.Parameters.AddWithValue("cantidad", fila["cantidad"] ?? DBNull.Value);
        cmd.Parameters.AddWithValue("nivel_urgencia", fila["nivel_urgencia"] ?? DBNull.Value);
        cmd.Parameters.AddWithValue("estado", fila["estado"] ?? DBNull.Value);
        cmd.Parameters.AddWithValue("autorizado_por", fila["autorizado_por"] ?? DBNull.Value);
        cmd.ExecuteNonQuery();
    }

    private RequerimientoCompra DesdeLector(NpgsqlDataReader r)
    {
        var m = new Dictionary<string, object?>();
        for (var i = 0; i < r.FieldCount; i++)
            m[r.GetName(i)] = r.IsDBNull(i) ? null : r.GetValue(i);
        return RequerimientoCompra.DesdeMapa(_cifrador.DescifrarCampos(m, CamposCifrados));
    }

    public RequerimientoCompra? Obtener(string id)
    {
        using var cmd = _fuente.CreateCommand("SELECT * FROM requerimiento_compra WHERE id = @id");
        cmd.Parameters.AddWithValue("id", id);
        using var r = cmd.ExecuteReader();
        return r.Read() ? DesdeLector(r) : null;
    }

    public IReadOnlyList<RequerimientoCompra> Listar()
    {
        using var cmd = _fuente.CreateCommand("SELECT * FROM requerimiento_compra ORDER BY id");
        using var r = cmd.ExecuteReader();
        var lista = new List<RequerimientoCompra>();
        while (r.Read()) lista.Add(DesdeLector(r));
        return lista;
    }
}
