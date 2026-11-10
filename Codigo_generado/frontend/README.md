# Frontend — shell + microfrontends

Generado desde el modelo ArchiMate. Ver la sección de microfrontends del README principal.

| App | Rol | Puerto |
|---|---|---|
| `shell` | Host: compone los microfrontends en tiempo de ejecución | 5100 |
| `mf-inventario` | Remoto: Inventario (D-01 CORE) | 5101 |
| `mf-vencimientos` | Remoto: Vencimientos (D-02 CORE) | 5102 |
| `mf-planificacion-de-demanda` | Remoto: Planificación de Demanda (D-03 SUPPORTING) | 5103 |
| `mf-abastecimiento` | Remoto: Abastecimiento (D-04 SUPPORTING) | 5104 |
| `mf-seguridad-y-auditoria` | Remoto: Seguridad y Auditoría (D-05 GENERIC) | 5105 |
| `mf-integraciones` | Remoto: Integraciones (V9 ACL) | 5106 |

```bash
npm install          # una vez (workspaces)
npm run iniciar      # construye todo y sirve las 7 apps
# abrir http://localhost:5100
```

Por defecto cada microfrontend llama directo al puerto de su servicio. Para pasar por el gateway:
`VITE_API_URL=http://localhost:8080/api npm run iniciar` (así lo hace docker-compose).
