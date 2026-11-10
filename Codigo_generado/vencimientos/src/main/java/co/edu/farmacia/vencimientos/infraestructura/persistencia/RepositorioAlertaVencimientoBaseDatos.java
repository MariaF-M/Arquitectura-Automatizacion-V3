package co.edu.farmacia.vencimientos.infraestructura.persistencia;

import co.edu.farmacia.vencimientos.dominio.modelo.AlertaVencimiento;
import co.edu.farmacia.vencimientos.dominio.puertos.RepositorioAlertaVencimiento;
import co.edu.farmacia.vencimientos.infraestructura.transversal.Cifrador;

import com.mongodb.MongoClient;
import com.mongodb.MongoClientURI;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.FindOneAndReplaceOptions;
import org.bson.Document;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Adaptador de persistencia para mongodb (NoSQL). Se activa con PERSISTENCIA=bd.
 * Colección «alerta_vencimiento». Campos cifrados en reposo: motivo.
 * Justificación: Las alertas son documentos de vida corta, con semaforización y metadatos que cambian según el tipo de alerta (vencimiento, retiro regulatorio). Se escriben mucho y se consultan por lote o semáforo; un documento por alerta evita joins y permite evolucionar el esquema sin migraciones.
 */
public class RepositorioAlertaVencimientoBaseDatos implements RepositorioAlertaVencimiento {
    private static final List<String> CAMPOS_CIFRADOS = List.of("motivo");
    private final Cifrador cifrador;
    private final MongoCollection<Document> coleccion;

    public RepositorioAlertaVencimientoBaseDatos(Cifrador cifrador) {
        this.cifrador = cifrador;
        MongoClientURI uri = new MongoClientURI(System.getenv().getOrDefault("BD_URL", "mongodb://localhost:27017/vencimientos"));
        this.coleccion = new MongoClient(uri).getDatabase(uri.getDatabase()).getCollection("alerta_vencimiento");
    }

    @Override
    public void guardar(AlertaVencimiento agregado) {
        Document doc = new Document(cifrador.cifrarCampos(agregado.aMapa(), CAMPOS_CIFRADOS));
        doc.put("_id", doc.remove("id"));
        coleccion.findOneAndReplace(Filters.eq("_id", agregado.getId()), doc, new FindOneAndReplaceOptions().upsert(true));
    }

    private AlertaVencimiento desdeDocumento(Document d) {
        Map<String, Object> m = new LinkedHashMap<>(d);
        m.put("id", m.remove("_id"));
        return AlertaVencimiento.desdeMapa(cifrador.descifrarCampos(m, CAMPOS_CIFRADOS));
    }

    @Override
    public AlertaVencimiento obtener(String id) {
        Document d = coleccion.find(Filters.eq("_id", id)).first();
        return d == null ? null : desdeDocumento(d);
    }

    @Override
    public List<AlertaVencimiento> listar() {
        List<AlertaVencimiento> r = new ArrayList<>();
        for (Document d : coleccion.find()) r.add(desdeDocumento(d));
        return r;
    }
}
