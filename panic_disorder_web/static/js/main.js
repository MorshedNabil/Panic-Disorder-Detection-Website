document.getElementById('assessmentForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const submitButton = this.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Processing...';
    
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
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
});

function displayResult(data) {
    const resultCard = document.getElementById('resultCard');
    const predictionResult = document.getElementById('predictionResult');
    const confidenceBar = document.getElementById('confidenceBar');
    const confidenceText = document.getElementById('confidenceText');
    const resultMessage = document.getElementById('resultMessage');
    const adviceMessage = document.getElementById('adviceMessage');
    
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

    if (data.advice) {
        adviceMessage.textContent = data.advice;
    } else {
        adviceMessage.textContent = 'No AI guidance is available right now. If symptoms feel severe or unsafe, seek urgent medical help.';
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
    const adviceMessage = document.getElementById('adviceMessage');
    
    // Add error class
    resultCard.classList.add('error');
    
    // Set error message
    predictionResult.textContent = 'Error';
    resultMessage.textContent = message;
    adviceMessage.textContent = 'Please try again. If you feel in immediate danger, have chest pain, fainting, or severe trouble breathing, seek emergency medical help now.';
    
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
