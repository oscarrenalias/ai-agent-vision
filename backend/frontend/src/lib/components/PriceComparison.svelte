<script>
  import { onMount } from 'svelte';
  import { renderMarkdown } from '$lib/utils/markdown';
  import LoadingSpinner from './LoadingSpinner.svelte';

  // Props
  export let item = {};
  export let onClose = () => {};

  // State
  let isLoading = false;
  let comparisonResult = null;
  let error = null;

  // Function to fetch price comparison data
  async function fetchPriceComparison() {
    isLoading = true;
    error = null;
    comparisonResult = null;

    try {
      // Get the Finnish item name to compare (Finnish is required for the backend lookup)
      const itemName = item.name_fi || item.name_en || '';

      if (!itemName) {
        throw new Error('No item name available for comparison');
      }

      console.log('Comparing prices for Finnish item name:', itemName);

      // Make API request to backend
      const response = await fetch('/api/price-comparison', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item: itemName }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch price comparison');
      }

      const data = await response.json();
      comparisonResult = data.result;
    } catch (err) {
      console.error('Error fetching price comparison:', err);
      error = err.message || 'Failed to fetch price comparison';
    } finally {
      isLoading = false;
    }
  }

  // Fetch price comparison data when component mounts
  onMount(() => {
    fetchPriceComparison();
  });
</script>

<div class="price-comparison">
  <div class="price-comparison-header">
    <h4>Price Comparison for {item.name_fi || item.name_en || 'Item'}</h4>
    <button class="close-button" on:click={onClose}>×</button>
  </div>

  <div class="price-comparison-content">
    {#if isLoading}
      <div class="loading-container">
        <LoadingSpinner size="40px" message="Searching for better prices..." />
      </div>
    {:else if error}
      <div class="error-message">
        <p>{error}</p>
        <button on:click={fetchPriceComparison} class="retry-button">Retry</button>
      </div>
    {:else if comparisonResult}
      <div class="comparison-results">
        {@html renderMarkdown(comparisonResult)}
      </div>
    {:else}
      <p>No comparison data available.</p>
    {/if}
  </div>
</div>

<style>
  .price-comparison {
    background-color: #f9f9f9;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin: 0.5rem 0 1.5rem;
    overflow: hidden;
  }

  .price-comparison-header {
    background-color: #f0f0f0;
    padding: 0.75rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e0e0e0;
  }

  .price-comparison-header h4 {
    margin: 0;
    font-size: 1rem;
    color: #333;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    color: #666;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    border-radius: 50%;
  }

  .close-button:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }

  .price-comparison-content {
    padding: 1rem;
  }

  .loading-container {
    display: flex;
    justify-content: center;
    padding: 1rem 0;
  }

  .error-message {
    color: #d32f2f;
    padding: 0.75rem;
    background-color: #ffebee;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .retry-button {
    background-color: #d32f2f;
    color: white;
    border: none;
    padding: 0.3rem 0.75rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
  }

  .comparison-results {
    font-size: 0.95rem;
    line-height: 1.5;
  }

  .comparison-results :global(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
    font-size: 0.9rem;
  }

  .comparison-results :global(th),
  .comparison-results :global(td) {
    padding: 0.5rem;
    border: 1px solid #ddd;
    text-align: left;
  }

  .comparison-results :global(th) {
    background-color: #f5f5f5;
    font-weight: 600;
  }

  .comparison-results :global(ul) {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }

  .comparison-results :global(li) {
    margin-bottom: 0.25rem;
  }

  .comparison-results :global(p) {
    margin: 0.5rem 0;
  }

  .comparison-results :global(strong) {
    color: #2e7d32;
  }
</style>
