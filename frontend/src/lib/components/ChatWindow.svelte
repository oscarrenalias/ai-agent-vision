<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { chatSessionId, setChatSessionId } from '$lib/stores/chatStore';

  export let receiptData = null;
  export let isOpen = false;

  const dispatch = createEventDispatcher();

  let messages = [
    {
      role: 'system',
      content: receiptData
        ? 'Hello! I can help you analyze your receipt and provide insights. What would you like to know?'
        : 'Hello! I can help you with questions about your receipts and shopping history. What would you like to know?',
    },
  ];

  let newMessage = '';
  let chatContainer;
  let messageInput;
  let isLoading = false;
  let error = null;

  // Function to scroll to bottom of chat
  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  // Load chat history when session ID changes or component mounts
  async function loadChatHistory() {
    if (!$chatSessionId) return;

    try {
      const response = await fetch(`/api/chat/history/${$chatSessionId}`);
      if (response.ok) {
        const history = await response.json();

        // Start with welcome message
        const welcomeMessage = {
          role: 'system',
          content: receiptData
            ? 'Hello! I can help you analyze your receipt and provide insights. What would you like to know?'
            : 'Hello! I can help you with questions about your receipts and shopping history. What would you like to know?',
        };

        // Add all messages from history
        messages = [welcomeMessage, ...history];

        // Scroll to bottom after loading history
        setTimeout(scrollToBottom, 100);
      }
    } catch (e) {
      console.error('Error loading chat history:', e);
    }
  }

  onMount(() => {
    // Initial scroll to bottom when component mounts
    scrollToBottom();

    // Load chat history if we have a session ID
    if ($chatSessionId) {
      loadChatHistory();
    }
  });

  // Watch for changes to chatSessionId
  $: if ($chatSessionId) {
    loadChatHistory();
  }

  function handleClose() {
    dispatch('close');
  }

  async function handleSubmit() {
    if (!newMessage.trim() || isLoading) return;

    // Add user message to UI immediately
    messages = [
      ...messages,
      {
        role: 'user',
        content: newMessage,
      },
    ];

    const messageToSend = newMessage;
    newMessage = ''; // Clear input
    isLoading = true;
    error = null;

    // Scroll to bottom after adding user message
    setTimeout(scrollToBottom, 50);

    try {
      // Prepare request data
      const requestData = {
        message: messageToSend,
        chat_id: $chatSessionId,
      };

      // Send message to backend
      const response = await fetch('/api/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Store the chat session ID if this is a new session
      if (!$chatSessionId) {
        setChatSessionId(data.chat_id);
      }

      // Update messages with the response
      messages = [
        ...messages, // Keep all previous messages
        {
          role: 'assistant',
          content: data.message,
        },
      ];
    } catch (e) {
      console.error('Error sending message:', e);
      error = e.message;

      // Add error message to chat
      messages = [
        ...messages,
        {
          role: 'system',
          content: `Error: ${error}. Please try again.`,
        },
      ];
    } finally {
      isLoading = false;
      // Scroll to bottom after receiving response
      setTimeout(scrollToBottom, 50);
    }
  }

  // Auto-scroll to bottom when messages change or loading state changes
  $: if (messages || isLoading) {
    setTimeout(scrollToBottom, 100); // Increased timeout to ensure DOM updates
  }

  // Focus input and scroll to bottom when chat opens
  $: if (isOpen) {
    setTimeout(() => {
      if (messageInput) messageInput.focus();
      scrollToBottom();
    }, 300); // Longer timeout to ensure animation completes
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
    {#if isLoading}
      <div class="message system loading">
        <div class="typing-indicator">
          <span />
          <span />
          <span />
        </div>
      </div>
    {/if}
  </div>

  <form class="chat-input" on:submit|preventDefault={handleSubmit}>
    <input
      type="text"
      bind:value={newMessage}
      bind:this={messageInput}
      placeholder="Ask about your receipts..."
      disabled={isLoading}
    />
    <button type="submit" disabled={!newMessage.trim() || isLoading}>
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
    scroll-behavior: smooth;
    max-height: calc(100% - 120px); /* Account for header and input area */
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

  .message.system,
  .message.assistant {
    align-self: flex-start;
    background-color: #f0f0f0;
    color: #333;
    border-bottom-left-radius: 5px;
  }

  .message.loading {
    padding: 10px;
  }

  .typing-indicator {
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .typing-indicator span {
    width: 8px;
    height: 8px;
    background-color: #999;
    border-radius: 50%;
    display: inline-block;
    animation: bounce 1.5s infinite ease-in-out;
  }

  .typing-indicator span:nth-child(1) {
    animation-delay: 0s;
  }

  .typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes bounce {
    0%,
    60%,
    100% {
      transform: translateY(0);
    }
    30% {
      transform: translateY(-5px);
    }
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

  .chat-input input:disabled {
    background-color: #f5f5f5;
    cursor: not-allowed;
  }

  .chat-input input:focus {
    border-color: var(--color-accent, #4caf50);
    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
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
