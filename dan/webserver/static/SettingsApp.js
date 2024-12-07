//SettingsApp.js
document.addEventListener('DOMContentLoaded', () => {
  // Button to toggle theme
  const modeButton = document.getElementById('toggle-theme');
  modeButton.textContent = 'Light Mode';  // Display as light mode button (even though only light mode is used)

  // Navigation logic for settings menu
  const menuItems = document.querySelectorAll('.settings-menu a');
  const sections = document.querySelectorAll('.settings-content');

  menuItems.forEach(item => {
    item.addEventListener('click', (event) => {
      event.preventDefault();

      const targetSectionId = item.getAttribute('data-section');

      sections.forEach(section => section.classList.add('hidden'));

      const targetSection = document.getElementById(targetSectionId);
      if (targetSection) targetSection.classList.remove('hidden');
    });
  });

  // Check for existing username in localStorage
  const userName = localStorage.getItem('username');
  if (userName) {
    console.log('Hey there, ' + userName);
    document.getElementById('chat-container').classList.remove('hidden');
  } else {
    window.location.href = 'index.html';
  }
});



