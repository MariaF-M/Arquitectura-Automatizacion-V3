package co.edu.farmacia.vencimientos.infraestructura.persistencia;

import co.edu.farmacia.vencimientos.dominio.modelo.AlertaVencimiento;
import co.edu.farmacia.vencimientos.dominio.puertos.RepositorioAlertaVencimiento;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/** Caché con TTL (60 s) como decorador del repositorio (patrón Decorator). */
public class RepositorioAlertaVencimientoCache implements RepositorioAlertaVencimiento {
    private record Entrada(AlertaVencimiento valor, long momento) { }

    private final RepositorioAlertaVencimiento repo;
    private final long ttlMs;
    private final Map<String, Entrada> cache = new ConcurrentHashMap<>();
    private int aciertos;
    private int fallos;

    public RepositorioAlertaVencimientoCache(RepositorioAlertaVencimiento repo) { this(repo, 60); }

    public RepositorioAlertaVencimientoCache(RepositorioAlertaVencimiento repo, int ttlSegundos) {
        this.repo = repo;
        this.ttlMs = ttlSegundos * 1000L;
    }

    @Override
    public void guardar(AlertaVencimiento a) {
        repo.guardar(a);
        cache.remove(a.getId());
    }

    @Override
    public AlertaVencimiento obtener(String id) {
        Entrada e = cache.get(id);
        if (e != null && System.currentTimeMillis() - e.momento() < ttlMs) {
            aciertos++;
            return e.valor();
        }
        fallos++;
        AlertaVencimiento v = repo.obtener(id);
        if (v != null) cache.put(id, new Entrada(v, System.currentTimeMillis()));
        return v;
    }

    @Override public List<AlertaVencimiento> listar() { return repo.listar(); }

    public Map<String, Integer> estadisticas() { return Map.of("aciertos", aciertos, "fallos", fallos); }
}
