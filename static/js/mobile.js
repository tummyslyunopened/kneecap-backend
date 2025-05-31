// Function to detect if the page is being displayed on a mobile device
function isMobileDevice() {
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    const isSmallScreen = window.innerWidth <= 768;
    const isMobileUserAgent = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    return isTouchDevice && (isSmallScreen || isMobileUserAgent);
}

// Apply red color to queue summary text if on a mobile device
document.addEventListener('DOMContentLoaded', () => {
    if (isMobileDevice()) {
        const queueSummary = document.querySelector('.queue-summary');
        if (queueSummary) {
            queueSummary.style.color = 'red';
        }
    }
});