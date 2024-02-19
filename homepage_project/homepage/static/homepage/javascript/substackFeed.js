if (window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log(`running substackFeed.js ... DOM content loaded`)


        // config. for substack feed widget
        window.SubstackFeedWidget = {
            substackUrl: 'matthewmcdonnell.substack.com',
            posts: 3
        };


        // Dynamically load the Substack script
        var substackScript = document.createElement('script');
        substackScript.src = 'https://substackapi.com/embeds/feed.js';
        substackScript.async = true;
        document.body.appendChild(substackScript);
    });
}