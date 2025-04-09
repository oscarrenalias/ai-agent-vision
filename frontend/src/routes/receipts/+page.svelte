<script>
  import { onMount } from 'svelte';
  import ProcessingIndicator from '$lib/components/ProcessingIndicator.svelte';
  import ChatButton from '$lib/components/ChatButton.svelte';
  import ChatWindow from '$lib/components/ChatWindow.svelte';
  //import { isChatOpen, currentReceiptData, openChat, closeChat } from '$lib/stores/chatStore';
  import { setReceiptData, openChat, closeChat, isChatOpen } from '$lib/stores/chatStore';

  //import { isChatOpen } from '$lib/stores/chatStore';

  let file;
  let previewUrl = '';
  let isUploading = false;
  let uploadResult = null;
  let error = null;
  let receiptData = null;
  let totalLoyaltyDiscount = 0;
  let discountedItemsCount = 0;
  let processingProgress = 25; // Initial progress value
  let processingInterval; // For simulating progress

  function handleFileChange(event) {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      file = selectedFile;
      previewUrl = URL.createObjectURL(selectedFile);
      // Reset previous results
      uploadResult = null;
      receiptData = null;
      error = null;
      totalLoyaltyDiscount = 0;
      discountedItemsCount = 0;

      // Clear the global receipt data
      setReceiptData(null);
    }
  }

  function calculateDiscountSummary(items) {
    let total = 0;
    let count = 0;

    if (items && items.length > 0) {
      items.forEach((item) => {
        if (item.has_loyalty_discount && item.loyalty_discount) {
          total += parseFloat(item.loyalty_discount);
          count++;
        }
      });
    }

    totalLoyaltyDiscount = total;
    discountedItemsCount = count;
  }

  // Function to simulate progress during processing
  function startProgressSimulation() {
    processingProgress = 10; // Start at 10%

    // Clear any existing interval
    if (processingInterval) clearInterval(processingInterval);

    // Update progress every 10 seconds to simulate the long-running process
    processingInterval = setInterval(() => {
      if (processingProgress < 40) {
        processingProgress += 10;
      }
    }, 5000); // 5 seconds between updates
  }

  // Function to stop progress simulation
  function stopProgressSimulation() {
    if (processingInterval) {
      clearInterval(processingInterval);
      processingInterval = null;
    }
    processingProgress = 100; // Complete the progress
  }

  let jobId = null;
  let pollingInterval = null;

  async function handleSubmit() {
    if (!file) {
      error = 'Please select a file first';
      return;
    }

    error = null;
    isUploading = true;
    receiptData = null;
    jobId = null;

    // Start simulating progress
    startProgressSimulation();

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Submit the file and get a job ID
      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (response.ok && result.job_id) {
        jobId = result.job_id;
        console.log(`Job started with ID: ${jobId}`);

        // Start polling for job status
        startPolling(jobId);
      } else {
        error = result.message || 'Failed to start receipt processing';
        isUploading = false;
        stopProgressSimulation();
      }
    } catch (err) {
      error = 'Error uploading file: ' + (err instanceof Error ? err.message : String(err));
      isUploading = false;
      stopProgressSimulation();
    }
  }

  function startPolling(jobId) {
    // Clear any existing polling
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }

    // Poll every 5 seconds
    pollingInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/jobs/${jobId}`);
        const jobStatus = await response.json();

        console.log('Job status:', jobStatus);

        if (jobStatus.status === 'completed') {
          // Job completed successfully
          clearInterval(pollingInterval);
          isUploading = false;
          stopProgressSimulation();

          // Set the receipt data
          receiptData = jobStatus.result;
          calculateDiscountSummary(receiptData.items);
          setReceiptData(receiptData);
          uploadResult = { status: 'success' };
        } else if (jobStatus.status === 'failed') {
          // Job failed
          clearInterval(pollingInterval);
          isUploading = false;
          stopProgressSimulation();
          error = jobStatus.error || 'Receipt processing failed';
        } else if (jobStatus.status === 'processing') {
          // Job is still processing, update progress
          processingProgress = 50; // Set to middle progress while processing
        }
      } catch (err) {
        console.error('Error polling job status:', err);
      }
    }, 5000); // Check every 5 seconds
  }

  // Clean up polling on component unmount
  onMount(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
      // Clean up object URL when component is destroyed
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      // Clear any running interval
      if (processingInterval) {
        clearInterval(processingInterval);
      }
    };
  });

  // When receipt data is available, set it in the store for the chat component to use
  $: if (receiptData) {
    setReceiptData(receiptData);
  }

  onMount(() => {
    return () => {
      // Clean up object URL when component is destroyed
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
      // Clear any running interval
      if (processingInterval) {
        clearInterval(processingInterval);
      }
    };
  });
</script>

<svelte:head>
  <title>AI Agent Vision - Receipt Upload</title>
</svelte:head>

<div class="receipt-upload">
  <h1>Upload Receipt</h1>

  <div class="upload-container">
    <div class="upload-area">
      <label for="receipt-upload" class="upload-label">
        {#if previewUrl}
          <img src={previewUrl} alt="Receipt preview" class="preview-image" />
        {:else}
          <div class="upload-placeholder">
            <span class="icon">📷</span>
            <span>Click to select a receipt image</span>
          </div>
        {/if}
      </label>
      <input
        type="file"
        id="receipt-upload"
        accept="image/*"
        on:change={handleFileChange}
        class="file-input"
      />
    </div>

    <div class="controls">
      <button on:click={handleSubmit} disabled={isUploading || !file} class="submit-button">
        {isUploading ? 'Processing...' : 'Analyze Receipt'}
      </button>

      {#if error}
        <div class="error-message">
          {error}
        </div>
      {/if}

      {#if uploadResult && !receiptData}
        <div class="success-message">Receipt processed successfully, but no data was returned.</div>
      {/if}

      {#if receiptData}
        <div class="success-message">
          Receipt processed successfully!
          <a href="/receipts/history" class="view-history-link">View Receipt History</a>
        </div>
      {/if}
    </div>
  </div>

  {#if isUploading}
    <ProcessingIndicator
      progress={processingProgress}
      message="Processing your receipt..."
      submessage="This may take 2-3 minutes to complete. Please don't refresh the page."
    />
  {/if}

  {#if receiptData}
    <div class="receipt-results">
      <h2>Receipt Analysis Results</h2>

      <!-- Receipt Summary -->
      {#if receiptData.receipt_data}
        <div class="receipt-summary">
          <h3>Receipt Summary</h3>
          <table>
            <tbody>
              <tr>
                <th>Date</th>
                <td>{receiptData.receipt_data.date || 'N/A'}</td>
              </tr>
              <tr>
                <th>Place</th>
                <td>{receiptData.receipt_data.place || 'N/A'}</td>
              </tr>
              <tr>
                <th>Total</th>
                <td
                  >{receiptData.receipt_data.total
                    ? `€${receiptData.receipt_data.total.toFixed(2)}`
                    : 'N/A'}</td
                >
              </tr>
              <tr>
                <th>Total Savings</th>
                <td>{receiptData.receipt_data.total_savings || 'N/A'}</td>
              </tr>
            </tbody>
          </table>
        </div>
      {/if}

      <!-- Loyalty Discount Summary -->
      {#if receiptData.items && receiptData.items.length > 0}
        <div class="loyalty-summary">
          <h3>Loyalty Discount Summary</h3>
          <div class="summary-cards">
            <div class="summary-card">
              <div class="summary-value">{discountedItemsCount}</div>
              <div class="summary-label">Items with Discounts</div>
            </div>
            <div class="summary-card highlight">
              <div class="summary-value">€{totalLoyaltyDiscount.toFixed(2)}</div>
              <div class="summary-label">Total Savings</div>
            </div>
            <div class="summary-card">
              <div class="summary-value">
                {discountedItemsCount > 0
                  ? `€${(totalLoyaltyDiscount / discountedItemsCount).toFixed(2)}`
                  : '€0.00'}
              </div>
              <div class="summary-label">Average Discount per Item</div>
            </div>
          </div>
        </div>
      {/if}

      <!-- Receipt Items -->
      {#if receiptData.items && receiptData.items.length > 0}
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
              {#each receiptData.items as item}
                <tr class={item.has_loyalty_discount ? 'has-discount' : ''}>
                  <td>{item.name_en || item.name_fi || 'N/A'}</td>
                  <td>{item.quantity ? `${item.quantity} ${item.unit_of_measure || ''}` : 'N/A'}</td
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
  {/if}
  {#if receiptData}
    <!-- Chat window component (only shown when open) -->
    <ChatWindow isOpen={$isChatOpen} {receiptData} on:close={closeChat} />
  {:else}
    <!-- Chat window without receipt data -->
    <ChatWindow isOpen={$isChatOpen} on:close={closeChat} />
  {/if}
</div>

<style>
  .receipt-upload {
    max-width: 1000px;
    margin: 0 auto;
    padding-bottom: 3rem;
  }

  h1 {
    margin-bottom: 2rem;
  }

  h2 {
    margin: 2rem 0 1rem;
  }

  h3 {
    margin: 1.5rem 0 1rem;
  }

  .upload-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .upload-area {
    border: 2px dashed #ccc;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    cursor: pointer;
  }

  .upload-label {
    display: block;
    cursor: pointer;
  }

  .upload-placeholder {
    padding: 4rem 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .icon {
    font-size: 3rem;
  }

  .file-input {
    display: none;
  }

  .preview-image {
    max-width: 100%;
    max-height: 400px;
    margin: 0 auto;
    display: block;
  }

  .controls {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .submit-button {
    padding: 0.75rem;
    font-size: 1.1rem;
  }

  .error-message {
    color: #d32f2f;
    padding: 0.75rem;
    background-color: #ffebee;
    border-radius: 4px;
  }

  .success-message {
    color: #2e7d32;
    padding: 0.75rem;
    background-color: #e8f5e9;
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .view-history-link {
    color: #2e7d32;
    font-weight: 600;
    text-decoration: underline;
  }

  .receipt-results {
    margin-top: 3rem;
    background-color: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
