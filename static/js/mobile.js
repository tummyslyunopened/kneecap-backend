// Export the isMobileDevice function to make it available as a module
export function isMobileDevice() {
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    const isSmallScreen = window.innerWidth <= 768;
    const isMobileUserAgent = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    return isTouchDevice && (isSmallScreen || isMobileUserAgent);
}
