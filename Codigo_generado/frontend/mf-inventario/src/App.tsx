// Punto de entrada que el shell carga vía Module Federation (expuesto como './App').
import './estilos.css';
import datos from './contexto.json';
import type { Descriptor } from './tipos';
import { VistaContexto } from './componentes/VistaContexto';
import { VistaIntegraciones } from './componentes/VistaIntegraciones';

const descriptor = datos as unknown as Descriptor;

export default function App() {
  return (
    <div className="mf-raiz">
      {descriptor.tipo === 'contexto'
        ? <VistaContexto d={descriptor} />
        : <VistaIntegraciones d={descriptor} />}
    </div>
  );
}
