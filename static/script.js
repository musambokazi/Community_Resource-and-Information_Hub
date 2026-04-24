// Function to get high-accuracy location and reload the page
function findNearby() {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            window.location.href = `/?lat=${lat}&lon=${lon}`;
        },
        (err) => {
            // This is the "Fallback" if GPS fails
            alert("Location blocked. Using default area (Springs). Please allow location in browser settings.");
            window.location.href = `/?lat=-26.2500&lon=28.4333`;
        },
        { enableHighAccuracy: true, timeout: 5000 }
    );
}

// Category Filter Function
function filterSelection(c) {
    var x = document.getElementsByClassName("card");
    if (c == "all") c = "";
    for (var i = 0; i < x.length; i++) {
        x[i].style.display = "none"; 
        if (x[i].className.indexOf(c) > -1) {
            x[i].style.display = "flex"; 
        }
    }
}

// Attach the location finder to your Search button
document.getElementById('search-btn').addEventListener('click', findNearby);

function searchSpecificPlace() {
    const query = document.getElementById('search-input').value;
    if (query) {
        // We get your location first so the search is local to you
        navigator.geolocation.getCurrentPosition((pos) => {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            window.location.href = `/find_specific?name=${query}&lat=${lat}&lon=${lon}`;
        });
    }
}

// Hook it up to the existing search button
document.getElementById('search-btn').addEventListener('click', searchSpecificPlace);

const toggleBtn = document.getElementById('theme-toggle');
const themeIcon = toggleBtn.querySelector('i');

// 1. Function to set the theme
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme); // Remembers for next time
    
    // Update icon
    if (theme === 'dark') {
        themeIcon.classList.replace('ti-moon', 'ti-sun');
    } else {
        themeIcon.classList.replace('ti-sun', 'ti-moon');
    }
}

// 2. Check Device Settings & Local Storage on Load
const savedTheme = localStorage.getItem('theme');
const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

if (savedTheme) {
    setTheme(savedTheme);
} else if (systemDark) {
    setTheme('dark');
}

// 3. Handle the Click
toggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
});

// 4. Listen for System Changes (Optional but cool)
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
    if (!localStorage.getItem('theme')) { // Only change if user hasn't manualy picked
        setTheme(e.matches ? 'dark' : 'light');
    }
});

