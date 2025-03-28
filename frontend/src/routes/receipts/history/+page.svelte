<script>
  import { onMount } from 'svelte';

  let receipts = [];
  let isLoading = true;
  let error = null;
  let selectedReceipt = null;

  // Format date string to a more readable format
  function formatDate(dateString) {
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }).format(date);
    } catch (e) {
      return dateString;
    }
  }

  // Calculate total loyalty discount for a receipt
  function calculateTotalDiscount(items) {
    if (!items || !Array.isArray(items)) return 0;

    return items.reduce((total, item) => {
      if (item.has_loyalty_discount && item.loyalty_discount) {
        return total + parseFloat(item.loyalty_discount);
      }
      return total;
    }, 0);
  }

  // Count items with discounts
  function countDiscountedItems(items) {
    if (!items || !Array.isArray(items)) return 0;

    return items.filter((item) => item.has_loyalty_discount).length;
  }

  // Load receipts from the API
  async function loadReceipts() {
    isLoading = true;
    error = null;

    try {
      const response = await fetch('/api/receipts');
      const result = await response.json();

      if (result.status === 'success') {
        receipts = result.receipts;
      } else {
        error = result.error || 'Failed to load receipts';
      }
    } catch (err) {
      error = 'Error loading receipts: ' + err.message;
    } finally {
      isLoading = false;
    }
  }

  // View details of a specific receipt
  function viewReceiptDetails(receipt) {
    selectedReceipt = receipt;
  }

  // Close the receipt details view
  function closeDetails() {
    selectedReceipt = null;
  }

  onMount(() => {
    loadReceipts();
  });
</script>

<svelte:head>
  <title>AI Agent Vision - Receipt History</title>
</svelte:head>

<div class="receipt-history">
  <h1>Receipt History</h1>

  {#if isLoading}
    <div class="loading">Loading receipts...</div>
  {:else if error}
    <div class="error-message">
      {error}
      <button on:click={loadReceipts} class="retry-button">Retry</button>
    </div>
  {:else if receipts.length === 0}
    <div class="empty-state">
      <p>No receipts found. Upload a receipt to get started.</p>
      <a href="/receipts" class="button">Upload Receipt</a>
    </div>
  {:else}
    <div class="receipts-list">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Store</th>
            <th>Total</th>
            <th>Items</th>
            <th>Savings</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {#each receipts as receipt}
            <tr>
              <td>{formatDate(receipt.created_at)}</td>
              <td>{receipt.data?.receipt_data?.place || 'N/A'}</td>
              <td
                >{receipt.data?.receipt_data?.total
                  ? `€${receipt.data.receipt_data.total.toFixed(2)}`
                  : 'N/A'}</td
              >
              <td>{receipt.data?.items?.length || 0} items</td>
              <td>
                {#if receipt.data?.items}
                  €{calculateTotalDiscount(receipt.data.items).toFixed(2)}
                {:else}
                  €0.00
                {/if}
              </td>
              <td>
                <button on:click={() => viewReceiptDetails(receipt)} class="view-button"
                  >View</button
                >
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}

  <!-- Receipt Details Modal -->
  {#if selectedReceipt}
    <div
      class="modal-overlay"
      on:click={closeDetails}
      on:keydown={(e) => e.key === 'Escape' && closeDetails()}
      role="dialog"
      aria-modal="true"
    >
      <div class="modal-content" on:click|stopPropagation>
        <div class="modal-header">
          <h2>Receipt Details</h2>
          <button class="close-button" on:click={closeDetails}>×</button>
        </div>

        <div class="modal-body">
          <!-- Receipt Summary -->
          {#if selectedReceipt.data?.receipt_data}
            <div class="receipt-summary">
              <h3>Receipt Summary</h3>
              <table>
                <tbody>
                  <tr>
                    <th>Date</th>
                    <td>{selectedReceipt.data.receipt_data.date || 'N/A'}</td>
                  </tr>
                  <tr>
                    <th>Place</th>
                    <td>{selectedReceipt.data.receipt_data.place || 'N/A'}</td>
                  </tr>
                  <tr>
                    <th>Total</th>
                    <td
                      >{selectedReceipt.data.receipt_data.total
                        ? `€${selectedReceipt.data.receipt_data.total.toFixed(2)}`
                        : 'N/A'}</td
                    >
                  </tr>
                  <tr>
                    <th>Total Savings</th>
                    <td>{selectedReceipt.data.receipt_data.total_savings || 'N/A'}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          {/if}

          <!-- Loyalty Discount Summary -->
          {#if selectedReceipt.data?.items && selectedReceipt.data.items.length > 0}
            <div class="loyalty-summary">
              <h3>Loyalty Discount Summary</h3>
              <div class="summary-cards">
                <div class="summary-card">
                  <div class="summary-value">
                    {countDiscountedItems(selectedReceipt.data.items)}
                  </div>
                  <div class="summary-label">Items with Discounts</div>
                </div>
                <div class="summary-card highlight">
                  <div class="summary-value">
                    €{calculateTotalDiscount(selectedReceipt.data.items).toFixed(2)}
                  </div>
                  <div class="summary-label">Total Savings</div>
                </div>
              </div>
            </div>
          {/if}

          <!-- Receipt Items -->
          {#if selectedReceipt.data?.items && selectedReceipt.data.items.length > 0}
            <div class="receipt-items">
              <h3>Receipt Items</h3>
              <table>
                <thead>
                  <tr>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total Price</th>
                    <th>Loyalty Discount</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody>
                  {#each selectedReceipt.data.items as item}
                    <tr class={item.has_loyalty_discount ? 'has-discount' : ''}>
                      <td>{item.name_en || item.name_fi || 'N/A'}</td>
                      <td
                        >{item.quantity
                          ? `${item.quantity} ${item.unit_of_measure || ''}`
                          : 'N/A'}</td
                      >
                      <td>{item.unit_price ? `€${item.unit_price.toFixed(2)}` : 'N/A'}</td>
                      <td>{item.total_price ? `€${item.total_price.toFixed(2)}` : 'N/A'}</td>
                      <td>
                        {#if item.has_loyalty_discount}
                          <span class="discount-badge">Yes</span>
                          {#if item.loyalty_discount}
                            <span class="discount-amount">€{item.loyalty_discount.toFixed(2)}</span>
                          {/if}
                        {:else}
                          -
                        {/if}
                      </td>
                      <td>
                        {#if item.item_category}
                          {item.item_category.level_1 || ''}
                          {item.item_category.level_2 ? `> ${item.item_category.level_2}` : ''}
                          {item.item_category.level_3 ? `> ${item.item_category.level_3}` : ''}
                        {:else}
                          N/A
                        {/if}
                      </td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          {:else}
            <p>No items found in the receipt.</p>
          {/if}
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .receipt-history {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
  }

  h1 {
    margin-bottom: 2rem;
  }

  .loading {
    text-align: center;
    padding: 2rem;
    color: #666;
  }

  .error-message {
    color: #d32f2f;
    padding: 1rem;
    background-color: #ffebee;
    border-radius: 4px;
    margin-bottom: 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .retry-button {
    background-color: #d32f2f;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }

  .empty-state {
    text-align: center;
    padding: 3rem;
    background-color: #f5f5f5;
    border-radius: 8px;
  }

  .button {
    display: inline-block;
    background-color: var(--color-accent);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    font-weight: 600;
    text-decoration: none;
    margin-top: 1rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    margin: 1rem 0;
  }

  th,
  td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #eee;
  }

  th {
    background-color: #f5f5f5;
    font-weight: 600;
  }

  tr:hover {
    background-color: #f9f9f9;
  }

  .view-button {
    background-color: var(--color-accent);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }

  /* Modal styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    overflow-y: auto;
    padding: 2rem;
  }

  .modal-content {
    background-color: white;
    border-radius: 8px;
    width: 90%;
    max-width: 1000px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #eee;
  }

  .modal-header h2 {
    margin: 0;
  }

  .close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #666;
  }

  .modal-body {
    padding: 1.5rem;
  }

  /* Receipt details styles */
  .receipt-summary,
  .loyalty-summary,
  .receipt-items {
    margin-bottom: 2rem;
  }

  h3 {
    margin: 1.5rem 0 1rem;
  }

  tr.has-discount {
    background-color: #fff8e1;
  }

  tr.has-discount:hover {
    background-color: #ffecb3;
  }

  .discount-badge {
    display: inline-block;
    background-color: #4caf50;
    color: white;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.8rem;
    margin-right: 0.5rem;
  }

  .discount-amount {
    color: #4caf50;
    font-weight: 600;
  }

  /* Loyalty Summary Styles */
  .loyalty-summary {
    margin: 1.5rem 0;
    padding: 1rem;
    background-color: #f5f5f5;
    border-radius: 8px;
  }

  .summary-cards {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 1rem;
  }

  .summary-card {
    flex: 1;
    min-width: 200px;
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
  }

  .summary-card.highlight {
    background-color: #e8f5e9;
    border: 1px solid #4caf50;
  }

  .summary-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #333;
    margin-bottom: 0.5rem;
  }

  .summary-card.highlight .summary-value {
    color: #2e7d32;
  }

  .summary-label {
    font-size: 0.9rem;
    color: #666;
  }
</style>
