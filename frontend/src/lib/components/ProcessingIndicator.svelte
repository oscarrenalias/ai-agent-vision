<script>
  import LoadingSpinner from './LoadingSpinner.svelte';

  export let progress = 0; // 0-100
  export let message = 'Processing your receipt...';
  export let submessage = 'This may take 2-3 minutes to complete.';
</script>

<div class="processing-indicator">
  <LoadingSpinner size="80px" {message} />

  <div class="progress-container">
    <div class="progress-bar">
      <div class="progress-fill" style="width: {progress}%" />
    </div>
    <p class="submessage">{submessage}</p>
  </div>

  <div class="processing-steps">
    <div class="step {progress >= 25 ? 'active' : ''}">
      <div class="step-icon">1</div>
      <div class="step-label">Analyzing receipt</div>
    </div>
    <div class="step {progress >= 50 ? 'active' : ''}">
      <div class="step-icon">2</div>
      <div class="step-label">Extracting items</div>
    </div>
    <div class="step {progress >= 75 ? 'active' : ''}">
      <div class="step-icon">3</div>
      <div class="step-label">Classifying items</div>
    </div>
    <div class="step {progress >= 100 ? 'active' : ''}">
      <div class="step-icon">4</div>
      <div class="step-label">Saving results</div>
    </div>
  </div>
</div>

<style>
  .processing-indicator {
    background-color: white;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    margin: 2rem 0;
    text-align: center;
  }

  .progress-container {
    margin: 1.5rem 0;
  }

  .progress-bar {
    height: 10px;
    background-color: #f0f0f0;
    border-radius: 5px;
    overflow: hidden;
    margin-bottom: 0.5rem;
  }

  .progress-fill {
    height: 100%;
    background-color: #4caf50;
    border-radius: 5px;
    transition: width 0.5s ease;
  }

  .submessage {
    color: #666;
    font-size: 0.9rem;
    margin: 0.5rem 0;
  }

  .processing-steps {
    display: flex;
    justify-content: space-between;
    margin-top: 2rem;
    flex-wrap: wrap;
  }

  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
    min-width: 100px;
    margin: 0.5rem;
    opacity: 0.5;
    transition: opacity 0.3s ease;
  }

  .step.active {
    opacity: 1;
  }

  .step-icon {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #ddd;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-bottom: 0.5rem;
  }

  .step.active .step-icon {
    background-color: #4caf50;
  }

  .step-label {
    font-size: 0.85rem;
    color: #555;
  }
</style>
