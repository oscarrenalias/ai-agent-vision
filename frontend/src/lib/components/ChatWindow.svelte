<script>
  import { onMount, createEventDispatcher } from 'svelte';

  export let receiptData = null;
  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let messages = [
    {
      role: 'system',
      content: receiptData
        ? 'Hello! I can help you analyze your receipt and provide insights. What would you like to know?'
        : 'Please upload and process a receipt first to get personalized insights.',
    },
  ];

  let newMessage = '';
  let chatContainer;
  let messageInput;

  function handleClose() {
    dispatch('close');
  }

  function handleSubmit() {
    if (!newMessage.trim()) return;

    // Add user message
    messages = [
      ...messages,
      {
        role: 'user',
        content: newMessage,
      },
    ];

    // Clear input
    newMessage = '';

    // In the future, this is where we'd send the message to the backend
    // For now, just simulate a response after a short delay
    setTimeout(() => {
      let responseMessage =
        "I'm just a placeholder response for now. Backend integration will be added later.";

      // If we have receipt data, make the response more contextual
      if (receiptData) {
        const store = receiptData.receipt_data?.place || 'the store';
        const total = receiptData.receipt_data?.total || 0;
        responseMessage = `I see you spent €${total.toFixed(
          2
        )} at ${store}. I'll be able to provide more insights once the backend is connected!`;
      }

      messages = [
        ...messages,
        {
          role: 'system',
          content: responseMessage,
        },
      ];
    }, 1000);
  }

  // Auto-scroll to bottom when messages change
  $: if (chatContainer && messages) {
    setTimeout(() => {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 0);
  }

  // Focus input when chat opens
  $: if (isOpen && messageInput) {
    setTimeout(() => {
      messageInput.focus();
    }, 100);
  }

  // Update welcome message when receipt data changes
  $: if (receiptData && messages.length === 1) {
    messages = [
      {
        role: 'system',
        content:
          'Hello! I can help you analyze your receipt and provide insights. What would you like to know?',
      },
    ];
  }
</script>

<div class="chat-window" class:open={isOpen}>
  <div class="chat-header">
    <h3>Receipt Insights</h3>
    <button class="close-button" on:click={handleClose}>×</button>
  </div>

  <div class="chat-messages" bind:this={chatContainer}>
    {#each messages as message}
      <div class="message {message.role}">
        <div class="message-content">
          {message.content}
        </div>
      </div>
    {/each}
  </div>

  <form class="chat-input" on:submit|preventDefault={handleSubmit}>
    <input
      type="text"
      bind:value={newMessage}
      bind:this={messageInput}
      placeholder="Ask about your receipt..."
      disabled={!receiptData}
    />
    <button type="submit" disabled={!newMessage.trim() || !receiptData}>
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
        <line x1="22" y1="2" x2="11" y2="13" />
        <polygon points="22 2 15 22 11 13 2 9 22 2" />
      </svg>
    </button>
  </form>
</div>

<style>
  .chat-window {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 380px;
    height: 500px;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    z-index: 1000;
    transform: translateY(calc(100% + 20px));
    opacity: 0;
    transition: transform 0.3s ease, opacity 0.3s ease;
    overflow: hidden;
  }

  .chat-window.open {
    transform: translateY(0);
    opacity: 1;
  }

  .chat-header {
    padding: 15px 20px;
    background-color: var(--color-accent, #4caf50);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
  }

  .chat-header h3 {
    margin: 0;
    font-size: 1.1rem;
  }

  .close-button {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 50%;
  }

  .close-button:hover {
    background-color: rgba(255, 255, 255, 0.2);
  }

  .chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .message {
    max-width: 80%;
    padding: 10px 15px;
    border-radius: 18px;
    margin-bottom: 5px;
    word-break: break-word;
  }

  .message.user {
    align-self: flex-end;
    background-color: var(--color-accent, #4caf50);
    color: white;
    border-bottom-right-radius: 5px;
  }

  .message.system {
    align-self: flex-start;
    background-color: #f0f0f0;
    color: #333;
    border-bottom-left-radius: 5px;
  }

  .chat-input {
    display: flex;
    padding: 15px;
    border-top: 1px solid #eee;
  }

  .chat-input input {
    flex: 1;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 25px;
    outline: none;
    font-size: 1rem;
  }

  .chat-input input:focus {
    border-color: var(--color-accent, #4caf50);
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
  }

  .chat-input input:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
  }

  .chat-input button {
    background-color: var(--color-accent, #4caf50);
    color: white;
    border: none;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    margin-left: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
  }

  .chat-input button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }

  .chat-input button svg {
    width: 18px;
    height: 18px;
  }
</style>
