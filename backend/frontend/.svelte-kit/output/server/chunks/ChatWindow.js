import { c as create_ssr_component, a as subscribe, b as createEventDispatcher, d as add_attribute, f as each, e as escape } from "./ssr.js";
import { w as writable } from "./index.js";
import { marked } from "marked";
import DOMPurify from "dompurify";
const isChatOpen = writable(false);
const currentReceiptData = writable(null);
const chatSessionId = writable(null);
function openChat() {
  isChatOpen.set(true);
}
marked.setOptions({
  breaks: true,
  // Add line breaks on single line breaks
  gfm: true,
  // Use GitHub Flavored Markdown
  headerIds: false,
  // Don't add IDs to headers (for security)
  mangle: false,
  // Don't mangle email addresses
  sanitize: false
  // Don't sanitize (we'll handle this with DOMPurify)
});
function renderMarkdown(markdown) {
  if (!markdown) return "";
  try {
    const html = marked.parse(markdown);
    const sanitizedHtml = DOMPurify.sanitize(html, {
      USE_PROFILES: { html: true },
      ALLOWED_TAGS: [
        "a",
        "b",
        "blockquote",
        "br",
        "code",
        "div",
        "em",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hr",
        "i",
        "li",
        "ol",
        "p",
        "pre",
        "span",
        "strong",
        "table",
        "tbody",
        "td",
        "th",
        "thead",
        "tr",
        "ul"
      ],
      ALLOWED_ATTR: ["href", "target", "rel", "class"]
    });
    return sanitizedHtml;
  } catch (error) {
    console.error("Error rendering markdown:", error);
    return markdown;
  }
}
const css = {
  code: ".chat-window.svelte-22ln21.svelte-22ln21{position:fixed;bottom:20px;right:20px;width:380px;height:500px;background-color:white;border-radius:12px;box-shadow:0 5px 20px rgba(0, 0, 0, 0.2);display:flex;flex-direction:column;z-index:1000;transform:translateY(calc(100% + 20px));opacity:0;transition:transform 0.3s ease, opacity 0.3s ease;overflow:hidden}.chat-window.open.svelte-22ln21.svelte-22ln21{transform:translateY(0);opacity:1}.chat-header.svelte-22ln21.svelte-22ln21{padding:15px 20px;background-color:var(--color-accent, #4caf50);color:white;display:flex;justify-content:space-between;align-items:center;border-top-left-radius:12px;border-top-right-radius:12px}.chat-header.svelte-22ln21 h3.svelte-22ln21{margin:0;font-size:1.1rem}.close-button.svelte-22ln21.svelte-22ln21{background:none;border:none;color:white;font-size:1.5rem;cursor:pointer;padding:0;display:flex;align-items:center;justify-content:center;width:30px;height:30px;border-radius:50%}.close-button.svelte-22ln21.svelte-22ln21:hover{background-color:rgba(255, 255, 255, 0.2)}.chat-messages.svelte-22ln21.svelte-22ln21{flex:1;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:10px;scroll-behavior:smooth;max-height:calc(100% - 120px)}.message.svelte-22ln21.svelte-22ln21{max-width:80%;padding:10px 15px;border-radius:18px;margin-bottom:5px;word-break:break-word}.message.user.svelte-22ln21.svelte-22ln21{align-self:flex-end;background-color:var(--color-accent, #4caf50);color:white;border-bottom-right-radius:5px}.message.system.svelte-22ln21.svelte-22ln21,.message.assistant.svelte-22ln21.svelte-22ln21{align-self:flex-start;background-color:#f0f0f0;color:#333;border-bottom-left-radius:5px}.message.loading.svelte-22ln21.svelte-22ln21{padding:10px}.message-content.svelte-22ln21 p{margin:0 0 0.75em 0}.message-content.svelte-22ln21 p:last-child{margin-bottom:0}.message-content.svelte-22ln21 pre{background-color:rgba(0, 0, 0, 0.05);padding:0.5em;border-radius:4px;overflow-x:auto;margin:0.5em 0}.message-content.svelte-22ln21 code{font-family:'Courier New', Courier, monospace;background-color:rgba(0, 0, 0, 0.05);padding:0.2em 0.4em;border-radius:3px;font-size:0.9em}.message-content.svelte-22ln21 pre code{background-color:transparent;padding:0}.message-content.svelte-22ln21 ul,.message-content.svelte-22ln21 ol{margin:0.5em 0;padding-left:1.5em}.message-content.svelte-22ln21 li{margin-bottom:0.25em}.message-content.svelte-22ln21 h1,.message-content.svelte-22ln21 h2,.message-content.svelte-22ln21 h3,.message-content.svelte-22ln21 h4,.message-content.svelte-22ln21 h5,.message-content.svelte-22ln21 h6{margin:0.5em 0 0.25em 0;font-weight:600}.message-content.svelte-22ln21 h1{font-size:1.4em}.message-content.svelte-22ln21 h2{font-size:1.3em}.message-content.svelte-22ln21 h3{font-size:1.2em}.message-content.svelte-22ln21 h4{font-size:1.1em}.message-content.svelte-22ln21 h5,.message-content.svelte-22ln21 h6{font-size:1em}.message-content.svelte-22ln21 table{border-collapse:collapse;margin:0.5em 0;width:100%}.message-content.svelte-22ln21 th,.message-content.svelte-22ln21 td{border:1px solid #ddd;padding:0.3em 0.5em;text-align:left}.message-content.svelte-22ln21 th{background-color:rgba(0, 0, 0, 0.05)}.message-content.svelte-22ln21 a{color:#2563eb;text-decoration:none}.message-content.svelte-22ln21 a:hover{text-decoration:underline}.message-content.svelte-22ln21 blockquote{border-left:3px solid #ddd;margin:0.5em 0;padding-left:1em;color:#555}.typing-indicator.svelte-22ln21.svelte-22ln21{display:flex;align-items:center;gap:5px}.typing-indicator.svelte-22ln21 span.svelte-22ln21{width:8px;height:8px;background-color:#999;border-radius:50%;display:inline-block;animation:svelte-22ln21-bounce 1.5s infinite ease-in-out}.typing-indicator.svelte-22ln21 span.svelte-22ln21:nth-child(1){animation-delay:0s}.typing-indicator.svelte-22ln21 span.svelte-22ln21:nth-child(2){animation-delay:0.2s}.typing-indicator.svelte-22ln21 span.svelte-22ln21:nth-child(3){animation-delay:0.4s}@keyframes svelte-22ln21-bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-5px)}}.chat-input.svelte-22ln21.svelte-22ln21{display:flex;padding:15px;border-top:1px solid #eee}.chat-input.svelte-22ln21 input.svelte-22ln21{flex:1;padding:12px 15px;border:1px solid #ddd;border-radius:25px;outline:none;font-size:1rem}.chat-input.svelte-22ln21 input.svelte-22ln21:disabled{background-color:#f5f5f5;cursor:not-allowed}.chat-input.svelte-22ln21 input.svelte-22ln21:focus{border-color:var(--color-accent, #4caf50);box-shadow:0 0 0 2px rgba(76, 175, 80, 0.2)}.chat-input.svelte-22ln21 button.svelte-22ln21{background-color:var(--color-accent, #4caf50);color:white;border:none;width:40px;height:40px;border-radius:50%;margin-left:10px;cursor:pointer;display:flex;align-items:center;justify-content:center;padding:0}.chat-input.svelte-22ln21 button.svelte-22ln21:disabled{background-color:#ccc;cursor:not-allowed}.chat-input.svelte-22ln21 button svg.svelte-22ln21{width:18px;height:18px}",
  map: `{"version":3,"file":"ChatWindow.svelte","sources":["ChatWindow.svelte"],"sourcesContent":["<script>\\n  import { onMount, createEventDispatcher } from 'svelte';\\n  import { chatSessionId, setChatSessionId } from '$lib/stores/chatStore';\\n  import { renderMarkdown } from '$lib/utils/markdown';\\n\\n  export let receiptData = null;\\n  export let isOpen = false;\\n\\n  const dispatch = createEventDispatcher();\\n\\n  let messages = [\\n    {\\n      role: 'system',\\n      content: receiptData\\n        ? 'Hello! I can help you analyze your receipt and provide insights. What would you like to know?'\\n        : 'Hello! I can help you with questions about your receipts and shopping history. What would you like to know?',\\n    },\\n  ];\\n\\n  let newMessage = '';\\n  let chatContainer;\\n  let messageInput;\\n  let isLoading = false;\\n  let error = null;\\n\\n  // Function to scroll to bottom of chat\\n  function scrollToBottom() {\\n    if (chatContainer) {\\n      chatContainer.scrollTop = chatContainer.scrollHeight;\\n    }\\n  }\\n\\n  // Load chat history when session ID changes or component mounts\\n  async function loadChatHistory() {\\n    if (!$chatSessionId) return;\\n\\n    try {\\n      const response = await fetch(\`/api/chat/history/\${$chatSessionId}\`);\\n      if (response.ok) {\\n        const history = await response.json();\\n\\n        // Start with welcome message\\n        const welcomeMessage = {\\n          role: 'system',\\n          content: receiptData\\n            ? 'Hello! I can help you analyze your receipt and provide insights. What would you like to know?'\\n            : 'Hello! I can help you with questions about your receipts and shopping history. What would you like to know?',\\n        };\\n\\n        // Add all messages from history\\n        messages = [welcomeMessage, ...history];\\n\\n        // Scroll to bottom after loading history\\n        setTimeout(scrollToBottom, 100);\\n      }\\n    } catch (e) {\\n      console.error('Error loading chat history:', e);\\n    }\\n  }\\n\\n  onMount(() => {\\n    // Initial scroll to bottom when component mounts\\n    scrollToBottom();\\n\\n    // Load chat history if we have a session ID\\n    if ($chatSessionId) {\\n      loadChatHistory();\\n    }\\n  });\\n\\n  // Watch for changes to chatSessionId\\n  $: if ($chatSessionId) {\\n    loadChatHistory();\\n  }\\n\\n  function handleClose() {\\n    dispatch('close');\\n  }\\n\\n  async function handleSubmit() {\\n    if (!newMessage.trim() || isLoading) return;\\n\\n    // Add user message to UI immediately\\n    messages = [\\n      ...messages,\\n      {\\n        role: 'user',\\n        content: newMessage,\\n      },\\n    ];\\n\\n    const messageToSend = newMessage;\\n    newMessage = ''; // Clear input\\n    isLoading = true;\\n    error = null;\\n\\n    // Scroll to bottom after adding user message\\n    setTimeout(scrollToBottom, 50);\\n\\n    try {\\n      // Prepare request data\\n      const requestData = {\\n        message: messageToSend,\\n        chat_id: $chatSessionId,\\n      };\\n\\n      // Send message to backend\\n      const response = await fetch('/api/chat/send', {\\n        method: 'POST',\\n        headers: {\\n          'Content-Type': 'application/json',\\n        },\\n        body: JSON.stringify(requestData),\\n      });\\n\\n      if (!response.ok) {\\n        throw new Error(\`Server responded with \${response.status}: \${response.statusText}\`);\\n      }\\n\\n      const data = await response.json();\\n\\n      // Store the chat session ID if this is a new session\\n      if (!$chatSessionId) {\\n        setChatSessionId(data.chat_id);\\n      }\\n\\n      // Update messages with the response\\n      messages = [\\n        ...messages, // Keep all previous messages\\n        {\\n          role: 'assistant',\\n          content: data.message,\\n        },\\n      ];\\n    } catch (e) {\\n      console.error('Error sending message:', e);\\n      error = e.message;\\n\\n      // Add error message to chat\\n      messages = [\\n        ...messages,\\n        {\\n          role: 'system',\\n          content: \`Error: \${error}. Please try again.\`,\\n        },\\n      ];\\n    } finally {\\n      isLoading = false;\\n      // Scroll to bottom after receiving response\\n      setTimeout(scrollToBottom, 50);\\n    }\\n  }\\n\\n  // Auto-scroll to bottom when messages change or loading state changes\\n  $: if (messages || isLoading) {\\n    setTimeout(scrollToBottom, 100); // Increased timeout to ensure DOM updates\\n  }\\n\\n  // Focus input and scroll to bottom when chat opens\\n  $: if (isOpen) {\\n    setTimeout(() => {\\n      if (messageInput) messageInput.focus();\\n      scrollToBottom();\\n    }, 300); // Longer timeout to ensure animation completes\\n  }\\n\\n  // Update welcome message when receipt data changes\\n  $: if (receiptData && messages.length === 1) {\\n    messages = [\\n      {\\n        role: 'system',\\n        content:\\n          'Hello! I can help you analyze your receipt and provide insights. What would you like to know?',\\n      },\\n    ];\\n  }\\n<\/script>\\n\\n<div class=\\"chat-window\\" class:open={isOpen}>\\n  <div class=\\"chat-header\\">\\n    <h3>Receipt Insights</h3>\\n    <button class=\\"close-button\\" on:click={handleClose}>×</button>\\n  </div>\\n\\n  <div class=\\"chat-messages\\" bind:this={chatContainer}>\\n    {#each messages as message}\\n      <div class=\\"message {message.role}\\">\\n        <div class=\\"message-content\\">\\n          {#if message.role === 'assistant' || message.role === 'system'}\\n            {@html renderMarkdown(message.content)}\\n          {:else}\\n            {message.content}\\n          {/if}\\n        </div>\\n      </div>\\n    {/each}\\n    {#if isLoading}\\n      <div class=\\"message system loading\\">\\n        <div class=\\"typing-indicator\\">\\n          <span />\\n          <span />\\n          <span />\\n        </div>\\n      </div>\\n    {/if}\\n  </div>\\n\\n  <form class=\\"chat-input\\" on:submit|preventDefault={handleSubmit}>\\n    <input\\n      type=\\"text\\"\\n      bind:value={newMessage}\\n      bind:this={messageInput}\\n      placeholder=\\"Ask about your receipts...\\"\\n      disabled={isLoading}\\n    />\\n    <button type=\\"submit\\" disabled={!newMessage.trim() || isLoading}>\\n      <svg\\n        xmlns=\\"http://www.w3.org/2000/svg\\"\\n        width=\\"24\\"\\n        height=\\"24\\"\\n        viewBox=\\"0 0 24 24\\"\\n        fill=\\"none\\"\\n        stroke=\\"currentColor\\"\\n        stroke-width=\\"2\\"\\n        stroke-linecap=\\"round\\"\\n        stroke-linejoin=\\"round\\"\\n      >\\n        <line x1=\\"22\\" y1=\\"2\\" x2=\\"11\\" y2=\\"13\\" />\\n        <polygon points=\\"22 2 15 22 11 13 2 9 22 2\\" />\\n      </svg>\\n    </button>\\n  </form>\\n</div>\\n\\n<style>\\n  .chat-window {\\n    position: fixed;\\n    bottom: 20px;\\n    right: 20px;\\n    width: 380px;\\n    height: 500px;\\n    background-color: white;\\n    border-radius: 12px;\\n    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);\\n    display: flex;\\n    flex-direction: column;\\n    z-index: 1000;\\n    transform: translateY(calc(100% + 20px));\\n    opacity: 0;\\n    transition: transform 0.3s ease, opacity 0.3s ease;\\n    overflow: hidden;\\n  }\\n\\n  .chat-window.open {\\n    transform: translateY(0);\\n    opacity: 1;\\n  }\\n\\n  .chat-header {\\n    padding: 15px 20px;\\n    background-color: var(--color-accent, #4caf50);\\n    color: white;\\n    display: flex;\\n    justify-content: space-between;\\n    align-items: center;\\n    border-top-left-radius: 12px;\\n    border-top-right-radius: 12px;\\n  }\\n\\n  .chat-header h3 {\\n    margin: 0;\\n    font-size: 1.1rem;\\n  }\\n\\n  .close-button {\\n    background: none;\\n    border: none;\\n    color: white;\\n    font-size: 1.5rem;\\n    cursor: pointer;\\n    padding: 0;\\n    display: flex;\\n    align-items: center;\\n    justify-content: center;\\n    width: 30px;\\n    height: 30px;\\n    border-radius: 50%;\\n  }\\n\\n  .close-button:hover {\\n    background-color: rgba(255, 255, 255, 0.2);\\n  }\\n\\n  .chat-messages {\\n    flex: 1;\\n    overflow-y: auto;\\n    padding: 15px;\\n    display: flex;\\n    flex-direction: column;\\n    gap: 10px;\\n    scroll-behavior: smooth;\\n    max-height: calc(100% - 120px); /* Account for header and input area */\\n  }\\n\\n  .message {\\n    max-width: 80%;\\n    padding: 10px 15px;\\n    border-radius: 18px;\\n    margin-bottom: 5px;\\n    word-break: break-word;\\n  }\\n\\n  .message.user {\\n    align-self: flex-end;\\n    background-color: var(--color-accent, #4caf50);\\n    color: white;\\n    border-bottom-right-radius: 5px;\\n  }\\n\\n  .message.system,\\n  .message.assistant {\\n    align-self: flex-start;\\n    background-color: #f0f0f0;\\n    color: #333;\\n    border-bottom-left-radius: 5px;\\n  }\\n\\n  .message.loading {\\n    padding: 10px;\\n  }\\n\\n  /* Markdown styling */\\n  .message-content :global(p) {\\n    margin: 0 0 0.75em 0;\\n  }\\n\\n  .message-content :global(p:last-child) {\\n    margin-bottom: 0;\\n  }\\n\\n  .message-content :global(pre) {\\n    background-color: rgba(0, 0, 0, 0.05);\\n    padding: 0.5em;\\n    border-radius: 4px;\\n    overflow-x: auto;\\n    margin: 0.5em 0;\\n  }\\n\\n  .message-content :global(code) {\\n    font-family: 'Courier New', Courier, monospace;\\n    background-color: rgba(0, 0, 0, 0.05);\\n    padding: 0.2em 0.4em;\\n    border-radius: 3px;\\n    font-size: 0.9em;\\n  }\\n\\n  .message-content :global(pre code) {\\n    background-color: transparent;\\n    padding: 0;\\n  }\\n\\n  .message-content :global(ul),\\n  .message-content :global(ol) {\\n    margin: 0.5em 0;\\n    padding-left: 1.5em;\\n  }\\n\\n  .message-content :global(li) {\\n    margin-bottom: 0.25em;\\n  }\\n\\n  .message-content :global(h1),\\n  .message-content :global(h2),\\n  .message-content :global(h3),\\n  .message-content :global(h4),\\n  .message-content :global(h5),\\n  .message-content :global(h6) {\\n    margin: 0.5em 0 0.25em 0;\\n    font-weight: 600;\\n  }\\n\\n  .message-content :global(h1) {\\n    font-size: 1.4em;\\n  }\\n  .message-content :global(h2) {\\n    font-size: 1.3em;\\n  }\\n  .message-content :global(h3) {\\n    font-size: 1.2em;\\n  }\\n  .message-content :global(h4) {\\n    font-size: 1.1em;\\n  }\\n  .message-content :global(h5),\\n  .message-content :global(h6) {\\n    font-size: 1em;\\n  }\\n\\n  .message-content :global(table) {\\n    border-collapse: collapse;\\n    margin: 0.5em 0;\\n    width: 100%;\\n  }\\n\\n  .message-content :global(th),\\n  .message-content :global(td) {\\n    border: 1px solid #ddd;\\n    padding: 0.3em 0.5em;\\n    text-align: left;\\n  }\\n\\n  .message-content :global(th) {\\n    background-color: rgba(0, 0, 0, 0.05);\\n  }\\n\\n  .message-content :global(a) {\\n    color: #2563eb;\\n    text-decoration: none;\\n  }\\n\\n  .message-content :global(a:hover) {\\n    text-decoration: underline;\\n  }\\n\\n  .message-content :global(blockquote) {\\n    border-left: 3px solid #ddd;\\n    margin: 0.5em 0;\\n    padding-left: 1em;\\n    color: #555;\\n  }\\n\\n  .typing-indicator {\\n    display: flex;\\n    align-items: center;\\n    gap: 5px;\\n  }\\n\\n  .typing-indicator span {\\n    width: 8px;\\n    height: 8px;\\n    background-color: #999;\\n    border-radius: 50%;\\n    display: inline-block;\\n    animation: bounce 1.5s infinite ease-in-out;\\n  }\\n\\n  .typing-indicator span:nth-child(1) {\\n    animation-delay: 0s;\\n  }\\n\\n  .typing-indicator span:nth-child(2) {\\n    animation-delay: 0.2s;\\n  }\\n\\n  .typing-indicator span:nth-child(3) {\\n    animation-delay: 0.4s;\\n  }\\n\\n  @keyframes bounce {\\n    0%,\\n    60%,\\n    100% {\\n      transform: translateY(0);\\n    }\\n    30% {\\n      transform: translateY(-5px);\\n    }\\n  }\\n\\n  .chat-input {\\n    display: flex;\\n    padding: 15px;\\n    border-top: 1px solid #eee;\\n  }\\n\\n  .chat-input input {\\n    flex: 1;\\n    padding: 12px 15px;\\n    border: 1px solid #ddd;\\n    border-radius: 25px;\\n    outline: none;\\n    font-size: 1rem;\\n  }\\n\\n  .chat-input input:disabled {\\n    background-color: #f5f5f5;\\n    cursor: not-allowed;\\n  }\\n\\n  .chat-input input:focus {\\n    border-color: var(--color-accent, #4caf50);\\n    box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);\\n  }\\n\\n  .chat-input button {\\n    background-color: var(--color-accent, #4caf50);\\n    color: white;\\n    border: none;\\n    width: 40px;\\n    height: 40px;\\n    border-radius: 50%;\\n    margin-left: 10px;\\n    cursor: pointer;\\n    display: flex;\\n    align-items: center;\\n    justify-content: center;\\n    padding: 0;\\n  }\\n\\n  .chat-input button:disabled {\\n    background-color: #ccc;\\n    cursor: not-allowed;\\n  }\\n\\n  .chat-input button svg {\\n    width: 18px;\\n    height: 18px;\\n  }\\n</style>\\n"],"names":[],"mappings":"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"}`
};
const ChatWindow = create_ssr_component(($$result, $$props, $$bindings, slots) => {
  let $chatSessionId, $$unsubscribe_chatSessionId;
  $$unsubscribe_chatSessionId = subscribe(chatSessionId, (value) => $chatSessionId = value);
  let { receiptData = null } = $$props;
  let { isOpen = false } = $$props;
  createEventDispatcher();
  let messages = [
    {
      role: "system",
      content: receiptData ? "Hello! I can help you analyze your receipt and provide insights. What would you like to know?" : "Hello! I can help you with questions about your receipts and shopping history. What would you like to know?"
    }
  ];
  let newMessage = "";
  let chatContainer;
  let messageInput;
  let isLoading = false;
  function scrollToBottom() {
  }
  async function loadChatHistory() {
    if (!$chatSessionId) return;
    try {
      const response = await fetch(`/api/chat/history/${$chatSessionId}`);
      if (response.ok) {
        const history = await response.json();
        const welcomeMessage = {
          role: "system",
          content: receiptData ? "Hello! I can help you analyze your receipt and provide insights. What would you like to know?" : "Hello! I can help you with questions about your receipts and shopping history. What would you like to know?"
        };
        messages = [welcomeMessage, ...history];
        setTimeout(scrollToBottom, 100);
      }
    } catch (e) {
      console.error("Error loading chat history:", e);
    }
  }
  if ($$props.receiptData === void 0 && $$bindings.receiptData && receiptData !== void 0) $$bindings.receiptData(receiptData);
  if ($$props.isOpen === void 0 && $$bindings.isOpen && isOpen !== void 0) $$bindings.isOpen(isOpen);
  $$result.css.add(css);
  {
    if ($chatSessionId) {
      loadChatHistory();
    }
  }
  {
    if (receiptData && messages.length === 1) {
      messages = [
        {
          role: "system",
          content: "Hello! I can help you analyze your receipt and provide insights. What would you like to know?"
        }
      ];
    }
  }
  {
    if (messages || isLoading) {
      setTimeout(scrollToBottom, 100);
    }
  }
  {
    if (isOpen) {
      setTimeout(
        () => {
        },
        300
      );
    }
  }
  $$unsubscribe_chatSessionId();
  return `<div class="${["chat-window svelte-22ln21", isOpen ? "open" : ""].join(" ").trim()}"><div class="chat-header svelte-22ln21"><h3 class="svelte-22ln21" data-svelte-h="svelte-9fjne9">Receipt Insights</h3> <button class="close-button svelte-22ln21" data-svelte-h="svelte-1fbk8id">×</button></div> <div class="chat-messages svelte-22ln21"${add_attribute("this", chatContainer, 0)}>${each(messages, (message) => {
    return `<div class="${"message " + escape(message.role, true) + " svelte-22ln21"}"><div class="message-content svelte-22ln21">${message.role === "assistant" || message.role === "system" ? `<!-- HTML_TAG_START -->${renderMarkdown(message.content)}<!-- HTML_TAG_END -->` : `${escape(message.content)}`}</div> </div>`;
  })} ${``}</div> <form class="chat-input svelte-22ln21"><input type="text" placeholder="Ask about your receipts..." ${""} class="svelte-22ln21"${add_attribute("value", newMessage, 0)}${add_attribute("this", messageInput, 0)}> <button type="submit" ${!newMessage.trim() || isLoading ? "disabled" : ""} class="svelte-22ln21"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="svelte-22ln21"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg></button></form> </div>`;
});
export {
  ChatWindow as C,
  currentReceiptData as c,
  isChatOpen as i,
  openChat as o
};
