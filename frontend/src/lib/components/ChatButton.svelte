<script>
  export let onClick = () => {};
</script>

<button class="chat-button" on:click={onClick} aria-label="Open chat">
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </svg>
  <span>Ask about receipts</span>
</button>

<style>
  .chat-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: var(--color-accent, #4caf50);
    color: white;
    border: none;
    border-radius: 25px;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    z-index: 900;
  }

  .chat-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }

  .chat-button svg {
    width: 20px;
    height: 20px;
  }
</style>
