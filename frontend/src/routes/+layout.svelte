<script>
  import '../app.css';
</script>

<div class="app">
  <header>
    <div class="container">
      <div class="logo">
        <a href="/">AI Agent Vision</a>
      </div>
      <nav>
        <ul>
          <li><a href="/">Home</a></li>
          <li><a href="/receipts">Upload Receipt</a></li>
          <li><a href="/receipts/history">Receipt History</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main>
    <slot />
  </main>

  <footer>
    <div class="container">
      <p>&copy; 2025 AI Agent Vision</p>
    </div>
  </footer>
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  header {
    background-color: var(--color-bg-1);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .logo a {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--color-accent);
    text-decoration: none;
  }

  nav ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 1.5rem;
  }

  nav a {
    color: var(--color-text);
    text-decoration: none;
    font-weight: 500;
  }

  nav a:hover {
    color: var(--color-accent);
  }

  main {
    flex: 1;
  }

  footer {
    background-color: var(--color-bg-1);
    padding: 1rem 0;
    text-align: center;
    margin-top: 2rem;
  }

  footer .container {
    max-width: 1200px;
    margin: 0 auto;
  }
</style>
