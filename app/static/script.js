/**
 * Pure Vanilla JS Interactions
 * Emil Kowalski physics, A11y, and DOM manipulation without any frameworks.
 */

document.addEventListener('DOMContentLoaded', () => {
    
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const locationBtn = document.getElementById('location-btn');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const grid = document.getElementById('results-grid');
    const spinner = document.getElementById('loading-spinner');

    // -- Event Listeners --

    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', () => executeSearch(searchInput.value));
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') executeSearch(searchInput.value);
        });
    }

    if (locationBtn) {
        locationBtn.addEventListener('click', findNearby);
    }

    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // UI State
            filterBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            const target = e.currentTarget;
            target.classList.add('active');
            target.setAttribute('aria-pressed', 'true');
            
            // Re-fetch based on filter
            if (navigator.geolocation) {
                // In a real app we'd filter cached data, but for demo we re-fetch location
                findNearby(); 
            }
        });
    });

    // -- Favorite Button Delegation (For Dynamic Elements) --
    grid.addEventListener('click', (e) => {
        const favBtn = e.target.closest('.favorite-btn');
        if (favBtn) {
            e.stopPropagation(); // Prevent opening map
            const icon = favBtn.querySelector('i');
            
            // Toggle state
            const isPressed = favBtn.getAttribute('aria-pressed') === 'true';
            favBtn.setAttribute('aria-pressed', !isPressed);
            
            icon.classList.toggle('text-yellow-400');
            icon.classList.toggle('fill-yellow-400');
            
            // Micro-animation trigger via class manipulation
            favBtn.style.transform = 'scale(1.2)';
            setTimeout(() => favBtn.style.transform = 'scale(1)', 150);
        }
    });

    // -- Keyboard Navigation for Grid --
    grid.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const card = e.target.closest('article');
            if (card) {
                card.click();
            }
        }
    });

    // -- Core Functions --

    async function findNearby() {
        if (navigator.geolocation) {
            showLoading();
            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    await fetchAndRender(`/api/nearby?lat=${lat}&lon=${lon}`);
                },
                (error) => {
                    console.error("Geolocation error:", error);
                    hideLoading();
                    grid.innerHTML = '<p class="text-center text-red-400 col-span-full">Unable to retrieve location.</p>';
                }
            );
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    }

    async function executeSearch(query) {
        if (!query.trim()) return;
        showLoading();
        await fetchAndRender(`/api/search?q=${encodeURIComponent(query)}`);
    }

    async function fetchAndRender(url) {
        try {
            const res = await fetch(url);
            const data = await res.json();
            
            hideLoading();
            grid.innerHTML = '';

            if (data.success && data.data && data.data.length > 0) {
                // Determine active filter
                const activeFilter = document.querySelector('.filter-btn.active').dataset.filter;
                let results = data.data;
                if (activeFilter !== 'all') {
                    results = results.filter(r => r.category === activeFilter);
                }

                if (results.length === 0) {
                    grid.innerHTML = '<p class="text-center text-zinc-400 col-span-full py-12">No resources match this filter.</p>';
                    return;
                }

                results.forEach((resource, idx) => {
                    const delay = idx * 0.05; // Staggered delay
                    const cardHTML = `
                        <article tabindex="0" aria-label="Resource: ${resource.title}" class="glass-card rounded-3xl p-5 flex flex-col h-full spring-hover cursor-pointer opacity-0" style="animation: fadeInUp 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) ${delay}s forwards;" onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${resource.lat},${resource.lon}', '_blank')">
                            <div class="relative w-full h-48 rounded-2xl overflow-hidden mb-4 shrink-0 bg-zinc-800">
                                <img src="${resource.image}" alt="Photo of ${resource.title}" loading="lazy" decoding="async" class="w-full h-full object-cover transition-transform duration-500 card-img">
                                <button class="favorite-btn active-spring absolute top-3 right-3 p-2 bg-black/40 backdrop-blur-md rounded-full text-zinc-400 hover:text-yellow-400 transition-colors z-10 focus:outline-none focus:ring-2 focus:ring-primary" aria-label="Add ${resource.title} to favorites" aria-pressed="false">
                                    <i class="ti ti-star" aria-hidden="true"></i>
                                </button>
                            </div>
                            <h2 class="text-xl font-semibold tracking-tight mb-2 line-clamp-2 text-foreground">${resource.title}</h2>
                            <div class="flex items-center gap-2 mb-3">
                                <span class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-background border border-border text-xs font-medium">
                                    <div class="w-2 h-2 rounded-full ${resource.is_open ? 'bg-green-500' : 'bg-red-500'}" aria-hidden="true"></div>
                                    ${resource.is_open ? 'Open Now' : 'Closed'}
                                </span>
                            </div>
                            <p class="text-zinc-400 text-sm mb-6 flex-grow leading-relaxed line-clamp-3">${resource.desc}</p>
                        </article>
                    `;
                    grid.insertAdjacentHTML('beforeend', cardHTML);
                });
            } else {
                grid.innerHTML = '<p class="text-center text-zinc-400 col-span-full py-12">No resources found.</p>';
            }
        } catch (err) {
            console.error("Fetch error:", err);
            hideLoading();
            grid.innerHTML = '<p class="text-center text-red-400 col-span-full py-12">Failed to load resources. Please try again.</p>';
        }
    }

    function showLoading() {
        grid.innerHTML = '';
        spinner.classList.remove('hidden');
        spinner.classList.add('flex');
    }

    function hideLoading() {
        spinner.classList.add('hidden');
        spinner.classList.remove('flex');
    }
});
