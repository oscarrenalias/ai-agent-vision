<script>
  import { onMount } from 'svelte';
  
  let file;
  let previewUrl = '';
  let isUploading = false;
  let uploadResult = null;
  let error = null;
  
  function handleFileChange(event) {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      file = selectedFile;
      previewUrl = URL.createObjectURL(selectedFile);
    }
  }
  
  async function handleSubmit() {
    if (!file) {
      error = 'Please select a file first';
      return;
    }
    
    error = null;
    isUploading = true;
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.status === 'success') {
        uploadResult = result;
      } else {
        error = result.error || 'Failed to process receipt';
      }
    } catch (err) {
      error = 'Error uploading file: ' + err.message;
    } finally {
      isUploading = false;
    }
  }
  
  onMount(() => {
    return () => {
      // Clean up object URL when component is destroyed
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
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
      <button 
        on:click={handleSubmit} 
        disabled={isUploading || !file} 
        class="submit-button"
      >
        {isUploading ? 'Processing...' : 'Analyze Receipt'}
      </button>
      
      {#if error}
        <div class="error-message">
          {error}
        </div>
      {/if}
      
      {#if uploadResult}
        <div class="success-message">
          Receipt processed successfully!
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .receipt-upload {
    max-width: 800px;
    margin: 0 auto;
  }
  
  h1 {
    margin-bottom: 2rem;
  }
  
  .upload-container {
    display: flex;
    flex-direction: column;
    gap: 2rem;
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
  }
</style>
