using System.Collections.Concurrent;

namespace Co.Edu.Farmacia.Abastecimiento.Dominio.Memento;

/// <summary>Caretaker del patrón Memento: historial de estados por agregado.</summary>
public class Caretaker<TMemento>(int maximo = 20) where TMemento : class
{
    private readonly ConcurrentDictionary<string, LinkedList<TMemento>> _historial = new();

    public void Guardar(string id, TMemento memento)
    {
        var pila = _historial.GetOrAdd(id, _ => new LinkedList<TMemento>());
        lock (pila)
        {
            pila.AddFirst(memento);
            while (pila.Count > maximo) pila.RemoveLast();
        }
    }

    public TMemento? Ultimo(string id)
    {
        if (!_historial.TryGetValue(id, out var pila)) return null;
        lock (pila)
        {
            if (pila.First is null) return null;
            var m = pila.First.Value;
            pila.RemoveFirst();
            return m;
        }
    }
}
