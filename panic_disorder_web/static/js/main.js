document.getElementById('assessmentForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/predict/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        const data = await response.json();
        
        // Check if response was successful
        if (data.success === false) {
            displayError(data.error || 'An error occurred while processing your assessment.');
        } else {
            // Display results in the card
            displayResult(data);
        }
    } catch (error) {
        console.error('Error:', error);
        displayError('An error occurred while processing your assessment. Please try again.');
    }
});

function displayResult(data) {
    const resultCard = document.getElementById('resultCard');
    const predictionResult = document.getElementById('predictionResult');
    const confidenceBar = document.getElementById('confidenceBar');
    const confidenceText = document.getElementById('confidenceText');
    const resultMessage = document.getElementById('resultMessage');
    
    // Remove error class if present
    resultCard.classList.remove('error');
    
    // Reset confidence bar first
    confidenceBar.style.width = '0%';
    
    // Set prediction value
    if (data.prediction) {
        predictionResult.textContent = data.prediction;
    }
    
    // Set confidence level
    if (data.confidence !== undefined) {
        const confidence = Math.round(data.confidence * 100);
        confidenceText.textContent = confidence + '%';
        // Animate the confidence bar
        setTimeout(() => {
            confidenceBar.style.width = confidence + '%';
        }, 100);
    }
    
    // Set result message
    if (data.message) {
        resultMessage.textContent = data.message;
    } else {
        resultMessage.textContent = 'Your assessment has been processed successfully.';
    }
    
    // Show the result card
    resultCard.classList.remove('hidden');
    
    // Scroll to result card
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function displayError(message) {
    const resultCard = document.getElementById('resultCard');
    const predictionResult = document.getElementById('predictionResult');
    const confidenceBar = document.getElementById('confidenceBar');
    const resultMessage = document.getElementById('resultMessage');
    
    // Add error class
    resultCard.classList.add('error');
    
    // Set error message
    predictionResult.textContent = 'Error';
    resultMessage.textContent = message;
    
    // Reset confidence bar
    confidenceBar.style.width = '0%';
    document.getElementById('confidenceText').textContent = '0%';
    
    // Show the result card
    resultCard.classList.remove('hidden');
    
    // Scroll to result card
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function closeResultCard() {
    const resultCard = document.getElementById('resultCard');
    resultCard.classList.add('hidden');
}