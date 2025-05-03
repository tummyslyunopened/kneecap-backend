import { CONSTANTS, state } from './base.js';

class AudioPlayer {
  constructor() {
    this.audio = document.getElementById('player-audio');
    this.progressContainer = document.querySelector('.progress-container');
    this.progressBar = document.querySelector('.progress-bar');
    this.progressHandle = document.querySelector('.progress-handle');
    this.currentTime = document.querySelector('.current-time');
    this.duration = document.querySelector('.duration');
    this.playButton = document.querySelector('.play-button');
    this.errorCount = 0;
    this.maxRetries = 3;
    this.lastSeekTime = 0;
    this.lastMemoryCheck = 0;
    this.memoryCheckInterval = 30000; // 30 seconds
    this.memoryUsageHistory = [];
    this.bindEvents();
    this.setupKeyboardShortcuts();
    this.startMemoryMonitoring();
  }

  startMemoryMonitoring() {
    // Start memory monitoring every 30 seconds
    setInterval(() => this.checkMemoryUsage(), this.memoryCheckInterval);
  }

  checkMemoryUsage() {
    if (!performance || !performance.memory) return;
    
    const now = Date.now();
    if (now - this.lastMemoryCheck < this.memoryCheckInterval) return;
    this.lastMemoryCheck = now;

    const memory = {
      timestamp: now,
      usedJSHeapSize: performance.memory.usedJSHeapSize,
      totalJSHeapSize: performance.memory.totalJSHeapSize,
      jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
    };

    this.memoryUsageHistory.push(memory);
    if (this.memoryUsageHistory.length > 10) {
      this.memoryUsageHistory.shift(); // Keep only last 10 measurements
    }

    // Log memory stats if they're getting too high
    const usedPercentage = (memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100;
    if (usedPercentage > 80) {
      console.warn('High memory usage detected:', memory);
      this.logMemoryHistory();
    }
  }

  logMemoryHistory() {
    console.log('Memory usage history (last 10 measurements):');
    this.memoryUsageHistory.forEach((mem, index) => {
      const usedPercentage = (mem.usedJSHeapSize / mem.jsHeapSizeLimit) * 100;
      console.log(`[${index}] Time: ${new Date(mem.timestamp).toLocaleTimeString()}, ` +
                 `Used: ${Math.round(usedPercentage)}% (${Math.round(mem.usedJSHeapSize / 1024 / 1024)}MB)`);
    });
  }

  bindEvents() {
    this.playButton?.addEventListener('click', () => this.togglePlay());
    this.progressContainer?.addEventListener('click', (e) => this.seek(e));
    this.progressHandle?.addEventListener('mousedown', this.startDrag.bind(this));
    this.audio?.addEventListener('timeupdate', () => this.updateProgress());
    this.audio?.addEventListener('play', () => this.updatePlayState(true));
    this.audio?.addEventListener('pause', () => this.updatePlayState(false));
    this.audio?.addEventListener('ended', () => this.updatePlayState(false));
    this.audio?.addEventListener('error', (e) => this.handleError(e));
    this.audio?.addEventListener('seeked', () => this.handleSeek());
    document.querySelector('.skip-forward')?.addEventListener('click', () => this.skip(CONSTANTS.SKIP_TIME));
    document.querySelector('.skip-backward')?.addEventListener('click', () => this.skip(-CONSTANTS.SKIP_TIME));
  }

  handleError(event) {
    console.error('Audio error:', event);
    this.errorCount++;
    if (this.errorCount < this.maxRetries) {
      // Try to recover by seeking back a bit
      this.audio.currentTime = Math.max(0, this.audio.currentTime - 10);
      // Log memory state when error occurs
      this.logMemoryHistory();
    } else {
      // If too many errors, pause and alert
      this.audio.pause();
      alert('Audio playback error. Please refresh the page and try again.');
      // Log final memory state
      this.logMemoryHistory();
    }
  }

  handleSeek() {
    const currentTime = this.audio.currentTime;
    const lastTime = this.lastSeekTime;
    
    // If we're seeking back, reset error count
    if (currentTime < lastTime) {
      this.errorCount = 0;
    }
    this.lastSeekTime = currentTime;
  }

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      switch (e.key) {
        case CONSTANTS.KEYBOARD_SHORTCUTS.PLAY_PAUSE:
          e.preventDefault();
          this.togglePlay();
          break;
        case CONSTANTS.KEYBOARD_SHORTCUTS.SKIP_FORWARD:
          this.skip(CONSTANTS.SKIP_TIME);
          break;
        case CONSTANTS.KEYBOARD_SHORTCUTS.SKIP_BACKWARD:
          this.skip(-CONSTANTS.SKIP_TIME);
          break;
        case CONSTANTS.KEYBOARD_SHORTCUTS.VOLUME_UP:
          this.adjustVolume(0.1);
          break;
        case CONSTANTS.KEYBOARD_SHORTCUTS.VOLUME_DOWN:
          this.adjustVolume(-0.1);
          break;
      }
    });
  }

  togglePlay() {
    if (!this.audio) return;
    if (this.audio.paused) {
      this.audio.play();
    } else {
      this.audio.pause();
    }
  }

  updatePlayState(isPlaying) {
    state.isPlaying = isPlaying;
    if (this.playButton) {
      this.playButton.innerHTML = isPlaying ? 
      `<svg width="40" height="40" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M36 24.0468V20.0468C36 17.8376 34.2091 16.0468 32 16.0468L24 16.0468C21.7909 16.0468 20 17.8376 20 20.0468V24.0468L20 56.2339V60.2339C20 62.443 21.7909 64.2339 24 64.2339H32C34.2091 64.2339 36 62.443 36 60.2339L36 56.2339L36 24.0468ZM60 24.0468V20.0468C60 17.8376 58.2091 16.0468 56 16.0468L48 16.0468C45.7909 16.0468 44 17.8376 44 20.0468V24.0468L44 56.2339V60.2339C44 62.443 45.7909 64.2339 48 64.2339H56C58.2091 64.2339 60 62.443 60 60.2339V56.2339L60 24.0468Z" fill="#9B51E0" />
        <path d="M36 24.0468L38 24.0468L36 24.0468ZM36 56.2339H38H38H36ZM44 24.0468H46H44ZM44 56.2339L42 56.2339L44 56.2339ZM34 20.0468V24.0468L38 24.0468V20.0468H34ZM24 18.0468L32 18.0468V14.0468L24 14.0468V18.0468ZM22 24.0468V20.0468H18V24.0468H22ZM22 56.2339L22 24.0468H18L18 56.2339H22ZM22 60.2339V56.2339H18V60.2339H22ZM32 62.2339H24V66.2339H32V62.2339ZM34 56.2339L34 60.2339H38V56.2339H34ZM34 24.0468L34 56.2339H38L38 24.0468L34 24.0468ZM58 20.0468V24.0468H62V20.0468H58ZM48 18.0468L56 18.0468V14.0468L48 14.0468V18.0468ZM46 24.0468V20.0468H42V24.0468H46ZM46 56.2339L46 24.0468H42L42 56.2339L46 56.2339ZM46 60.2339V56.2339L42 56.2339V60.2339L46 60.2339ZM56 62.2339H48V66.2339H56V62.2339ZM58 56.2339V60.2339H62V56.2339H58ZM58 24.0468L58 56.2339H62L62 24.0468H58ZM56 66.2339C59.3137 66.2339 62 63.5476 62 60.2339H58C58 61.3385 57.1046 62.2339 56 62.2339V66.2339ZM48 14.0468C44.6863 14.0468 42 16.733 42 20.0468H46C46 18.9422 46.8954 18.0468 48 18.0468V14.0468ZM62 20.0468C62 16.733 59.3137 14.0468 56 14.0468V18.0468C57.1046 18.0468 58 18.9422 58 20.0468H62ZM32 66.2339C35.3137 66.2339 38 63.5476 38 60.2339H34C34 61.3385 33.1046 62.2339 32 62.2339V66.2339ZM42 60.2339C42 63.5476 44.6863 66.2339 48 66.2339V62.2339C46.8954 62.2339 46 61.3385 46 60.2339L42 60.2339ZM24 14.0468C20.6863 14.0468 18 16.733 18 20.0468H22C22 18.9422 22.8954 18.0468 24 18.0468V14.0468ZM18 60.2339C18 63.5476 20.6863 66.2339 24 66.2339V62.2339C22.8954 62.2339 22 61.3385 22 60.2339H18ZM38 20.0468C38 16.733 35.3137 14.0468 32 14.0468V18.0468C33.1046 18.0468 34 18.9422 34 20.0468H38Z" fill="#9B51E0" />
      </svg>` : 
      `<svg width="40" height="40" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <g transform="scale(-1,1) translate(-80,0)">
              <path
                  d="M26.1333 38.4C25.0667 39.2 25.0667 40.8 26.1333 41.6L52.8 61.6C54.1185 62.5889 55 61.6481 55 60L55 20C55 18.3519 54.1185 17.4111 52.8 18.4L26.1333 38.4Z"
                  fill="#9B51E0" stroke="#9B51E0" stroke-width="4" stroke-linecap="square" stroke-linejoin="round" />
          </g>
      </svg>`;
    }
  }

  updateProgress() {
    if (!this.audio || !this.progressBar || !this.progressHandle) return;
    const progress = (this.audio.currentTime / this.audio.duration) * 100;
    this.progressBar.style.width = `${progress}%`;
    this.progressHandle.style.left = `${progress}%`;
    if (this.currentTime) {
      this.currentTime.textContent = this.formatTime(this.audio.currentTime);
    }
    if (this.duration) {
      this.duration.textContent = this.formatTime(this.audio.duration);
    }
  }

  formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  getCurrentTime() {
    return this.audio ? this.audio.currentTime : 0;
  }

  setTime(time) {
    if (this.audio && !isNaN(time)) {
      this.audio.currentTime = time;
    }
  }

  seek(e) {
    if (!this.audio || !this.progressContainer) return;
    const rect = this.progressContainer.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    this.audio.currentTime = pos * this.audio.duration;
  }

  startDrag(e) {
    const handleDrag = (e) => {
      this.seek(e);
    };
    const stopDrag = () => {
      document.removeEventListener('mousemove', handleDrag);
      document.removeEventListener('mouseup', stopDrag);
    };
    document.addEventListener('mousemove', handleDrag);
    document.addEventListener('mouseup', stopDrag);
  }

  skip(seconds) {
    if (!this.audio) return;
    const newTime = Math.max(0, Math.min(this.audio.currentTime + seconds, this.audio.duration));
    this.audio.currentTime = newTime;
    // Reset error count when skipping
    this.errorCount = 0;
    // Log memory usage when skipping
    this.checkMemoryUsage();
  }

  adjustVolume(delta) {
    if (!this.audio) return;
    this.audio.volume = Math.max(0, Math.min(1, this.audio.volume + delta));
  }
}



export default AudioPlayer;
