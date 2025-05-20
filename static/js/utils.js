export function debounce(func, wait) {
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

export function safeGetElement(id) {
  const element = document.getElementById(id);
  return element;
}

export function logState(state, title = 'State') {
    const stateEntries = Object.entries(state);
    const maxLength = Math.max(...stateEntries.map(([key]) => key.length));
    
    console.groupCollapsed(`%c${title}`,'color: #9b51e0; font-weight: bold;');
    console.log('%cTimestamp:', 'color: #666;', new Date().toLocaleTimeString());
    console.log('%c---', 'color: #666;');
    
    stateEntries.forEach(([key, value]) => {
        const padding = ' '.repeat(maxLength - key.length);
        console.log(`%c${key}${padding}:`, 'color: #9b51e0;', value);
    });
    
    console.groupEnd();
}

/**
 * Displays a toast notification
 * @param {string} message - The message to display
 * @param {string} type - The type of toast (success, error, warning, info)
 * @param {number} [duration=5000] - Duration in milliseconds to show the toast
 */
export function showToast(message, type = 'info', duration = 5000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-width: 350px;
        `;
        document.body.appendChild(toastContainer);
    }

    // Create toast element
    const toast = document.createElement('div');
    const toastId = `toast-${Date.now()}`;
    toast.id = toastId;
    
    // Set styles based on type
    const typeStyles = {
        success: {
            background: '#4caf50',
            icon: '✓',
        },
        error: {
            background: '#f44336',
            icon: '!',
        },
        warning: {
            background: '#ff9800',
            icon: '⚠️',
        },
        info: {
            background: '#2196f3',
            icon: 'ℹ️',
        },
    };

    const style = typeStyles[type] || typeStyles.info;
    
    toast.style.cssText = `
        background: ${style.background};
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        opacity: 0;
        transform: translateX(100%);
        transition: opacity 0.3s ease, transform 0.3s ease;
        cursor: pointer;
    `;

    // Add icon
    const icon = document.createElement('span');
    icon.textContent = style.icon;
    icon.style.fontSize = '18px';
    
    // Add message
    const messageElement = document.createElement('span');
    messageElement.textContent = message;
    messageElement.style.flex = '1';
    
    // Add close button
    const closeButton = document.createElement('span');
    closeButton.textContent = '×';
    closeButton.style.cssText = `
        font-size: 20px;
        cursor: pointer;
        opacity: 0.8;
        margin-left: 10px;
        line-height: 1;
    `;
    closeButton.onclick = () => removeToast(toastId);
    
    // Assemble toast
    toast.appendChild(icon);
    toast.appendChild(messageElement);
    toast.appendChild(closeButton);
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto-remove after duration
    if (duration > 0) {
        const timeoutId = setTimeout(() => {
            removeToast(toastId);
        }, duration);
        
        // Pause auto-removal on hover
        toast.addEventListener('mouseenter', () => {
            clearTimeout(timeoutId);
        });
        
        // Resume auto-removal when mouse leaves
        toast.addEventListener('mouseleave', () => {
            setTimeout(() => removeToast(toastId), 1000);
        });
    }
    
    // Click to dismiss
    toast.addEventListener('click', (e) => {
        if (e.target === toast || e.target === messageElement) {
            removeToast(toastId);
        }
    });
    
    function removeToast(id) {
        const toastToRemove = document.getElementById(id);
        if (toastToRemove) {
            toastToRemove.style.opacity = '0';
            toastToRemove.style.transform = 'translateX(100%)';
            
            // Remove from DOM after animation
            setTimeout(() => {
                if (toastToRemove.parentNode) {
                    toastToRemove.parentNode.removeChild(toastToRemove);
                    
                    // Remove container if no more toasts
                    if (toastContainer && toastContainer.children.length === 0) {
                        document.body.removeChild(toastContainer);
                    }
                }
            }, 300);
        }
    }
}