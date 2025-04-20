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
    this.bindEvents();
    this.setupKeyboardShortcuts();
  }

  bindEvents() {
    this.playButton?.addEventListener('click', () => this.togglePlay());
    this.progressContainer?.addEventListener('click', (e) => this.seek(e));
    this.progressHandle?.addEventListener('mousedown', this.startDrag.bind(this));
    this.audio?.addEventListener('timeupdate', () => this.updateProgress());
    this.audio?.addEventListener('play', () => this.updatePlayState(true));
    this.audio?.addEventListener('pause', () => this.updatePlayState(false));
    this.audio?.addEventListener('ended', () => this.updatePlayState(false));
    document.querySelector('.skip-forward')?.addEventListener('click', () => this.skip(CONSTANTS.SKIP_TIME));
    document.querySelector('.skip-backward')?.addEventListener('click', () => this.skip(-CONSTANTS.SKIP_TIME));
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
      this.playButton.innerHTML = isPlaying ? '<p>Pause</p>' : '<p>Play</p>';
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
    this.audio.currentTime = Math.max(0, Math.min(this.audio.currentTime + seconds, this.audio.duration));
  }

  adjustVolume(delta) {
    if (!this.audio) return;
    this.audio.volume = Math.max(0, Math.min(1, this.audio.volume + delta));
  }
}



export default AudioPlayer;
