<script>
  import '../app.css';
</script>

<div class="app">
  <header>
    <h1>AI Agent Vision</h1>
    <nav>
      <a href="/">Home</a>
      <a href="/receipts">Receipts</a>
    </nav>
  </header>

  <main>
    <slot />
  </main>

  <footer>
    <p>© 2025 AI Agent Vision</p>
  </footer>
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  header {
    background-color: #333;
    color: white;
    padding: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  nav {
    display: flex;
    gap: 1rem;
  }

  nav a {
    color: white;
    text-decoration: none;
  }

  nav a:hover {
    text-decoration: underline;
  }

  main {
    flex: 1;
    padding: 1rem;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
  }

  footer {
    background-color: #333;
    color: white;
    padding: 1rem;
    text-align: center;
  }
</style>
