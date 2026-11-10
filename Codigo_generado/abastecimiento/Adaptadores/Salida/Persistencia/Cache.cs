using System.Collections.Concurrent;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;
using Co.Edu.Farmacia.Abastecimiento.Puertos.Salida;

namespace Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Persistencia;

/// <summary>Caché con TTL (30 s) como decorador del repositorio (patrón Decorator).</summary>
public class RepositorioRequerimientoCompraCache(IRepositorioRequerimientoCompra repo, int ttlSegundos = 30) : IRepositorioRequerimientoCompra
{
    private readonly ConcurrentDictionary<string, (RequerimientoCompra Valor, DateTime Momento)> _cache = new();
    public int Aciertos { get; private set; }
    public int Fallos { get; private set; }

    public void Guardar(RequerimientoCompra a)
    {
        repo.Guardar(a);
        _cache.TryRemove(a.Id, out _);
    }

    public RequerimientoCompra? Obtener(string id)
    {
        if (_cache.TryGetValue(id, out var e) && (DateTime.UtcNow - e.Momento).TotalSeconds < ttlSegundos)
        {
            Aciertos++;
            return e.Valor;
        }
        Fallos++;
        var v = repo.Obtener(id);
        if (v is not null) _cache[id] = (v, DateTime.UtcNow);
        return v;
    }

    public IReadOnlyList<RequerimientoCompra> Listar() => repo.Listar();
}
