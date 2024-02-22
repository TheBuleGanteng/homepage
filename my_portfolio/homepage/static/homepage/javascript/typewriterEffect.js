if (window.location.pathname === '/') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log(`running typewriterEffect.js ... DOM content loaded`)
        
        const textElement = document.querySelector('.second-text');
        const words = ['observe', 'hypothesize', 'design', 'build', 'test', 'measure', 're-invent'];
        let currentWordIndex = 0;

        function typeWord(word, onComplete) {
            let i = 0; // i represents a counter
            const interval = setInterval(() => {
                textElement.textContent += word[i]; // Every time we pass this point, we add the letter at word[i] to the text in the container
                i++;
                if (i >= word.length) {
                    clearInterval(interval);
                    setTimeout(onComplete, 500); // Pause after each word is completed
                }
            }, 100); // Pause between each character
        }

        function startTyping() {
            if (currentWordIndex < words.length) {
                textElement.textContent = ''; // Clear the text element before typing next word
                typeWord(words[currentWordIndex], startTyping); // We pass 'startTyping' so that the 'startTyping' function runs when the following line is hit in the 'typeWord' function 'setTimeout(onComplete, 1000);'
                currentWordIndex++;
            }
        }

        startTyping(); // Start the typewriter effect
    });
}
