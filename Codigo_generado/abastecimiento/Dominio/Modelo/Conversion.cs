using System.Globalization;

namespace Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;

/// <summary>Conversión de valores a los tipos de los atributos del dominio (la usan los agregados).</summary>
public static class Conversion
{
    public static string? Texto(string c, object? v) => v?.ToString();

    public static int? Entero(string c, object? v)
    {
        if (v is null) return null;
        if (v is string s0 && s0.Length == 0) return null;
        try { return Convert.ToInt32(v, CultureInfo.InvariantCulture); }
        catch (Exception) { throw new ReglaNegocioException($"Valor inválido para '{c}': {v}"); }
    }

    public static double? Decimal(string c, object? v)
    {
        if (v is null) return null;
        try { return Convert.ToDouble(v, CultureInfo.InvariantCulture); }
        catch (Exception) { throw new ReglaNegocioException($"Valor inválido para '{c}': {v}"); }
    }

    public static DateOnly? Fecha(string c, object? v)
    {
        if (v is null) return null;
        if (v is DateOnly d) return d;
        if (v is DateTime dt) return DateOnly.FromDateTime(dt);   // así llegan las columnas DATE desde Npgsql
        return DateOnly.TryParseExact(v.ToString(), "yyyy-MM-dd", out var f) ? f : throw new ReglaNegocioException($"Valor inválido para '{c}': {v}");
    }

    public static bool? Booleano(string c, object? v) => v is null ? null : Convert.ToBoolean(v, CultureInfo.InvariantCulture);
}
