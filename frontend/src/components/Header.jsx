export default function Header() {
  return (
    <header className="topbar" role="banner">
      <div className="brand-group">
        <a className="brand" href="#inicio" aria-label="IASTECH Automação Industrial">
          <img src="/iastech-logo.png" alt="IASTECH" />
        </a>
        <span className="brand-divider" aria-hidden="true">/</span>
        <span className="app-badge">TAGVision P&amp;ID <span className="version-tag">v1.0</span></span>
      </div>
      <nav className="nav-links" aria-label="Navegação principal">
        <a href="#inicio">Início</a>
        <a href="#analise">Análise de Planta</a>
      </nav>
    </header>
  );
}
