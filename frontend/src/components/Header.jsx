export default function Header() {
  return (
    <header className="topbar">
      <a className="brand" href="#inicio" aria-label="IASTECH">
        <img src="/iastech-logo.png" alt="IASTECH Industrial Automation" />
      </a>
      <nav className="nav-links" aria-label="Navegação principal">
        <a href="#inicio">Início</a>
        <a href="#analise">Análise P&amp;ID</a>
      </nav>
    </header>
  );
}
