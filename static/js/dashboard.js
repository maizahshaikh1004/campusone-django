document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlElement = document.documentElement;
    const body = document.body;

    // Set initial icon based on theme from documentElement
    if (htmlElement.classList.contains('dark-mode') || body.classList.contains('dark-mode')) {
        if (themeIcon) themeIcon.textContent = 'light_mode';
    } else {
        if (themeIcon) themeIcon.textContent = 'dark_mode';
    }

    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            htmlElement.classList.toggle('dark-mode');
            body.classList.toggle('dark-mode');
            
            if (htmlElement.classList.contains('dark-mode')) {
                if (themeIcon) themeIcon.textContent = 'light_mode';
                localStorage.setItem('theme', 'dark');
            } else {
                if (themeIcon) themeIcon.textContent = 'dark_mode';
                localStorage.setItem('theme', 'light');
            }
        });
    }
});
