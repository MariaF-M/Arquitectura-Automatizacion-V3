using Co.Edu.Farmacia.Abastecimiento.Dominio.Eventos;

namespace Co.Edu.Farmacia.Abastecimiento.Dominio.Eventos;

/// <summary>Bus de eventos en memoria (patrón Observer).</summary>
public class BusEventos(ILogger<BusEventos> log)
{
    private readonly Dictionary<string, List<Action<EventoDominio>>> _suscriptores = [];
    private readonly List<Dictionary<string, object?>> _historial = [];

    public IReadOnlyList<Dictionary<string, object?>> Historial { get { lock (_historial) return _historial.ToList(); } }

    public void Suscribir(string nombreEvento, Action<EventoDominio> manejador)
    {
        if (!_suscriptores.TryGetValue(nombreEvento, out var lista)) _suscriptores[nombreEvento] = lista = [];
        lista.Add(manejador);
    }

    public void Publicar(EventoDominio evento)
    {
        lock (_historial) _historial.Add(evento.AMapa());
        log.LogInformation("evento publicado: {Evento} ({Id})", evento.Nombre, evento.AgregadoId);
        foreach (var m in _suscriptores.GetValueOrDefault(evento.Nombre) ?? [])
        {
            try { m(evento); }
            catch (Exception e) { log.LogWarning("falló un suscriptor de {Evento}: {Error}", evento.Nombre, e.Message); }
        }
    }
}
