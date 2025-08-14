/**
 * Exam Timer JavaScript
 * Handles countdown timer, progress bar, and automatic submission
 */

class ExamTimer {
    constructor() {
        this.duration = parseInt(document.querySelector('meta[name="exam-duration"]').content) * 60; // Convert to seconds
        this.timeRemaining = parseInt(document.querySelector('meta[name="time-remaining"]').content);
        this.sessionId = document.querySelector('meta[name="exam-session-id"]').content;
        this.timerInterval = null;
        this.warningThresholds = [300, 120, 60, 30]; // Warning at 5min, 2min, 1min, 30sec
        this.warningsShown = new Set();
        this.isRunning = false;
        
        this.init();
    }
    
    init() {
        this.updateDisplay();
        this.updateProgressBar();
        this.start();
        
        console.log(`Timer initialized: ${this.timeRemaining} seconds remaining`);
    }
    
    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.timerInterval = setInterval(() => {
            this.tick();
        }, 1000);
        
        console.log('Timer started');
    }
    
    stop() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
            this.isRunning = false;
            console.log('Timer stopped');
        }
    }
    
    tick() {
        this.timeRemaining--;
        
        this.updateDisplay();
        this.updateProgressBar();
        this.checkWarnings();
        
        // Auto-submit when time is up
        if (this.timeRemaining <= 0) {
            this.timeUp();
        }
        
        // Sync with server every 30 seconds
        if (this.timeRemaining % 30 === 0) {
            this.syncWithServer();
        }
    }
    
    updateDisplay() {
        const minutes = Math.floor(Math.abs(this.timeRemaining) / 60);
        const seconds = Math.abs(this.timeRemaining) % 60;
        
        const minutesElement = document.getElementById('timer-minutes');
        const secondsElement = document.getElementById('timer-seconds');
        const timerDisplay = document.getElementById('timer-display');
        
        if (minutesElement && secondsElement) {
            minutesElement.textContent = minutes.toString().padStart(2, '0');
            secondsElement.textContent = seconds.toString().padStart(2, '0');
            
            // Add visual warnings
            if (this.timeRemaining <= 0) {
                timerDisplay.className = 'timer-display timer-danger';
                minutesElement.textContent = '00';
                secondsElement.textContent = '00';
            } else if (this.timeRemaining <= 300) { // 5 minutes
                timerDisplay.className = 'timer-display timer-danger';
            } else if (this.timeRemaining <= 600) { // 10 minutes
                timerDisplay.className = 'timer-display timer-warning';
            } else {
                timerDisplay.className = 'timer-display';
            }
        }
    }
    
    updateProgressBar() {
        const progressBar = document.getElementById('timer-progress-bar');
        if (progressBar && this.duration > 0) {
            const percentage = Math.max(0, (this.timeRemaining / this.duration) * 100);
            progressBar.style.width = `${percentage}%`;
            
            // Change color based on time remaining
            if (percentage <= 8.33) { // 5 minutes for 60-minute exam
                progressBar.className = 'progress-bar bg-danger';
            } else if (percentage <= 16.67) { // 10 minutes for 60-minute exam
                progressBar.className = 'progress-bar bg-warning';
            } else {
                progressBar.className = 'progress-bar bg-primary';
            }
        }
    }
    
    checkWarnings() {
        this.warningThresholds.forEach(threshold => {
            if (this.timeRemaining <= threshold && !this.warningsShown.has(threshold)) {
                this.showTimeWarning(threshold);
                this.warningsShown.add(threshold);
            }
        });
    }
    
    showTimeWarning(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        
        let message;
        if (minutes > 0) {
            message = `${minutes} minute${minutes > 1 ? 's' : ''} remaining!`;
        } else {
            message = `${remainingSeconds} second${remainingSeconds > 1 ? 's' : ''} remaining!`;
        }
        
        this.showTimerAlert(message, 'warning');
        
        // Play warning sound (if allowed by browser)
        this.playWarningSound();
        
        console.log(`Time warning: ${message}`);
    }
    
    showTimerAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 120px; left: 50%; transform: translateX(-50%); z-index: 1050; max-width: 400px;';
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i data-feather="clock" class="me-2"></i>
                <strong>${message}</strong>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        feather.replace();
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    playWarningSound() {
        try {
            // Create a simple beep sound using Web Audio API
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800; // 800 Hz
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start();
            oscillator.stop(audioContext.currentTime + 0.5);
        } catch (error) {
            console.log('Could not play warning sound:', error);
        }
    }
    
    timeUp() {
        this.stop();
        
        this.showTimerAlert('Time is up! Your exam is being submitted automatically.', 'danger');
        
        // Automatically submit the exam
        setTimeout(() => {
            if (window.examManager && !window.examManager.examSubmitted) {
                window.examManager.submitExam();
            } else {
                // Fallback: submit form directly
                document.getElementById('exam-form').submit();
            }
        }, 2000);
        
        console.log('Time up - auto-submitting exam');
    }
    
    async syncWithServer() {
        try {
            const response = await fetch(`/api/exam/session/${this.sessionId}/time-remaining`);
            if (response.ok) {
                const data = await response.json();
                
                // Check if exam was submitted from another tab/device
                if (data.is_submitted) {
                    this.stop();
                    window.location.reload();
                    return;
                }
                
                // Sync time with server (in case of clock drift)
                const serverTime = data.time_remaining;
                const timeDiff = Math.abs(this.timeRemaining - serverTime);
                
                if (timeDiff > 5) { // Sync if difference is more than 5 seconds
                    console.log(`Time sync: Local ${this.timeRemaining}s, Server ${serverTime}s`);
                    this.timeRemaining = serverTime;
                    this.updateDisplay();
                    this.updateProgressBar();
                }
            }
        } catch (error) {
            console.error('Failed to sync with server:', error);
        }
    }
    
    // Public methods
    getTimeRemaining() {
        return this.timeRemaining;
    }
    
    getFormattedTime() {
        const minutes = Math.floor(Math.abs(this.timeRemaining) / 60);
        const seconds = Math.abs(this.timeRemaining) % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    addTime(seconds) {
        this.timeRemaining += seconds;
        this.updateDisplay();
        this.updateProgressBar();
        console.log(`Added ${seconds} seconds to timer`);
    }
    
    pause() {
        if (this.isRunning) {
            this.stop();
            console.log('Timer paused');
        }
    }
    
    resume() {
        if (!this.isRunning && this.timeRemaining > 0) {
            this.start();
            console.log('Timer resumed');
        }
    }
}

// Initialize timer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize timer on exam pages
    if (document.querySelector('meta[name="exam-session-id"]')) {
        window.examTimer = new ExamTimer();
        console.log('Exam timer loaded successfully');
    }
});

// Handle page visibility for timer accuracy
document.addEventListener('visibilitychange', function() {
    if (window.examTimer) {
        if (document.hidden) {
            // Page is hidden - could pause timer or continue running
            console.log('Page hidden - timer continues running');
        } else {
            // Page is visible - sync with server
            console.log('Page visible - syncing timer');
            window.examTimer.syncWithServer();
        }
    }
});

// Expose timer functions globally for debugging
window.timerDebug = {
    getTime: () => window.examTimer ? window.examTimer.getFormattedTime() : 'No timer',
    addTime: (seconds) => window.examTimer ? window.examTimer.addTime(seconds) : 'No timer',
    pause: () => window.examTimer ? window.examTimer.pause() : 'No timer',
    resume: () => window.examTimer ? window.examTimer.resume() : 'No timer'
};
