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