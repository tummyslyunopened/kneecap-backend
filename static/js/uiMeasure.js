export function findTopEpisodeElement() {
  const container = document.getElementById('episode-previews');
  if (!container) return null;
  const children = Array.from(container.children);
  let topEpisode = null;
  let topEpisodeDistance = Infinity;
  for (const child of children) {
    const rect = child.getBoundingClientRect();
    if (rect.top >= 0 && rect.top < topEpisodeDistance) {
      topEpisode = child;
      topEpisodeDistance = rect.top;
    }
  }
  return topEpisode;
}
