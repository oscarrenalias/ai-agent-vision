import { writable } from 'svelte/store';

// Store for chat state
export const isChatOpen = writable(false);

// Store for current receipt data (if any)
export const currentReceiptData = writable(null);

// Function to open chat
export function openChat() {
  isChatOpen.set(true);
}

// Function to close chat
export function closeChat() {
  isChatOpen.set(false);
}

// Function to set current receipt data
export function setReceiptData(data) {
  currentReceiptData.set(data);
}
