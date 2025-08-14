/**
 * Exam Interface JavaScript
 * Handles exam functionality, navigation, answer submission, and anti-cheat measures
 */

class ExamManager {
    constructor() {
        this.sessionId = document.querySelector('meta[name="exam-session-id"]').content;
        this.totalQuestions = document.querySelectorAll('.question-card').length;
        this.answeredQuestions = new Set();
        this.currentQuestion = 1;
        this.tabSwitchCount = 0;
        this.examSubmitted = false;
        this.autoSaveInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updateNavigationButtons();
        this.updateProgress();
        this.startAutoSave();
        this.setupAntiCheat();
        this.scrollToFirstQuestion();
        
        console.log('Exam Manager initialized');
    }
    
    setupEventListeners() {
        // Question input change handlers
        document.querySelectorAll('.question-input').forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleAnswerChange(e);
            });
            
            // For text areas, also listen to input events for real-time saving
            if (input.tagName === 'TEXTAREA') {
                input.addEventListener('input', (e) => {
                    this.handleAnswerChange(e);
                });
            }
        });
        
        // Navigation button handlers
        document.querySelectorAll('.question-nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.navigateToQuestion(parseInt(e.target.dataset.questionNumber));
            });
        });
        
        // Submit button handler
        document.getElementById('submit-btn').addEventListener('click', (e) => {
            e.preventDefault();
            this.showSubmitConfirmation();
        });
        
        // Review button handler
        document.getElementById('review-btn').addEventListener('click', (e) => {
            this.showReviewMode();
        });
        
        // Modal confirmation handler
        document.getElementById('confirm-submit').addEventListener('click', (e) => {
            this.submitExam();
        });
        
        // Form submit handler
        document.getElementById('exam-form').addEventListener('submit', (e) => {
            if (!this.examSubmitted) {
                e.preventDefault();
                this.showSubmitConfirmation();
            }
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyNavigation(e);
        });
    }
    
    handleAnswerChange(event) {
        const input = event.target;
        const questionId = input.dataset.questionId;
        const answer = input.value;
        
        // Mark question as answered
        if (answer && answer.trim() !== '') {
            this.answeredQuestions.add(questionId);
        } else {
            this.answeredQuestions.delete(questionId);
        }
        
        // Update UI
        this.updateNavigationButtons();
        this.updateProgress();
        this.updateSubmitButton();
        
        // Auto-save answer
        this.saveAnswer(questionId, answer);
        
        console.log(`Answer changed for question ${questionId}:`, answer);
    }
    
    async saveAnswer(questionId, answer) {
        try {
            const response = await fetch(`/student/exam/session/${this.sessionId}/submit-answer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question_id: questionId,
                    answer: answer
                })
            });
            
            if (!response.ok) {
                throw new Error('Failed to save answer');
            }
            
            console.log(`Answer saved for question ${questionId}`);
        } catch (error) {
            console.error('Error saving answer:', error);
            // Show temporary error message
            this.showTempMessage('Failed to save answer. Please try again.', 'warning');
        }
    }
    
    navigateToQuestion(questionNumber) {
        const questionCard = document.getElementById(`question-${questionNumber}`);
        if (questionCard) {
            questionCard.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start',
                inline: 'nearest'
            });
            
            this.currentQuestion = questionNumber;
            this.updateNavigationButtons();
        }
    }
    
    updateNavigationButtons() {
        document.querySelectorAll('.question-nav-btn').forEach(btn => {
            const questionNumber = parseInt(btn.dataset.questionNumber);
            const questionId = btn.dataset.questionId || this.getQuestionIdByNumber(questionNumber);
            
            // Remove existing classes
            btn.classList.remove('answered', 'current');
            
            // Add appropriate classes
            if (this.answeredQuestions.has(questionId)) {
                btn.classList.add('answered');
            }
            
            if (questionNumber === this.currentQuestion) {
                btn.classList.add('current');
            }
        });
    }
    
    updateProgress() {
        const answeredCount = this.answeredQuestions.size;
        const progressPercentage = (answeredCount / this.totalQuestions) * 100;
        
        document.getElementById('progress-text').textContent = `${answeredCount} / ${this.totalQuestions}`;
        document.getElementById('progress-bar').style.width = `${progressPercentage}%`;
    }
    
    updateSubmitButton() {
        const submitBtn = document.getElementById('submit-btn');
        const reviewBtn = document.getElementById('review-btn');
        
        if (this.answeredQuestions.size > 0) {
            submitBtn.disabled = false;
            reviewBtn.disabled = false;
        } else {
            submitBtn.disabled = true;
            reviewBtn.disabled = true;
        }
    }
    
    showSubmitConfirmation() {
        const answeredCount = this.answeredQuestions.size;
        const unansweredCount = this.totalQuestions - answeredCount;
        
        document.getElementById('answered-count').textContent = answeredCount;
        
        // Update time remaining text
        const timeRemainingElement = document.getElementById('time-remaining-text');
        if (window.examTimer) {
            const timeLeft = window.examTimer.getTimeRemaining();
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timeRemainingElement.textContent = `Time remaining: ${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Show warning for unanswered questions
        if (unansweredCount > 0) {
            const warningDiv = document.createElement('div');
            warningDiv.className = 'alert alert-warning mt-2';
            warningDiv.innerHTML = `<strong>Warning:</strong> You have ${unansweredCount} unanswered question${unansweredCount > 1 ? 's' : ''}. These will be marked as incorrect.`;
            
            const existingWarning = document.querySelector('#submitModal .alert-warning');
            if (existingWarning) {
                existingWarning.remove();
            }
            
            document.querySelector('#submitModal .modal-body').appendChild(warningDiv);
        }
        
        const modal = new bootstrap.Modal(document.getElementById('submitModal'));
        modal.show();
    }
    
    showReviewMode() {
        // Scroll to top and highlight unanswered questions
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Highlight unanswered questions
        document.querySelectorAll('.question-card').forEach((card, index) => {
            const questionNumber = index + 1;
            const questionId = this.getQuestionIdByNumber(questionNumber);
            
            if (!this.answeredQuestions.has(questionId)) {
                card.classList.add('border-warning');
                setTimeout(() => {
                    card.classList.remove('border-warning');
                }, 3000);
            }
        });
        
        this.showTempMessage('Unanswered questions are highlighted in yellow.', 'info');
    }
    
    submitExam() {
        this.examSubmitted = true;
        
        // Stop auto-save
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
        
        // Stop timer
        if (window.examTimer) {
            window.examTimer.stop();
        }
        
        // Disable all inputs
        document.querySelectorAll('.question-input').forEach(input => {
            input.disabled = true;
        });
        
        // Show loading state
        const submitBtn = document.getElementById('confirm-submit');
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting...';
        submitBtn.disabled = true;
        
        // Submit the form
        document.getElementById('exam-form').submit();
    }
    
    startAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            // Auto-save is handled by individual answer changes
            console.log('Auto-save interval tick');
        }, 30000); // 30 seconds
    }
    
    setupAntiCheat() {
        let isVisible = true;
        
        // Tab/window visibility change detection
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && isVisible) {
                this.tabSwitchCount++;
                this.logTabSwitch();
                this.showTabSwitchWarning();
                isVisible = false;
            } else if (!document.hidden) {
                isVisible = true;
            }
        });
        
        // Window focus/blur events
        window.addEventListener('blur', () => {
            if (isVisible) {
                this.tabSwitchCount++;
                this.logTabSwitch();
            }
        });
        
        // Prevent right-click context menu
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
        });
        
        // Prevent common keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Prevent F12, Ctrl+Shift+I, Ctrl+U, etc.
            if (
                e.key === 'F12' ||
                (e.ctrlKey && e.shiftKey && e.key === 'I') ||
                (e.ctrlKey && e.shiftKey && e.key === 'C') ||
                (e.ctrlKey && e.key === 'u')
            ) {
                e.preventDefault();
                this.showTempMessage('This action is not allowed during the exam.', 'warning');
            }
        });
        
        console.log('Anti-cheat measures activated');
    }
    
    logTabSwitch() {
        console.log(`Tab switch detected. Count: ${this.tabSwitchCount}`);
        
        // Log to server (you could implement this)
        // this.sendTabSwitchLog();
    }
    
    showTabSwitchWarning() {
        if (this.tabSwitchCount <= 3) { // Only show for first few violations
            const modal = new bootstrap.Modal(document.getElementById('tabSwitchModal'));
            modal.show();
        }
    }
    
    handleKeyNavigation(event) {
        if (event.target.tagName === 'TEXTAREA' || event.target.tagName === 'INPUT') {
            return; // Don't interfere with text input
        }
        
        switch(event.key) {
            case 'ArrowUp':
                event.preventDefault();
                this.navigateToQuestion(Math.max(1, this.currentQuestion - 1));
                break;
            case 'ArrowDown':
                event.preventDefault();
                this.navigateToQuestion(Math.min(this.totalQuestions, this.currentQuestion + 1));
                break;
            case 'Enter':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.showSubmitConfirmation();
                }
                break;
        }
    }
    
    getQuestionIdByNumber(questionNumber) {
        const questionCard = document.querySelector(`.question-card:nth-child(${questionNumber})`);
        return questionCard ? questionCard.id.replace('question-', '') : null;
    }
    
    showTempMessage(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 120px; right: 20px; z-index: 1050; max-width: 400px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    scrollToFirstQuestion() {
        const firstQuestion = document.querySelector('.question-card');
        if (firstQuestion) {
            firstQuestion.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Public methods for external access
    getAnsweredCount() {
        return this.answeredQuestions.size;
    }
    
    getTotalQuestions() {
        return this.totalQuestions;
    }
    
    getTabSwitchCount() {
        return this.tabSwitchCount;
    }
}

// Initialize exam manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.examManager = new ExamManager();
    
    // Initialize feather icons
    feather.replace();
    
    console.log('Exam interface loaded successfully');
});

// Prevent page refresh/navigation without confirmation
window.addEventListener('beforeunload', function(e) {
    if (!window.examManager || !window.examManager.examSubmitted) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to leave? Your exam progress may be lost.';
        return e.returnValue;
    }
});
