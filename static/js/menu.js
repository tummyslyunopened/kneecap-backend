function toggleMenu() {
  const menuContent = document.getElementById('menu-content');
  menuContent.classList.toggle('show');
  
  // Close the menu when clicking outside
  document.addEventListener('click', function closeMenu(e) {
    if (!e.target.matches('.menu-btn')) {
      menuContent.classList.remove('show');
      document.removeEventListener('click', closeMenu);
    }
  });
}
