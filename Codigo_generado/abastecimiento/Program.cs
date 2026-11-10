// Punto de entrada de Abastecimiento — raíz de composición (inyección de dependencias de ASP.NET Core).
// Contexto: D-04 Abastecimiento y requerimientos de compra (SUPPORTING) · Arquitectura: hexagonal · Puerto: 8004
// Consume a Planificación de Demanda: «Customer / Supplier»
// Consume a Seguridad y Auditoría: «Open Host Service»
// Consume a Inventario: «Customer / Supplier»
// INT-04 ERP de compras y contabilidad (salida) vía ACL-01
// Generado automáticamente desde el modelo ArchiMate.
using Co.Edu.Farmacia.Abastecimiento.Adaptadores.Entrada;
using Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Clientes;
using Co.Edu.Farmacia.Abastecimiento.Puertos.Entrada;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Memento;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Modelo;
using Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Persistencia;
using Co.Edu.Farmacia.Abastecimiento.Puertos.Salida;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Servicios;
using Co.Edu.Farmacia.Abastecimiento.Dominio.Eventos;
using Co.Edu.Farmacia.Abastecimiento.Adaptadores.Salida.Transversal;

string Env(string clave, string defecto) => Environment.GetEnvironmentVariable(clave) ?? defecto;

var builder = WebApplication.CreateBuilder(args);
var puerto = Env("PUERTO", "8004");
builder.WebHost.UseUrls($"http://0.0.0.0:{puerto}");
var usarBd = Env("PERSISTENCIA", "memoria") == "bd";

builder.Services.AddSingleton(new Cifrador());
builder.Services.AddSingleton<BusEventos>();
builder.Services.AddSingleton(sp => new RepositorioRequerimientoCompraCache(
    usarBd ? new RepositorioRequerimientoCompraBaseDatos(sp.GetRequiredService<Cifrador>()) : new RepositorioRequerimientoCompraMemoria(sp.GetRequiredService<Cifrador>())));
builder.Services.AddSingleton<IRepositorioRequerimientoCompra>(sp => sp.GetRequiredService<RepositorioRequerimientoCompraCache>());
builder.Services.AddSingleton(new Caretaker<RequerimientoCompraMemento>());
builder.Services.AddSingleton<ManejadorRequerimientoCompra>();
// customer-supplier: «Customer / Supplier»
builder.Services.AddHttpClient<IPuertoPlanificacionDeDemanda, ClientePlanificacionDeDemandaHttp>(c =>
    c.BaseAddress = new Uri(Env("PLANIFICACION_DE_DEMANDA_URL", "http://localhost:8003")));
// open-host-service: «Open Host Service»
builder.Services.AddHttpClient<IPuertoSeguridadYAuditoria, ClienteSeguridadYAuditoriaHttp>(c =>
    c.BaseAddress = new Uri(Env("SEGURIDAD_Y_AUDITORIA_URL", "http://localhost:8005")));
// customer-supplier: «Customer / Supplier»
builder.Services.AddHttpClient<IPuertoInventario, ClienteInventarioHttp>(c =>
    c.BaseAddress = new Uri(Env("INVENTARIO_URL", "http://localhost:8001")));
builder.Services.AddHttpClient<IPuertoAnticorrupcion, ClienteAnticorrupcionHttp>(c =>
    c.BaseAddress = new Uri(Env("ACL_URL", "http://localhost:8010")));

// CORS: permite que los microfrontends (otro origen) llamen a esta API
var origenes = Env("CORS_ORIGENES", "*");
builder.Services.AddCors(o => o.AddDefaultPolicy(p =>
{
    if (origenes == "*") p.AllowAnyOrigin(); else p.WithOrigins(origenes.Split(','));
    p.AllowAnyHeader().AllowAnyMethod();
}));

var app = builder.Build();
app.UseCors();

var bus = app.Services.GetRequiredService<BusEventos>();
// INT-04: cuando ocurre «Requerimiento Autorizado» se envía a Sistema ERP (Compras) por la ACL
bus.Suscribir("RequerimientoAutorizado", e =>
    _ = app.Services.CreateScope().ServiceProvider.GetRequiredService<IPuertoAnticorrupcion>().Enviar("INT-04", e.Datos));

Rutas.Mapear(app, () => new Dictionary<string, object?>
{
    ["contexto"] = "Abastecimiento",
    ["dominio"] = "D-04 Abastecimiento y requerimientos de compra",
    ["clasificacion"] = "SUPPORTING",
    ["arquitectura"] = "hexagonal",
    ["componentes"] = Catalogo.Componentes,
    ["funciones"] = Catalogo.Funciones.Keys,
    ["cache"] = new Dictionary<string, object?>
    {
        ["requerimiento-compra"] = new { aciertos = app.Services.GetRequiredService<RepositorioRequerimientoCompraCache>().Aciertos, fallos = app.Services.GetRequiredService<RepositorioRequerimientoCompraCache>().Fallos },
    },
});

app.Run();
