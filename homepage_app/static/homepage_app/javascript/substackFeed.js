if (window.location.pathname === '/') {
    console.log('running substackFeed.js ... DOM content loaded');

    fetch('/fetch-substack-rss')
        .then(response => response.json())
        .then(data => {
            const articlesDiv = document.getElementById('substack-feed-embed');
            data.articles.forEach((article, index, articlesArray) => {
                const articleContainer = document.createElement('div');
                articleContainer.className = 'article-container';
                articleContainer.style.display = 'flex'; // Use flexbox
                articleContainer.style.alignItems = 'flex-start'; // Align items to start of the flex container
                articleContainer.style.cursor = 'pointer';
                articleContainer.style.backgroundColor = 'var(--bs-gray-dark)';
                // Add bottom border to all but the last article div
                if (index !== articlesArray.length - 1) {
                    articleContainer.style.borderBottom = '1px solid lightgrey';
                }
                articleContainer.style.padding = '1em';
                articleContainer.style.fontFamily = 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"';
                articleContainer.style.fontWeight = '300'; // Set font weight for the container
                articleContainer.onclick = () => window.open(article.link, '_blank');
                
                const textContainer = document.createElement('div'); // Container for text
                textContainer.style.flex = '1'; // Take up remaining space

                const title = document.createElement('h5');
                title.textContent = article.title;

                const description = document.createElement('p');
                description.textContent = article.description;

                const author = document.createElement('div');
                author.textContent = article.author;

                const pubDate = document.createElement('div');
                pubDate.textContent = new Date(article.pubDate).toLocaleDateString('en-UK', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });

                const articleImage = document.createElement('div');
                articleImage.className = 'article-image';
                articleImage.style.flexShrink = '0'; // Prevent the image from shrinking
                articleImage.style.marginLeft = '0em'; // Space to the left of the image
                if (article.image) {
                    articleImage.style.backgroundImage = `url('${article.image}')`;
                    articleImage.style.width = '125px'; // Fixed width for the image
                    articleImage.style.height = '125px';
                    articleImage.style.backgroundSize = 'cover';
                    articleImage.style.backgroundPosition = 'center';
                }

                textContainer.appendChild(title);
                textContainer.appendChild(description);
                textContainer.appendChild(author);
                textContainer.appendChild(pubDate);
                
                articleContainer.appendChild(textContainer); // Add text container first
                if (article.image) {
                    articleContainer.appendChild(articleImage); // Add image next
                }

                articlesDiv.appendChild(articleContainer);
            });
        })
        .catch(error => console.error('Error:', error));
}
