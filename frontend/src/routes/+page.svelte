<script>
  // Home page component
</script>

<svelte:head>
  <title>AI Agent Vision - Home</title>
</svelte:head>

<div class="container">
  <section class="hero">
    <h1>AI Receipt Analysis</h1>
    <p>Upload your receipts and get detailed analysis using AI vision capabilities</p>
    <a href="/receipts" class="cta-button">Get Started</a>
  </section>

  <section class="features">
    <div class="feature-card">
      <h2>Receipt Analysis</h2>
      <p>Extract detailed information from your receipts including items, prices, and totals.</p>
    </div>
    
    <div class="feature-card">
      <h2>Item Classification</h2>
      <p>Automatically categorize items from your receipts for better expense tracking.</p>
    </div>
    
    <div class="feature-card">
      <h2>Data Storage</h2>
      <p>Save and retrieve your receipt data for future reference and analysis.</p>
    </div>
  </section>
</div>

<style>
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  .hero {
    text-align: center;
    margin-bottom: 3rem;
    padding: 3rem 1rem;
    background-color: var(--color-bg-1);
    border-radius: 8px;
  }

  .hero h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
  }

  .hero p {
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto 2rem;
  }

  .cta-button {
    display: inline-block;
    background-color: var(--color-accent);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    font-weight: 600;
    text-decoration: none;
  }

  .cta-button:hover {
    opacity: 0.9;
    text-decoration: none;
  }

  .features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
  }

  .feature-card {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .feature-card h2 {
    margin-bottom: 1rem;
    color: var(--color-accent);
  }
</style>
