if (window.location.pathname === '/') {
        console.log(`running substackFeed.js ... DOM content loaded`)
        
        // config. for substack feed widget
        window.SubstackFeedWidget = {
            substackUrl: 'matthewmcdonnell.substack.com',
            posts: 3
        };
        
}