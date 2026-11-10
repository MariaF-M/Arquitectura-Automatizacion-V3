import { Component, type ReactNode } from 'react';

/**
 * Si un microfrontend no carga (su servidor está caído o falla), solo esa parte muestra el error:
 * el shell y los demás microfrontends siguen funcionando (aislamiento de fallos).
 */
export class LimiteErrores extends Component<{ nombre: string; puerto: number; children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };

  static getDerivedStateFromError(error: Error) {
    return { error };
  }

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div className="sh-caido">
        <h2>El microfrontend «{this.props.nombre}» no está disponible</h2>
        <p>Verifique que esté corriendo en <code>http://localhost:{this.props.puerto}</code>. El resto de la aplicación sigue funcionando.</p>
        <p className="sh-detalle">{this.state.error.message}</p>
        <button onClick={() => location.reload()}>Reintentar</button>
      </div>
    );
  }
}
