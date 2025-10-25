// Fake Account Detector - JavaScript
// LITE CODERS

document.addEventListener('DOMContentLoaded', function() {
    // Animate trust score circle on result page
    const scoreCircle = document.querySelector('.score-circle');

    if (scoreCircle) {
        animateTrustScore(scoreCircle);
    }

    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';

    // Enhance form submission with loading state
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = 'Analyzing... ⏳';
                submitButton.style.opacity = '0.7';
            }
        });
    }

    // Add hover effects to feature items
    const featureItems = document.querySelectorAll('.feature-item');
    featureItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });

        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Animate reasons list on scroll
    observeElements('.reasons-list li', 'fadeInUp');

    // Add copy functionality to username
    const profileHeader = document.querySelector('.profile-header h2');
    if (profileHeader) {
        profileHeader.style.cursor = 'pointer';
        profileHeader.title = 'Click to copy username';

        profileHeader.addEventListener('click', function() {
            const username = this.textContent;
            copyToClipboard(username);
            showNotification('Username copied!');
        });
    }
});

/**
 * Animate trust score circle with color gradient
 */
function animateTrustScore(scoreCircle) {
    const score = parseInt(scoreCircle.getAttribute('data-score'));
    const percentage = (score / 1000) * 100;

    // Determine color based on score ranges
    let gradientColor;
    if (score >= 800) {
        gradientColor = '#10b981'; // Green - High trust
    } else if (score >= 600) {
        gradientColor = '#3b82f6'; // Blue - Good trust
    } else if (score >= 400) {
        gradientColor = '#f59e0b'; // Orange - Medium trust
    } else if (score >= 200) {
        gradientColor = '#ef4444'; // Red - Low trust
    } else {
        gradientColor = '#dc2626'; // Dark red - Very low trust
    }

    // Animate the circle gradient
    let currentPercentage = 0;
    const animationDuration = 1500; // 1.5 seconds
    const steps = 60;
    const increment = percentage / steps;
    const stepDuration = animationDuration / steps;

    const animation = setInterval(() => {
        currentPercentage += increment;

        if (currentPercentage >= percentage) {
            currentPercentage = percentage;
            clearInterval(animation);
        }

        scoreCircle.style.background = `conic-gradient(${gradientColor} ${currentPercentage}%, rgba(139, 92, 246, 0.2) ${currentPercentage}%)`;
    }, stepDuration);

    // Add pulse animation for very low or very high scores
    if (score >= 800 || score <= 200) {
        scoreCircle.style.animation = 'pulse 2s infinite';
    }
}

/**
 * Observe elements and add animation class when visible
 */
function observeElements(selector, animationClass) {
    const elements = document.querySelectorAll(selector);

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add(animationClass);
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        elements.forEach(element => {
            observer.observe(element);
        });
    }
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
        document.body.removeChild(textArea);
    }
}

/**
 * Show notification toast
 */
function showNotification(message) {
    // Remove existing notification if any
    const existingNotification = document.querySelector('.notification-toast');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.className = 'notification-toast';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        font-weight: 500;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 2000);
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
            box-shadow: 0 8px 30px rgba(139, 92, 246, 0.3);
        }
        50% {
            transform: scale(1.05);
            box-shadow: 0 12px 40px rgba(139, 92, 246, 0.5);
        }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    .fadeInUp {
        animation: fadeInUp 0.6s ease backwards;
    }

    .reasons-list li:nth-child(1) { animation-delay: 0.1s; }
    .reasons-list li:nth-child(2) { animation-delay: 0.2s; }
    .reasons-list li:nth-child(3) { animation-delay: 0.3s; }
    .reasons-list li:nth-child(4) { animation-delay: 0.4s; }
    .reasons-list li:nth-child(5) { animation-delay: 0.5s; }
    .reasons-list li:nth-child(6) { animation-delay: 0.6s; }
`;
document.head.appendChild(style);

// Add input validation and real-time feedback
const inputField = document.querySelector('input[name="profile_url"]');
if (inputField) {
    inputField.addEventListener('input', function(e) {
        const value = e.target.value.trim();

        // Check if input matches Twitter/X URL pattern
        const twitterPattern = /^(https?:\/\/)?(www\.)?(twitter\.com|x\.com)\/[a-zA-Z0-9_]+\/?$/;

        if (value && !twitterPattern.test(value) && !value.startsWith('@')) {
            this.style.borderColor = 'rgba(239, 68, 68, 0.6)';
        } else {
            this.style.borderColor = 'rgba(167, 139, 250, 0.4)';
        }
    });

    // Auto-format username input
    inputField.addEventListener('blur', function(e) {
        let value = e.target.value.trim();

        // If user entered just username without @ or URL
        if (value && !value.includes('twitter.com') && !value.includes('x.com') && !value.startsWith('@')) {
            this.value = `https://twitter.com/${value}`;
        }
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus on input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const input = document.querySelector('input[name="profile_url"]');
        if (input) {
            input.focus();
        }
    }
});

// Console easter egg
console.log('%c🛡️ Who-Are-You? Fake Account Detector', 'font-size: 20px; font-weight: bold; color: #8b5cf6;');
console.log('%cBuilt with ❤️ by LITE CODERS', 'font-size: 14px; color: #a78bfa;');
console.log('%cAI-Powered Social Media Account Analysis', 'font-size: 12px; color: #c4b5fd;');
