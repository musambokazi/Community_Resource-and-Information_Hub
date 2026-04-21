const toggleBtn = document.getElementById('theme-toggle');
const themeIcon = toggleBtn.querySelector('i');
const greetingEl = document.getElementById('greeting');
const searchBtn = document.getElementById('search-btn');
const searchInput = document.getElementById('search-input');

// Theme toggle with icon transition
toggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    
    // Add little animation to icon
    themeIcon.style.transform = 'scale(0) rotate(-180deg)';
    
    setTimeout(() => {
        if (document.body.classList.contains('dark-mode')) {
            themeIcon.classList.replace('ti-moon', 'ti-sun');
        } else {
            themeIcon.classList.replace('ti-sun', 'ti-moon');
        }
        themeIcon.style.transform = 'scale(1) rotate(0deg)';
    }, 150);
});

// Dynamic Greeting for a human touch based on the time of day
function setFriendlyGreeting() {
    const hour = new Date().getHours();
    let greeting = 'Welcome to our community.';
    
    if (hour >= 5 && hour < 12) {
        greeting = 'Good morning, neighbor.';
    } else if (hour >= 12 && hour < 18) {
        greeting = 'Good afternoon! How can we help?';
    } else if (hour >= 18 || hour < 5) {
        greeting = 'Good evening. Unwind and connect.';
    }
    
    if (greetingEl) {
        greetingEl.textContent = greeting;
    }
}

// Call on load
setFriendlyGreeting();

// Interactive search input validation
if (searchBtn && searchInput) {
    searchBtn.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            // Placeholder for a real search action
            const originalText = searchBtn.textContent;
            searchBtn.textContent = 'Searching...';
            setTimeout(() => {
                alert(`Looking for community resources related to: "${query}"...`);
                searchBtn.textContent = originalText;
                searchInput.value = '';
            }, 600);
        } else {
            // Soft shake animation if input is empty
            searchInput.focus();
            searchInput.parentElement.animate([
                { transform: 'translateX(0)' },
                { transform: 'translateX(-6px)' },
                { transform: 'translateX(6px)' },
                { transform: 'translateX(-3px)' },
                { transform: 'translateX(3px)' },
                { transform: 'translateX(0)' }
            ], { duration: 400, easing: 'ease-in-out' });
        }
    });

    // Enter key support
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });
}

function filterSelection(category) {
    const cards = document.getElementsByClassName('card'); // Selects all resource cards
    
    for (let i = 0; i < cards.length; i++) { // Loops through every card
        if (category === 'all') {
            cards[i].style.display = 'flex'; // Shows the card if 'all' is selected
        } else if (cards[i].classList.contains(category)) {
            cards[i].style.display = 'flex'; // Shows the card if the category matches
        } else {
            cards[i].style.display = 'none'; // Hides the card if it doesn't match
        }
    }
}

function findMe() {
    navigator.geolocation.getCurrentPosition((pos) => {
        const lat = pos.coords.latitude; // Gets your current latitude
        const lon = pos.coords.longitude; // Gets your current longitude
        alert(`Your location: ${lat}, ${lon}`); // Shows your location (for testing)
    });
}

function findNearbyResources() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const lat = position.coords.latitude; // User's real Latitude
            const lon = position.coords.longitude; // User's real Longitude
            
            // Send these coordinates to our Flask backend to get live data
            window.location.href = `/search?lat=${lat}&lon=${lon}`;
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Attach this function to your Search button
document.getElementById('search-btn').addEventListener('click', findNearbyResources);

function findNearby() {
    navigator.geolocation.getCurrentPosition((pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        // This forces the app to look right where the user is standing
        window.location.href = `/?lat=${lat}&lon=${lon}&range=5000`; // 5000 meters = 5km
    }, (err) => {
        alert("Please enable location to find nearest resources.");
    }, {
        enableHighAccuracy: true // This forces the GPS to be precise
    });
}