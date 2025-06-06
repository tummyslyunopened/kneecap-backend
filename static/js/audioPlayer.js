import { CONSTANTS, state } from './base.js';
import ApiService from './apiService.js';
import { safeGetElement } from './utils.js';

/**
 * AudioPlayer class handles all audio playback functionality
 */
class AudioPlayer {
  constructor() {
    this.audio = document.getElementById('player-audio');
    
    this.progressContainer = document.querySelector('.progress-container');
    this.progressBar = document.querySelector('.progress-bar');
    this.progressHandle = document.querySelector('.progress-handle');
    this.currentTime = document.querySelector('.current-time');
    this.duration = document.querySelector('.duration');
    this.playButton = document.querySelector('.play-button');
    
    // Playback rate controls
    this.increasePlaybackRateButton = document.querySelector('.increase-playback-rate');
    this.decreasePlaybackRateButton = document.querySelector('.decrease-playback-rate');

    this.errorCount = 0;
    this.maxRetries = 3;
    this.lastSeekTime = 0;
    this.updateInterval = null;
    
    this.bindEvents();
    this.setupKeyboardShortcuts();
  }
  
  /**
   * Start the update interval for playback time logging
   */
  startUpdateInterval() {
    this.updateInterval = setInterval(() => {
      if (this.audio && !this.audio.paused) {
        this.logPlaybackTime();
      }
    }, 100); // Update every 100ms for smoother progress updates
  }
  
  /**
   * Stop the update interval
   */
  stopUpdateInterval() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }
  

  bindEvents() {
    // Playback controls
    this.playButton?.addEventListener('click', () => {
      this.togglePlay();
    });
    
    this.progressContainer?.addEventListener('click', (e) => {
      this.seek(e);
    });
    
    this.progressHandle?.addEventListener('mousedown', this.startDrag.bind(this));
    
    // Playback rate controls
    const handleRateIncrease = () => {
      this.adjustPlaybackRate(0.25);
    };
    
    const handleRateDecrease = () => {
      this.adjustPlaybackRate(-0.25);
    };
    
    if (this.increasePlaybackRateButton) {
      this.increasePlaybackRateButton.addEventListener('click', handleRateIncrease);
    }
    
    if (this.decreasePlaybackRateButton) {
      this.decreasePlaybackRateButton.addEventListener('click', handleRateDecrease);
    }
    
    // Audio element events
    const events = [
      ['timeupdate', () => this.updateProgress()],
      ['play', () => {
        this.updatePlayState(true);
        this.startUpdateInterval();
      }],
      ['pause', () => {
        this.updatePlayState(false);
        this.stopUpdateInterval();
      }],
      ['ended', () => {
        this.updatePlayState(false);
        this.stopUpdateInterval();
      }],
      ['error', (e) => this.handleError(e)],
      ['seeked', () => this.handleSeek()]
    ];
    
    events.forEach(([event, handler]) => {
      this.audio?.addEventListener(event, handler);
    });
    
    // Navigation controls
    document.querySelector('.skip-forward')?.addEventListener('click', () => this.skip(CONSTANTS.SKIP_TIME));
    document.querySelector('.skip-backward')?.addEventListener('click', () => this.skip(-CONSTANTS.SKIP_TIME));
  }

  handleError(event) {
    console.error('Audio error:', event);
    this.errorCount++;
    if (this.errorCount < this.maxRetries) {
      // Try to recover by seeking back a bit
      this.audio.currentTime = Math.max(0, this.audio.currentTime - 10);
    } else {
      // If too many errors, pause and alert
      this.audio.pause();
      alert('Audio playback error. Please refresh the page and try again.');
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
    const currentTime = this.audio ? this.audio.currentTime : 0;
    state.currentTime = currentTime;
    return currentTime;
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
  }

  adjustVolume(change) {
    if (!this.audio) return;
    this.audio.volume = Math.min(1, Math.max(0, this.audio.volume + change));
  }

  /**
   * Adjusts the playback rate by the specified increment
   * @param {number} increment - The amount to adjust the playback rate by (can be positive or negative)
   */
  adjustPlaybackRate(increment) {
    if (!this.audio) {
      return;
    }
    
    // Define the range of allowed playback rates
    const minRate = 0.5;
    const maxRate = 3.0;
    const step = 0.25;
    
    // Calculate new rate and round to nearest step to avoid floating point precision issues
    let newRate = Math.round((this.audio.playbackRate + increment) / step) * step;
    
    // Clamp the value within allowed range
    newRate = Math.min(maxRate, Math.max(minRate, newRate));
    
    // Only update if rate has changed
    if (newRate !== this.audio.playbackRate) {
      this.audio.playbackRate = newRate;
      this.updatePlaybackRateDisplay();
    } else {
      console.log('Playback rate unchanged');
    }
  }

  /**
   * Updates the UI to reflect the current playback rate
   */
  updatePlaybackRateDisplay() {
    console.log('Updating playback rate display');
    
    if (!this.audio) {
      console.error('No audio element for rate display');
      return;
    }
    
    // Update any UI elements that show playback rate
    const rateDisplay = document.querySelector('.playback-rate-display');
    console.log('Rate display element:', rateDisplay);
    
    if (rateDisplay) {
      const rateText = `${this.audio.playbackRate.toFixed(2)}x`;
      console.log('Setting rate display text to:', rateText);
      rateDisplay.textContent = rateText;
    } else {
      console.warn('No element with class "playback-rate-display" found');
    }
  }

  /**
   * Logs the current playback time to the server
   * @private
   */
  async logPlaybackTime() {
    if (!this.audio) {
      console.warn('Audio player not found when attempting to log playback time');
      return;
    }
    
    const currentTime = this.audio.currentTime;
    if (typeof currentTime !== 'number' || isNaN(currentTime)) {
      console.warn('Invalid time detected for audioPlayer:', currentTime);
      return;
    }

    const hasBeenPlaying = state.isPlaying && state.lastRecordedIsPlaying;
    const hasActuallyChanged = currentTime !== state.lastRecordedPlaybackTime;

    if (hasBeenPlaying && !hasActuallyChanged) {
      console.warn('Suspected Failure to load remote adudio File. Playback is not changing over last log period.');
      return;
    }
    
    // Update playback rate in state
    state.playbackRate = this.audio.playbackRate;
    safeGetElement('playback-rate-label').textContent = `${state.playbackRate}x`;
    state.lastRecordedPlaybackTime = currentTime;

    
    if (Math.abs(currentTime - state.lastSentPlaybackTime) >= CONSTANTS.PLAYBACK_LOG_INTERVAL) {
      state.lastSentPlaybackTime = currentTime;
      state.lastRecordedIsPlaying = state.isPlaying;
      console.info('Current playback:', {
        time: currentTime,
        rate: state.playbackRate
      });
      
      // Use silent mode to suppress toast notifications
      await ApiService.post(
        CONSTANTS.API_URLS.SET_PLAYBACK_TIME, 
        { 'currentTime': currentTime },
        { 
          showSuccess: false, 
          showError: true,
        }
      );
    }
  }
}

export default AudioPlayer;
