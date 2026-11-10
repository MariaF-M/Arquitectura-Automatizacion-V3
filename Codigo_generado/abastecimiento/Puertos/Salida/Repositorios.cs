using Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;

namespace Co.Edu.Farmacia.Abastecimiento.Puertos.Salida;

/// <summary>Puerto de persistencia de RequerimientoCompra (DIP: el dominio no conoce la base de datos).</summary>
public interface IRepositorioRequerimientoCompra
{
    void Guardar(RequerimientoCompra agregado);
    RequerimientoCompra? Obtener(string id);
    IReadOnlyList<RequerimientoCompra> Listar();
}
