using System.Text;

namespace Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Transversal;

/// <summary>
/// Cifrado simple (XOR con clave + Base64) para campos sensibles en reposo.
/// Didáctico: en producción se cambia por AES (System.Security.Cryptography) sin tocar el dominio.
/// </summary>
public class Cifrador(string? clave = null)
{
    private const string Prefijo = "enc:";
    private readonly byte[] _clave = Encoding.UTF8.GetBytes(clave ?? Environment.GetEnvironmentVariable("CLAVE_CIFRADO") ?? "farmacia-2026");

    private byte[] Xor(byte[] d) => d.Select((b, i) => (byte)(b ^ _clave[i % _clave.Length])).ToArray();

    public string Cifrar(string texto) => Prefijo + Convert.ToBase64String(Xor(Encoding.UTF8.GetBytes(texto)));

    public string Descifrar(string texto) =>
        texto.StartsWith(Prefijo) ? Encoding.UTF8.GetString(Xor(Convert.FromBase64String(texto[Prefijo.Length..]))) : texto;

    public Dictionary<string, object?> CifrarCampos(Dictionary<string, object?> fila, string[] campos) =>
        fila.ToDictionary(kv => kv.Key, kv => campos.Contains(kv.Key) && kv.Value is not null ? Cifrar(kv.Value.ToString()!) : kv.Value);

    public Dictionary<string, object?> DescifrarCampos(Dictionary<string, object?> fila, string[] campos) =>
        fila.ToDictionary(kv => kv.Key, kv => campos.Contains(kv.Key) && kv.Value is string s ? Descifrar(s) : kv.Value);
}
