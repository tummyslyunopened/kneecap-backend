import { state } from "./base.js";
import { safeGetElement } from "./utils.js";

export class TranscriptManager {
    constructor() {
        this.updateInterval = null;
    }

    async showTranscript() {
        const container = safeGetElement('transcript-container');
        if (container) {
            container.style.display = 'block';
            const closeBtn = safeGetElement('close-transcript');
            if (closeBtn) closeBtn.style.display = 'block';
            const showBtn = safeGetElement('show-transcript');
            if (showBtn) showBtn.style.display = "none";
            state.transcript_visible = true;
            this.startUpdateInterval();
        }
    }

    async hideTranscript() {
        const container = safeGetElement('transcript-container');
        if (container) {
            container.style.display = 'none';
            const closeBtn = safeGetElement('close-transcript');
            if (closeBtn) closeBtn.style.display = 'none';
            const showBtn = safeGetElement('show-transcript');
            if (showBtn) showBtn.style.display = "block";
            state.transcript_visible = false;
            this.stopUpdateInterval();
        }
    }

    startUpdateInterval() {
        if (this.updateInterval) return;
        this.updateInterval = setInterval(() => {
            if (state.transcript_visible) {
                this.styleActiveTranscriptSegment();
            }
        }, 1000); // Changed interval to 1000ms (1s) to avoid high CPU usage
    }

    stopUpdateInterval() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async styleActiveTranscriptSegment() {
        const currentTime = state.lastRecordedPlaybackTime;
        const transcriptContainer = safeGetElement('transcript-container');
        if (!transcriptContainer) {
            return;
        }
        const segments = transcriptContainer.querySelectorAll('.transcript-segment');
        segments.forEach(segment => {
            segment.classList.remove('segment-active');
        });
        let activeSegment = null;
        segments.forEach(segment => {
            const startTime = parseFloat(segment.querySelector('.transcript-start-time').textContent);
            const endTime = parseFloat(segment.querySelector('.transcript-end-time').textContent);
            if (currentTime >= startTime && currentTime < endTime) {
                activeSegment = segment;
                segment.classList.add('segment-active');
            }
        });
        if (activeSegment) {
            const container = activeSegment.closest('.transcript-container');
            if (container) {
                const segmentRect = activeSegment.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                const segmentTop = segmentRect.top - containerRect.top;
                const segmentBottom = segmentRect.bottom - containerRect.top;
                const isSegmentInView = segmentTop >= 0 && segmentBottom <= container.offsetHeight;
                if (!isSegmentInView) {
                    const newScrollTop = container.scrollTop + segmentTop - (container.offsetHeight / 3);
                    setTimeout(() => {
                        container.scrollTo({
                            top: newScrollTop,
                            behavior: 'smooth'
                        });
                    }, 100);
                }
            }
        }
    }
}



export default TranscriptManager;