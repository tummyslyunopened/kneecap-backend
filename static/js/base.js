const episodeTitleSelector = '[id^="episode-title-"]';
const maxEpisodeTitleWidth = 375; //px
const episodeTitleMarqueeSpeed = 95; //px /s
const marqueeFocusTimeDelay = 1; // s

let lastTopEpisode = null; // Keep a memory of the last topEpisode element

function hide(id) {
  let el = document.getElementById(id);
  el.style.display = "none";
}

function topElement(selector) {
  const elements = document.querySelectorAll(selector); // Select elements with IDs starting with 'episode-title-'
  let topEpisode = null;
  let topEpisodeDistance = Infinity;

  elements.forEach(element => {
    const rect = element.getBoundingClientRect();
    const distance = rect.top; // Distance from the top of the viewport
    if (distance >= 0 && distance < topEpisodeDistance) {
      topEpisodeDistance = distance;
      topEpisode = element;
    }
  });
  console.log(topEpisode)
  return topEpisode
}

function getMarqueeKeyframeParams(distance, speed, delay){
 let animationTime = distance / speed
 let totalTime = 2*delay + animationTime
 let beginAnimationPercentage = 100 * delay / totalTime
 let endAnimationPercentage = beginAnimationPercentage + 100 * animationTime / totalTime 
 return {
  distance:distance,
  totalTime:totalTime,
  beginAnimationPercentage:beginAnimationPercentage,
  endAnimationPercentage:endAnimationPercentage
 }
}

function marqueeTitle(){
 console.log("attempting title marquee") 
 console.log(episodeTitleSelector)  
 topEpisode = topElement(episodeTitleSelector)
  if (topEpisode) {
    // If the topEpisode element is different from the last closest, reset the last closest
    if (lastTopEpisode && lastTopEpisode !== topEpisode) {
      lastTopEpisode.style.color = ''; // Reset text color
      lastTopEpisode.style.whiteSpace = ''; // Allow text to wrap again
      lastTopEpisode.style.overflow = ''; // Show overflow again
      lastTopEpisode.style.position = ''; // Reset position
      lastTopEpisode.style.animation = ''; // Stop animation
    }
    const titleWidth = topEpisode.offsetWidth;
    if (titleWidth > maxEpisodeTitleWidth) {
      let overflowWidth = titleWidth - maxEpisodeTitleWidth
      marqueeParams = getMarqueeKeyframeParams(overflowWidth, episodeTitleMarqueeSpeed, marqueeFocusTimeDelay)

      topEpisode.style.color = 'red'; // Change text color to red if width is greater than 500px
      topEpisode.style.whiteSpace = 'nowrap'; // Prevent text from wrapping
      topEpisode.style.overflow = 'hidden'; // Hide overflow
      topEpisode.style.position = 'relative'; // Set position for animation
      // Create a dynamic keyframe animation
      const keyframes = `
        @keyframes scroll-left {
          0% {
            transform: translateX(0); /* Start from the initial position */
          }
          ${marqueeParams.beginAnimationPercentage}% {
            transform: translateX(0); /* Start from the initial position */
          }
          ${marqueeParams.endAnimationPercentage}% {
            transform: translateX(-${marqueeParams.distance}px); /* Scroll to the left based on text width */
          }
          100% {
            transform: translateX(-${marqueeParams.distance}px); /* Scroll to the left based on text width */
          }
        }
      `;
      // Append the keyframes to a <style> element
      const styleSheet = document.createElement("style");
      styleSheet.type = "text/css";
      styleSheet.innerText = keyframes;
      document.head.appendChild(styleSheet);
      topEpisode.style.animation = 'scroll-left ' + (marqueeParams.totalTime) + 's linear infinite';
      lastTopEpisode = topEpisode;
    }
  }
}

// Add scroll event listener to run findtopEpisodeEpisode on scroll
window.addEventListener('scroll', marqueeTitle);
