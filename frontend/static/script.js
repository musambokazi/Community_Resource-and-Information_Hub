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
function filterSelection(c, btn) {
    var x = document.getElementsByClassName("card");
    
    // Manage active state on buttons if btn is passed
    if (btn) {
        var btns = document.getElementsByClassName("filter-btn");
        for (var j = 0; j < btns.length; j++) {
            btns[j].classList.remove("active");
        }
        btn.classList.add("active");
    }

    var filterC = c;
    if (c == "all") filterC = "";
    
    for (var i = 0; i < x.length; i++) {
        x[i].style.display = "none"; 
        if (c === "all") {
            // Show only nearest items for each category on "All" page
            if (x[i].className.indexOf("is-nearest") > -1 || x[i].className.indexOf("search-result") > -1) {
                x[i].style.display = "flex"; 
            }
        } else {
            // Specific category view: show all items matching category
            if (x[i].className.indexOf(filterC) > -1) {
                x[i].style.display = "flex"; 
            }
        }
    }
}

// Handle Enter key on search input
document.getElementById('search-input').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent form submission if it were in a form
        searchSpecificPlace();
    }
});

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

// Auto-scroll to results OR trigger initial location OR handle refresh
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const isReload = performance.getEntriesByType('navigation')[0].type === 'reload';

    // If it's a manual refresh/reload, go back to the clean front page
    if (isReload && window.location.search) {
        window.location.href = '/';
        return;
    }

    // If we have coordinates (and NOT a reload), scroll to results
    if (urlParams.has('lat') && urlParams.has('lon')) {
        const resultsSection = document.querySelector('.resource-grid');
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    } 
    // If we are on the home page and NO coordinates are present, trigger findNearby
    else if (window.location.pathname === '/' || window.location.pathname === '/find_specific') {
        if (!urlParams.has('lat')) {
             findNearby();
        }
    }
});
