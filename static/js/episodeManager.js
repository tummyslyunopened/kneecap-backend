import ApiService from './apiService.js';
import { CONSTANTS, state } from './base.js';
import { safeGetElement } from './utils.js';

class EpisodeManager {
  constructor() {
    this.updateInterval = null;
  }

  async hideEpisode(episodeId) {
    try {
      await ApiService.idMethod(CONSTANTS.API_URLS.HIDE_EPISODE, episodeId);
      const element = safeGetElement(episodeId);
      if (element) {
        element.remove();
        state.lastTopEpisode = null;
        this.updateQueueDuration();
      }
    } catch (error) {
    }
  }

  async downloadEpisode(episodeId) {
    try {
      await ApiService.idMethod(CONSTANTS.API_URLS.DOWNLOAD_EPISODE, episodeId);
      const button = safeGetElement(`episode-download-btn-${episodeId}`);
      if (button) {
        button.disabled = true;
        button.innerHTML = "Queued";
      }
    } catch (error) {
    }
  }

  async playEpisode(episodeId) {
    try {
      await ApiService.idMethod(CONSTANTS.API_URLS.PLAY_EPISODE, episodeId);
      location.reload();
    } catch (error) {
    }
  }

  async hideAll() {
    try {
      await ApiService.post(CONSTANTS.API_URLS.HIDE_ALL_EPISODES);
      this.updateQueueDuration();
      location.reload();
    } catch (error) {
    }
  }

  async refreshFeed() {
    try {
      await ApiService.post(CONSTANTS.API_URLS.REFRESH_SUBSCRIPTIONS);
      location.reload();
    } catch (error) {
    }
  }

  async toggleChron() {
    try {
      await ApiService.post(CONSTANTS.API_URLS.TOGGLE_CHRONOLOGICAL);
      const container = safeGetElement('episode-previews');
      if (container) {
        const children = Array.from(container.children);
        container.innerHTML = '';
        children.reverse().forEach(child => container.appendChild(child));
        window.scrollTo(0, 0);
        state.lastScrollTime = Date.now() + 5000;
        this.updateQueueDuration();
      }
    } catch (error) {
    }
  }

  async toggleAutoplay() {
    try {
      await ApiService.post(CONSTANTS.API_URLS.TOGGLE_AUTOPLAY);
      const toggle = document.getElementById('autoplay-toggle');
      state.isAutoplayEnabled = toggle.checked;
    } catch (error) {
    }
  }

  /**
   * Calculate and update the total duration of all episodes in the queue
   */
  updateQueueDuration() {
    const durationElements = document.querySelectorAll('.episode-info');
    let totalDuration = 0;

    durationElements.forEach(element => {
      // Find the duration string (starts with ⏲️)
      const durationStr = element.textContent.split('⏲️')[1]?.trim();
      // console.log(durationStr)
      if (durationStr && durationStr !== '0') {
        const [hours, minutes, seconds] = durationStr.split(':').map(str => {
          const num = Number(str);
          return isNaN(num) ? 0 : num;
        });
        totalDuration += hours * 3600 + minutes * 60 + seconds;
      }
    });

    totalDuration -= Math.floor(state.currentTime)

    // Convert total seconds to HH:MM:SS format
    const hours = Math.floor(totalDuration / 3600);
    const minutes = Math.floor((totalDuration % 3600) / 60);
    const seconds = Math.floor(totalDuration % 60);

    const formattedDuration = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

    // Update the queue summary display
    const queueSummary = document.querySelector('.queue-summary h2');
    if (queueSummary) {
      queueSummary.textContent = formattedDuration;
    }
  }

  /**
   * Start the interval to update queue duration
   */
  startUpdateInterval() {
    if (this.updateInterval) return;
    this.updateInterval = setInterval(() => {
      this.updateQueueDuration();
    }, 1000); // Update every second
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
}

export default EpisodeManager;
