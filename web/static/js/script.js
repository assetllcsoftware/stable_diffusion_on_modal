// script.js - JavaScript for the Stable Diffusion web interface

document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const form = document.getElementById('generation-form');
    const generateBtn = document.getElementById('generate-btn');
    const loadingDiv = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const generatedImage = document.getElementById('generated-image');
    const downloadBtn = document.getElementById('download-btn');
    const newGenerationBtn = document.getElementById('new-generation-btn');
    
    // Add event listeners
    form.addEventListener('submit', handleFormSubmit);
    downloadBtn.addEventListener('click', handleDownload);
    newGenerationBtn.addEventListener('click', resetForm);
    
    // Handle form submission
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        // Show loading state
        generateBtn.disabled = true;
        loadingDiv.classList.remove('hidden');
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        
        // Get form data
        const formData = new FormData(form);
        const params = new URLSearchParams();
        
        // Add form data to URL params
        for (const [key, value] of formData.entries()) {
            params.append(key, value);
        }
        
        try {
            // Send request to the API
            const response = await fetch(`/generate?${params.toString()}`, {
                method: 'POST',
            });
            
            // Check if the request was successful
            if (!response.ok) {
                throw new Error('Failed to generate image');
            }
            
            // Parse the response
            const data = await response.json();
            
            // Display the generated image
            generatedImage.src = data.image_url;
            generatedImage.onload = () => {
                loadingDiv.classList.add('hidden');
                resultDiv.classList.remove('hidden');
                generateBtn.disabled = false;
            };
        } catch (error) {
            console.error('Error:', error);
            loadingDiv.classList.add('hidden');
            errorDiv.classList.remove('hidden');
            generateBtn.disabled = false;
        }
    }
    
    // Handle image download
    function handleDownload() {
        const imageUrl = generatedImage.src;
        const link = document.createElement('a');
        link.href = imageUrl;
        link.download = `stable-diffusion-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Reset the form for a new generation
    function resetForm() {
        resultDiv.classList.add('hidden');
        form.reset();
    }
}); 