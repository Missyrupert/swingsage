/**
 * Main JavaScript for Swing Sage Application
 * Handles file uploads, API calls, and UI interactions
 */

class SwingSageApp {
    constructor() {
        this.apiBaseUrl = '/analyze';
        this.currentFile = null;
        this.isProcessing = false;
        
        this.initializeEventListeners();
    }
    
    initializeEventListeners() {
        // File upload handling
        const fileInput = document.getElementById('videoInput');
        const fileUpload = document.querySelector('.file-upload');
        const uploadForm = document.getElementById('uploadForm');
        
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
        
        if (fileUpload) {
            fileUpload.addEventListener('click', () => fileInput?.click());
            fileUpload.addEventListener('dragover', (e) => this.handleDragOver(e));
            fileUpload.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            fileUpload.addEventListener('drop', (e) => this.handleDrop(e));
        }
        
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
        
        // Golfer type selection
        const golferTypeSelect = document.getElementById('golferType');
        if (golferTypeSelect) {
            golferTypeSelect.addEventListener('change', (e) => this.handleGolferTypeChange(e));
        }
        
        // Club selection
        const clubSelect = document.getElementById('clubType');
        if (clubSelect) {
            clubSelect.addEventListener('change', (e) => this.handleClubChange(e));
        }
    }
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.currentFile = file;
            this.updateFileDisplay(file);
            this.validateFile(file);
        }
    }
    
    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }
    
    handleDragLeave(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
    }
    
    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            this.currentFile = file;
            this.updateFileDisplay(file);
            this.validateFile(file);
            
            // Update file input
            const fileInput = document.getElementById('videoInput');
            if (fileInput) {
                fileInput.files = files;
            }
        }
    }
    
    updateFileDisplay(file) {
        const fileDisplay = document.getElementById('fileDisplay');
        if (fileDisplay) {
            const fileSize = this.formatFileSize(file.size);
            fileDisplay.innerHTML = `
                <div class="file-info">
                    <strong>${file.name}</strong>
                    <span class="file-size">${fileSize}</span>
                </div>
            `;
        }
        
        // Enable submit button
        const submitBtn = document.querySelector('.btn-primary');
        if (submitBtn) {
            submitBtn.disabled = false;
        }
    }
    
    validateFile(file) {
        const allowedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/wmv'];
        const maxSize = 100 * 1024 * 1024; // 100MB
        
        let isValid = true;
        let errorMessage = '';
        
        // Check file type
        if (!allowedTypes.includes(file.type)) {
            isValid = false;
            errorMessage = 'Please select a valid video file (MP4, AVI, MOV, MKV, WMV)';
        }
        
        // Check file size
        if (file.size > maxSize) {
            isValid = false;
            errorMessage = 'File size must be less than 100MB';
        }
        
        if (!isValid) {
            this.showError(errorMessage);
            this.currentFile = null;
            this.updateFileDisplay(null);
        } else {
            this.hideError();
        }
        
        return isValid;
    }
    
    async handleFormSubmit(event) {
        event.preventDefault();
        
        if (!this.currentFile) {
            this.showError('Please select a video file');
            return;
        }
        
        if (!this.validateFile(this.currentFile)) {
            return;
        }
        
        this.isProcessing = true;
        this.showLoading();
        
        try {
            const formData = new FormData();
            formData.append('video', this.currentFile);
            
            // Add golfer type and club if available
            const golferType = document.getElementById('golferType')?.value || 'weekend';
            const clubType = document.getElementById('clubType')?.value || 'driver';
            
            formData.append('golfer_type', golferType);
            formData.append('club', clubType);
            
            const response = await fetch(this.apiBaseUrl, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showSuccess(result);
            } else {
                this.showError(result.error || 'Analysis failed. Please try again.');
            }
            
        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Network error. Please check your connection and try again.');
        } finally {
            this.isProcessing = false;
            this.hideLoading();
        }
    }
    
    handleGolferTypeChange(event) {
        const golferType = event.target.value;
        console.log('Golfer type changed to:', golferType);
        
        // Update UI based on golfer type
        this.updateGolferSpecificUI(golferType);
    }
    
    handleClubChange(event) {
        const clubType = event.target.value;
        console.log('Club type changed to:', clubType);
        
        // Update UI based on club type
        this.updateClubSpecificUI(clubType);
    }
    
    updateGolferSpecificUI(golferType) {
        // Update coaching tips or UI elements based on golfer type
        const coachingTips = {
            'beginner': 'Focus on basic fundamentals and consistency',
            'weekend': 'Enjoy the game while improving your technique',
            'competitive': 'Fine-tune your swing for maximum performance',
            'senior': 'Maintain flexibility and adapt to your current abilities',
            'junior': 'Build good habits and have fun learning'
        };
        
        const tipElement = document.getElementById('golferTip');
        if (tipElement && coachingTips[golferType]) {
            tipElement.textContent = coachingTips[golferType];
        }
    }
    
    updateClubSpecificUI(clubType) {
        // Update UI based on club selection
        const clubTips = {
            'driver': 'Driver swings need more control and tempo',
            'iron': 'Iron shots benefit from consistent posture',
            'wedge': 'Wedge shots require precision and feel',
            'putter': 'Putting is all about rhythm and confidence'
        };
        
        const tipElement = document.getElementById('clubTip');
        if (tipElement && clubTips[clubType]) {
            tipElement.textContent = clubTips[clubType];
        }
    }
    
    showLoading() {
        const loadingElement = document.getElementById('loadingIndicator');
        const submitBtn = document.querySelector('.btn-primary');
        
        if (loadingElement) {
            loadingElement.classList.remove('hidden');
        }
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading"></span> Analyzing...';
        }
    }
    
    hideLoading() {
        const loadingElement = document.getElementById('loadingIndicator');
        const submitBtn = document.querySelector('.btn-primary');
        
        if (loadingElement) {
            loadingElement.classList.add('hidden');
        }
        
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Analyze Swing';
        }
    }
    
    showSuccess(result) {
        const resultContainer = document.getElementById('resultContainer');
        const videoElement = document.getElementById('resultVideo');
        const coachingElement = document.getElementById('coachingTip');
        
        if (resultContainer) {
            resultContainer.classList.remove('hidden');
        }
        
        if (videoElement && result.video_url) {
            videoElement.src = result.video_url;
            videoElement.style.display = 'block';
        }
        
        if (coachingElement && result.coaching_tip) {
            coachingElement.textContent = result.coaching_tip;
            coachingElement.style.display = 'block';
        }
        
        // Show success message
        this.showMessage('Analysis complete! Check your results below.', 'success');
        
        // Scroll to results
        resultContainer?.scrollIntoView({ behavior: 'smooth' });
    }
    
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    hideError() {
        const errorElement = document.querySelector('.status-error');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    showMessage(message, type = 'info') {
        // Remove existing messages
        const existingMessages = document.querySelectorAll('.status-message');
        existingMessages.forEach(msg => msg.remove());
        
        // Create new message
        const messageElement = document.createElement('div');
        messageElement.className = `status-message status-${type}`;
        messageElement.textContent = message;
        
        // Insert at top of main content
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertBefore(messageElement, mainContent.firstChild);
        }
        
        // Auto-hide after 5 seconds for success messages
        if (type === 'success') {
            setTimeout(() => {
                messageElement.remove();
            }, 5000);
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.swingSageApp = new SwingSageApp();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SwingSageApp;
} 