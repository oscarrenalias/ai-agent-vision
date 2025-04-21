<script>
  export let progress = 0;
  export let message = 'Processing...';
  export let submessage = '';
</script>

<div class="processing-overlay">
  <div class="processing-container">
    <div class="spinner" />
    <h3>{message}</h3>
    {#if submessage}
      <p>{submessage}</p>
    {/if}
    <div class="progress-container">
      <div class="progress-bar" style="width: {progress}%" />
    </div>
    <div class="progress-text">{progress}%</div>
  </div>
</div>

<style>
  .processing-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }

  .processing-container {
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    text-align: center;
    max-width: 90%;
    width: 400px;
  }

  h3 {
    margin: 1rem 0;
    color: #333;
  }

  p {
    margin-bottom: 1.5rem;
    color: #666;
    font-size: 0.9rem;
  }

  .spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 2s linear infinite;
    margin: 0 auto 1rem;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  .progress-container {
    height: 8px;
    background-color: #f3f3f3;
    border-radius: 4px;
    margin: 1rem 0 0.5rem;
    overflow: hidden;
  }

  .progress-bar {
    height: 100%;
    background-color: #4caf50;
    transition: width 0.5s ease;
  }

  .progress-text {
    font-size: 0.9rem;
    color: #666;
    font-weight: 600;
  }
</style>
