// Catálogo de microfrontends que compone el shell. Generado desde V5/V8/V9 del modelo ArchiMate.
import { lazy, type ComponentType, type LazyExoticComponent } from 'react';

export interface Remoto {
  id: string;
  nombre: string;
  dominio: string;
  clasificacion: string;
  puerto: number;
  Componente: LazyExoticComponent<ComponentType>;
}

export const REMOTOS: Remoto[] = [
  {
    id: 'mf_inventario', nombre: 'Inventario', dominio: 'D-01', clasificacion: 'CORE', puerto: 5101,
    Componente: lazy(() => import('mf_inventario/App')),
  },
  {
    id: 'mf_vencimientos', nombre: 'Vencimientos', dominio: 'D-02', clasificacion: 'CORE', puerto: 5102,
    Componente: lazy(() => import('mf_vencimientos/App')),
  },
  {
    id: 'mf_planificacion_de_demanda', nombre: 'Planificación de Demanda', dominio: 'D-03', clasificacion: 'SUPPORTING', puerto: 5103,
    Componente: lazy(() => import('mf_planificacion_de_demanda/App')),
  },
  {
    id: 'mf_abastecimiento', nombre: 'Abastecimiento', dominio: 'D-04', clasificacion: 'SUPPORTING', puerto: 5104,
    Componente: lazy(() => import('mf_abastecimiento/App')),
  },
  {
    id: 'mf_seguridad_y_auditoria', nombre: 'Seguridad y Auditoría', dominio: 'D-05', clasificacion: 'GENERIC', puerto: 5105,
    Componente: lazy(() => import('mf_seguridad_y_auditoria/App')),
  },
  {
    id: 'mf_integraciones', nombre: 'Integraciones', dominio: 'V9', clasificacion: 'ACL', puerto: 5106,
    Componente: lazy(() => import('mf_integraciones/App')),
  },
];
