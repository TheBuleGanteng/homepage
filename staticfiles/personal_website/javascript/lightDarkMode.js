document.addEventListener('DOMContentLoaded', function() {
    console.log(`running lightDarkMode.js ... DOM content loaded`)

    // Toggle navbar class based on prefers-color-scheme
    function togglePageTheme() {
        console.log(`running lightDarkMode.js ... running togglePageTheme()`)
        
        // Creates variable 'userPrefersDark' and sets it to true or false based on the preferences detected.
        const userPrefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        console.log(`running lightDarkMode.js ... the value for userPrefersDark is ${ userPrefersDark }`)

        // Toggle theme for navbar
        const navbar = document.getElementById('navbar');
        if (userPrefersDark) {
        navbar.classList.remove('navbar-light', 'bg-light');
        navbar.classList.add('navbar-dark', 'bg-dark');
        } else {
        navbar.classList.remove('navbar-dark', 'bg-dark');
        navbar.classList.add('navbar-light', 'bg-light');
        }
    
        // Additional elements can be toggled here
        // For example, changing the page background and text color
        const body = document.body;
        if (userPrefersDark) {
        body.classList.add('dark-mode'); // Ensure .dark-mode class has the desired styles in CSS
        } else {
        body.classList.remove('dark-mode');
        }
    
        // You can continue to add more elements and their corresponding class changes here
    }
    
    // Call the function when the DOM is loaded
    togglePageTheme();
    
    // Listen for changes in color scheme preference
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
        togglePageTheme();
    });
});