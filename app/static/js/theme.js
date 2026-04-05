document.addEventListener('DOMContentLoaded', function() {
    const themeSelect = document.getElementById('theme-select');
    const savedTheme = localStorage.getItem('theme') || 'dark';
    
    document.documentElement.setAttribute('data-theme', savedTheme);
    if (themeSelect) {
        themeSelect.value = savedTheme;
    }
    
    if (themeSelect) {
        themeSelect.addEventListener('change', function() {
            const theme = this.value;
            document.documentElement.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });
    }
});
