document.addEventListener('DOMContentLoaded', function() {
    console.log(`running googleAnalytics.js ... DOM content loaded`)

    // Below is JS to run google analytics
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-62CJ8QX96T');

});