using System.Collections.Concurrent;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;
using Co.Edu.Farmacia.Abastecimiento.Puertos.Salida;
using Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Transversal;

namespace Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Persistencia;

/// <summary>Persistencia en memoria (por defecto). Cifra en reposo: autorizado_por.</summary>
public class RepositorioRequerimientoCompraMemoria(Cifrador cifrador) : IRepositorioRequerimientoCompra
{
    private static readonly string[] CamposCifrados = ["autorizado_por"];
    private readonly ConcurrentDictionary<string, Dictionary<string, object?>> _datos = new();

    public void Guardar(RequerimientoCompra agregado) => _datos[agregado.Id] = cifrador.CifrarCampos(agregado.AMapa(), CamposCifrados);

    public RequerimientoCompra? Obtener(string id) =>
        _datos.TryGetValue(id, out var fila) ? RequerimientoCompra.DesdeMapa(cifrador.DescifrarCampos(fila, CamposCifrados)) : null;

    public IReadOnlyList<RequerimientoCompra> Listar() => _datos.Keys.Select(k => Obtener(k)!).ToList();
}
