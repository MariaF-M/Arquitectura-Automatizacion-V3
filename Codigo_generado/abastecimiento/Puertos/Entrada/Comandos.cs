using Co.Edu.Farmacia.Abastecimiento.Dominio.Memento;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;
using Co.Edu.Farmacia.Abastecimiento.Puertos.Salida;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Eventos;

namespace Co.Edu.Farmacia.Abastecimiento.Puertos.Entrada;

/// <summary>Comando «Generar Requisición» (Application Process en V6).</summary>
public sealed record GenerarRequisicionComando(Dictionary<string, object?> Datos);

/// <summary>Comando «Autorizar Requisición» (Application Process en V6).</summary>
public sealed record AutorizarRequisicionComando(string Id, Dictionary<string, object?> Datos);

/// <summary>
/// Manejador de comandos de RequerimientoCompra: toma memento, ejecuta, valida invariantes;
/// si falla restaura el memento; si no, guarda y publica eventos.
/// </summary>
public class ManejadorRequerimientoCompra(IRepositorioRequerimientoCompra repo, BusEventos bus, Caretaker<RequerimientoCompraMemento> caretaker)
{
    private RequerimientoCompra Cargar(string id) => repo.Obtener(id) ?? throw new NoEncontradoException($"RequerimientoCompra {id} no existe");

    /// <summary>Atributos que no se pueden repetir (spec.yaml -> unicos).</summary>
    private void VerificarUnicos(RequerimientoCompra nuevo)
    {
    }

    private Dictionary<string, object?> Confirmar(RequerimientoCompra a)
    {
        repo.Guardar(a);
        foreach (var e in a.ExtraerEventos()) bus.Publicar(e);
        return a.AMapa();
    }

    public Dictionary<string, object?> Manejar(GenerarRequisicionComando comando)
    {
        var nuevo = RequerimientoCompra.GenerarRequisicion(comando.Datos);
        VerificarUnicos(nuevo);
        return Confirmar(nuevo);
    }

    public Dictionary<string, object?> Manejar(AutorizarRequisicionComando comando)
    {
        var a = Cargar(comando.Id);
        var memento = a.CrearMemento();
        try { a.AutorizarRequisicion(comando.Datos); }
        catch (ReglaNegocioException) { a.Restaurar(memento); throw; }
        caretaker.Guardar(a.Id, memento);
        return Confirmar(a);
    }

    /// <summary>Deshace el último comando (patrón Memento).</summary>
    public Dictionary<string, object?> Deshacer(string id)
    {
        var a = Cargar(id);
        var m = caretaker.Ultimo(id) ?? throw new ReglaNegocioException("No hay cambios para deshacer");
        a.Restaurar(m);
        repo.Guardar(a);
        return a.AMapa();
    }

    public Dictionary<string, object?> Obtener(string id) => Cargar(id).AMapa();

    public List<Dictionary<string, object?>> Listar() => repo.Listar().Select(a => a.AMapa()).ToList();
}
