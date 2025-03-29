<script>
  export let size = '60px';
  export let color = '#4caf50';
  export let message = 'Processing...';
</script>

<div class="spinner-container">
  <div
    class="spinner"
    style="width: {size}; height: {size}; border-color: {color} transparent transparent transparent;"
  />
  {#if message}
    <p class="message">{message}</p>
  {/if}
</div>

<style>
  .spinner-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
  }

  .spinner {
    display: inline-block;
    position: relative;
    width: 60px;
    height: 60px;
  }

  .spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top-color: #4caf50;
    animation: spin 1s ease-in-out infinite;
  }

  .message {
    margin-top: 1rem;
    font-size: 1.1rem;
    color: #555;
    text-align: center;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
