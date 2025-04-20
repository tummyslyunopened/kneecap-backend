import ApiService from './apiService.js';
import { CONSTANTS, state } from './base.js';
import { safeGetElement } from './utils.js';

class EpisodeManager {
  async hideEpisode(episodeId) {
    try {
      await ApiService.episodeMethod(CONSTANTS.API_URLS.HIDE_EPISODE, episodeId);
      const element = safeGetElement(episodeId);
      if (element) {
        element.remove();
        state.lastTopEpisode = null;
      }
    } catch (error) {
    }
  }

  async downloadEpisode(episodeId) {
    try {
      await ApiService.episodeMethod(CONSTANTS.API_URLS.DOWNLOAD_EPISODE, episodeId);
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
      await ApiService.episodeMethod(CONSTANTS.API_URLS.PLAY_EPISODE, episodeId);
      location.reload();
    } catch (error) {
    }
  }

  async hideAll() {
    try {
      await ApiService.post(CONSTANTS.API_URLS.HIDE_ALL_EPISODES);
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
      }
    } catch (error) {
    }
  }
}

export default EpisodeManager;
