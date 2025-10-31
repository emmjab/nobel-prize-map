// Initialize map
let map = L.map('map').setView([30, 0], 2);
let workMarkers = []; // Always visible work location markers
let laureateData = []; // Store birth markers and connections for each laureate
let currentLaureates = [];
let activeHighlightElements = []; // Currently visible birth markers and connection lines
let laureateToMarkerMap = {}; // Map laureate index to work marker
let currentHighlightedMarker = null; // Currently highlighted marker
let currentSelectedLaureateIndex = null; // Currently selected laureate index
let locationGroups = []; // Store location groups for updating popups
let currentCategory = null; // Currently selected category

// Category color scheme (matching table view)
const CATEGORY_COLORS = {
    'physics': '#667eea',       // Purple
    'chemistry': '#f093fb',     // Pink/Magenta
    'medicine': '#4facfe',      // Light Blue
    'literature': '#43e97b',    // Green
    'peace': '#fa709a',         // Pink
    'economics': '#feca57'      // Yellow
};

// Category display names
const CATEGORY_NAMES = {
    'physics': 'Physics',
    'chemistry': 'Chemistry',
    'medicine': 'Physiology or Medicine',
    'literature': 'Literature',
    'peace': 'Peace',
    'economics': 'Economic Sciences'
};

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
}).addTo(map);

// Helper function to generate Wikipedia URL from laureate name
function getWikipediaUrl(name) {
    // Replace spaces with underscores and encode special characters
    const wikiName = name.trim().replace(/ /g, '_');
    return `https://en.wikipedia.org/wiki/${encodeURIComponent(wikiName)}`;
}

// Custom marker icons
const workIcon = L.divIcon({
    className: 'custom-marker',
    html: '<div style="background-color: #667eea; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
    iconSize: [24, 24],
    iconAnchor: [12, 12]
});

const birthIcon = L.divIcon({
    className: 'custom-marker',
    html: '<div style="background-color: #48bb78; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>',
    iconSize: [20, 20],
    iconAnchor: [10, 10]
});

// Category selector
const categorySelect = document.getElementById('category-select');
const laureateInfo = document.getElementById('laureate-info');
const infoTitle = document.getElementById('info-title');

// Search elements
const searchContainer = document.getElementById('search-container');
const laureateSearch = document.getElementById('laureate-search');
const searchSuggestions = document.getElementById('search-suggestions');

// Function to update dropdown background color based on selected category
function updateDropdownColor(category) {
    if (category === 'all') {
        categorySelect.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        categorySelect.style.color = 'white';
    } else if (category === 'economics') {
        categorySelect.style.background = CATEGORY_COLORS[category];
        categorySelect.style.color = '#333';
    } else if (CATEGORY_COLORS[category]) {
        categorySelect.style.background = CATEGORY_COLORS[category];
        categorySelect.style.color = 'white';
    } else {
        categorySelect.style.background = 'white';
        categorySelect.style.color = '#333';
    }
}

// Function to update legend work marker color
function updateLegendWorkMarker() {
    const legendMarker = document.getElementById('legend-work-marker');
    if (!legendMarker) return;

    // If viewing a specific category (not 'all'), use that category's color
    if (currentCategory && currentCategory !== 'all' && CATEGORY_COLORS[currentCategory]) {
        legendMarker.style.background = CATEGORY_COLORS[currentCategory];
        legendMarker.style.backgroundImage = 'none';
    }
    // If viewing 'all categories', always use rainbow gradient
    else if (currentCategory === 'all') {
        legendMarker.style.background = '';
        legendMarker.style.backgroundImage = `conic-gradient(
            #667eea 0deg 60deg,
            #f093fb 60deg 120deg,
            #4facfe 120deg 180deg,
            #43e97b 180deg 240deg,
            #fa709a 240deg 300deg,
            #feca57 300deg 360deg
        )`;
    }
    // Default state
    else {
        legendMarker.style.background = '#667eea';
        legendMarker.style.backgroundImage = 'none';
    }
}

// Function to show/hide search bar based on category
function updateSearchVisibility() {
    if (currentCategory === 'all') {
        searchContainer.style.display = 'flex';
    } else {
        searchContainer.style.display = 'none';
        laureateSearch.value = '';
        searchSuggestions.classList.remove('show');
    }
}

// Function to filter laureates based on search query
function filterLaureates(query) {
    if (!query || query.length < 2) {
        return [];
    }

    const lowerQuery = query.toLowerCase();
    return currentLaureates
        .map((laureate, index) => ({ laureate, index }))
        .filter(({ laureate }) => laureate.name.toLowerCase().includes(lowerQuery))
        .slice(0, 10); // Limit to 10 suggestions
}

// Function to display search suggestions
function displaySuggestions(matches) {
    if (matches.length === 0) {
        searchSuggestions.classList.remove('show');
        return;
    }

    searchSuggestions.innerHTML = matches.map(({ laureate, index }) => `
        <div class="search-suggestion-item" data-index="${index}">
            <div class="search-suggestion-name">${laureate.name}</div>
            <div class="search-suggestion-details">
                ${CATEGORY_NAMES[laureate.category] || laureate.category} • ${laureate.prize_year} • ${laureate.work_location}
            </div>
        </div>
    `).join('');

    searchSuggestions.classList.add('show');

    // Add click handlers to suggestion items
    searchSuggestions.querySelectorAll('.search-suggestion-item').forEach(item => {
        item.addEventListener('click', () => {
            const index = parseInt(item.dataset.index);
            selectLaureateFromSearch(index);
        });
    });
}

// Function to select a laureate from search
function selectLaureateFromSearch(index) {
    laureateSearch.value = currentLaureates[index].name;
    searchSuggestions.classList.remove('show');
    highlightLaureate(index);
}

categorySelect.addEventListener('change', async (e) => {
    const category = e.target.value;

    if (!category) {
        resetView();
        return;
    }

    // Update dropdown color
    updateDropdownColor(category);

    try {
        const response = await fetch(`/api/laureates/${category}`);
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        displayLaureates(data);
    } catch (error) {
        console.error('Error fetching laureates:', error);
        alert('Failed to load laureate data');
    }
});

// Search input event listener
laureateSearch.addEventListener('input', (e) => {
    const query = e.target.value;
    const matches = filterLaureates(query);
    displaySuggestions(matches);
});

// Close suggestions when clicking outside
document.addEventListener('click', (e) => {
    if (!searchContainer.contains(e.target)) {
        searchSuggestions.classList.remove('show');
    }
});

// Handle keyboard navigation in search
laureateSearch.addEventListener('keydown', (e) => {
    const items = searchSuggestions.querySelectorAll('.search-suggestion-item');
    const activeItem = searchSuggestions.querySelector('.search-suggestion-item.active');
    let currentIndex = -1;

    if (activeItem) {
        currentIndex = Array.from(items).indexOf(activeItem);
    }

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (currentIndex < items.length - 1) {
            if (activeItem) activeItem.classList.remove('active');
            items[currentIndex + 1].classList.add('active');
        }
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (currentIndex > 0) {
            if (activeItem) activeItem.classList.remove('active');
            items[currentIndex - 1].classList.add('active');
        }
    } else if (e.key === 'Enter') {
        e.preventDefault();
        if (activeItem) {
            const index = parseInt(activeItem.dataset.index);
            selectLaureateFromSearch(index);
        } else if (items.length > 0) {
            const index = parseInt(items[0].dataset.index);
            selectLaureateFromSearch(index);
        }
    } else if (e.key === 'Escape') {
        searchSuggestions.classList.remove('show');
    }
});

function resetView() {
    laureateInfo.innerHTML = '<p class="placeholder">Select a category to explore Nobel Prize winners</p>';
    infoTitle.textContent = 'Laureates';
    unhighlightMarker();
    clearMap();
    map.setView([30, 0], 2);
    updateLegendWorkMarker();
}

function clearMap() {
    // Remove work markers
    workMarkers.forEach(marker => map.removeLayer(marker));
    workMarkers = [];

    // Clear active highlight elements
    clearActiveHighlights();

    // Clear stored laureate data
    laureateData = [];

    // Clear marker mapping and highlighted marker
    laureateToMarkerMap = {};
    currentHighlightedMarker = null;
    currentSelectedLaureateIndex = null;
    locationGroups = [];
}

// Group laureates by location (with a small threshold for "same location")
function groupLaureatesByLocation(laureates, locationType = 'work') {
    const threshold = 0.1; // Consider locations within this range as "same"
    const groups = [];

    laureates.forEach((laureate, index) => {
        const lat = locationType === 'work' ? laureate.work_lat : laureate.birth_lat;
        const lon = locationType === 'work' ? laureate.work_lon : laureate.birth_lon;

        // Find existing group for this location
        let group = groups.find(g => {
            const latDiff = Math.abs(g.lat - lat);
            const lonDiff = Math.abs(g.lon - lon);
            return latDiff < threshold && lonDiff < threshold;
        });

        if (!group) {
            // Create new group
            group = {
                lat: lat,
                lon: lon,
                laureates: [],
                indices: [],
                categories: new Set() // Track unique categories in this group
            };
            groups.push(group);
        }

        group.laureates.push(laureate);
        group.indices.push(index);
        if (laureate.category) {
            group.categories.add(laureate.category);
        }
    });

    return groups;
}

// Get the color for a marker based on category
function getMarkerColor(category = null) {
    // If a specific category is provided (from 'all' view or group category), use it
    if (category && CATEGORY_COLORS[category]) {
        return CATEGORY_COLORS[category];
    }
    // If viewing a single category (not 'all'), use that category's color
    if (currentCategory && currentCategory !== 'all' && CATEGORY_COLORS[currentCategory]) {
        return CATEGORY_COLORS[currentCategory];
    }
    // Default to purple
    return '#667eea';
}

// Create a custom marker icon with optional number badge
function createWorkIcon(count, highlighted = false, category = null, isMultiCategory = false) {
    const hasMultiple = count > 1;
    const numberBadge = hasMultiple
        ? `<div style="position: absolute; top: -8px; right: -8px; background-color: #f56565; color: white; border-radius: 50%; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${count}</div>`
        : '';

    const size = 24;
    const boxShadow = '0 2px 4px rgba(0,0,0,0.3)';

    let markerStyle;
    if (isMultiCategory && currentCategory === 'all') {
        // Rainbow gradient for mixed categories in 'all' view (using matching table colors)
        markerStyle = `background: conic-gradient(
            #667eea 0deg 60deg,
            #f093fb 60deg 120deg,
            #4facfe 120deg 180deg,
            #43e97b 180deg 240deg,
            #fa709a 240deg 300deg,
            #feca57 300deg 360deg
        );`;
    } else {
        markerStyle = `background-color: ${getMarkerColor(category)};`;
    }

    // Add black center dot if highlighted
    const centerDot = highlighted
        ? `<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 8px; height: 8px; border-radius: 50%; background-color: black;"></div>`
        : '';

    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="position: relative;">
                <div style="${markerStyle} width: ${size}px; height: ${size}px; border-radius: 50%; border: 3px solid white; box-shadow: ${boxShadow};"></div>
                ${centerDot}
                ${numberBadge}
            </div>`,
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2]
    });
}

// Highlight a marker
function highlightMarker(marker, count, category = null, isMultiCategory = false) {
    if (currentHighlightedMarker) {
        unhighlightMarker();
    }

    const highlightedIcon = createWorkIcon(count, true, category, isMultiCategory);
    marker.setIcon(highlightedIcon);
    currentHighlightedMarker = { marker, count, category, isMultiCategory };
    updateLegendWorkMarker();
}

// Unhighlight the current marker
function unhighlightMarker() {
    if (currentHighlightedMarker) {
        const normalIcon = createWorkIcon(
            currentHighlightedMarker.count,
            false,
            currentHighlightedMarker.category,
            currentHighlightedMarker.isMultiCategory
        );
        currentHighlightedMarker.marker.setIcon(normalIcon);
        currentHighlightedMarker = null;
    }
    updateLegendWorkMarker();
}

function displayLaureates(data) {
    currentLaureates = data.laureates;
    currentCategory = categorySelect.value; // Store the current category
    infoTitle.textContent = `${data.category} Laureates`;

    // Sort laureates by prize year (oldest to newest)
    currentLaureates.sort((a, b) => a.prize_year - b.prize_year);

    // Clear previous content
    laureateInfo.innerHTML = '';
    clearMap();

    if (currentLaureates.length === 0) {
        laureateInfo.innerHTML = '<p class="placeholder">No laureates found</p>';
        return;
    }

    // Create laureate cards and prepare data
    currentLaureates.forEach((laureate, index) => {
        const card = createLaureateCard(laureate, index);
        laureateInfo.appendChild(card);

        // Store birth markers/connections (hidden until selected)
        prepareLaureateData(laureate, index);
    });

    // Group laureates by work location and store globally
    locationGroups = groupLaureatesByLocation(currentLaureates, 'work');

    // Create one marker per location group
    locationGroups.forEach(group => {
        // For 'all' category, check if there are multiple categories at this location
        const isMultiCategory = group.categories.size > 1;
        const markerCategory = group.categories.size === 1
            ? Array.from(group.categories)[0]
            : null;

        const icon = createWorkIcon(group.laureates.length, false, markerCategory, isMultiCategory);
        const workMarker = L.marker([group.lat, group.lon], { icon: icon });

        // Store marker reference with count, category, and multi-category flag for each laureate in this group
        group.indices.forEach(index => {
            laureateToMarkerMap[index] = {
                marker: workMarker,
                count: group.laureates.length,
                group: group,
                category: markerCategory,
                isMultiCategory: isMultiCategory
            };
        });

        // Create popup content showing all laureates at this location
        workMarker.bindPopup(createGroupPopupContent(group, null));

        // Click handler
        workMarker.on('click', () => {
            if (group.indices.length === 1) {
                // Single laureate - highlight them
                highlightLaureate(group.indices[0]);
            } else {
                // Multiple laureates - clear any previous laureate selection and just highlight the marker
                clearActiveHighlights();
                currentSelectedLaureateIndex = null;

                // Remove active class from all cards
                document.querySelectorAll('.laureate-card').forEach(card => {
                    card.classList.remove('active');
                });

                highlightMarker(workMarker, group.laureates.length, markerCategory, isMultiCategory);

                // Update popup to show no specific laureate is selected
                const newPopupContent = createGroupPopupContent(group, null);
                workMarker.setPopupContent(newPopupContent);
            }
        });

        workMarker.addTo(map);
        workMarkers.push(workMarker);
    });

    // Fit map to show all work markers
    if (workMarkers.length > 0) {
        const group = L.featureGroup(workMarkers);
        map.fitBounds(group.getBounds().pad(0.1));
    }

    // Update legend work marker color
    updateLegendWorkMarker();

    // Update search bar visibility
    updateSearchVisibility();
}

function createLaureateCard(laureate, index) {
    const div = document.createElement('div');
    div.className = 'laureate-card';
    div.dataset.index = index;
    div.dataset.laureateId = laureate.laureate_id;

    const sharedText = laureate.shared_with.length > 0
        ? `Shared with: ${laureate.shared_with.map(id => {
            const coLaureate = currentLaureates.find(l => l.laureate_id === id);
            return coLaureate ? `<a href="#" class="co-laureate-link" data-laureate-id="${id}">${coLaureate.name}</a>` : '';
        }).join(', ')}`
        : 'Solo prize';

    const wikiUrl = getWikipediaUrl(laureate.name);

    // Show category badge only when viewing "All Categories"
    const categoryBadge = currentCategory === 'all' && laureate.category && CATEGORY_NAMES[laureate.category]
        ? `<div class="laureate-category category-${laureate.category}">${CATEGORY_NAMES[laureate.category]}</div>`
        : '';

    div.innerHTML = `
        <div class="laureate-name">
            ${laureate.name}
            <a href="${wikiUrl}" target="_blank" rel="noopener noreferrer" class="wiki-link" title="View Wikipedia page">📖</a>
        </div>
        ${categoryBadge}
        <div class="laureate-year">Nobel Prize ${laureate.prize_year}</div>
        <div class="laureate-achievement">${laureate.achievement}</div>
        <div class="laureate-locations">
            <div class="location-item">
                <span class="location-icon">🎂</span>
                <span>Born: ${laureate.birth_location}</span>
            </div>
            <div class="location-item">
                <span class="location-icon">🔬</span>
                <span>Work: ${laureate.work_location} (${laureate.work_years})</span>
            </div>
        </div>
        ${laureate.shared_with.length > 0 ? `<div class="shared-info">${sharedText}</div>` : ''}
    `;

    div.addEventListener('click', (e) => {
        // Don't trigger if clicking on a co-laureate link or wiki link
        if (!e.target.classList.contains('co-laureate-link') && !e.target.classList.contains('wiki-link')) {
            highlightLaureate(index);
        }
    });

    // Add click handlers to co-laureate links
    div.querySelectorAll('.co-laureate-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const laureateId = e.target.dataset.laureateId;
            const targetIndex = currentLaureates.findIndex(l => l.laureate_id === laureateId);
            if (targetIndex !== -1) {
                highlightLaureate(targetIndex);
            }
        });
    });

    return div;
}

function prepareLaureateData(laureate, index) {
    // Prepare data for this laureate (birth marker, connections) but don't add to map yet
    const data = {
        birthMarker: null,
        birthToWorkLine: null,
        prizeConnections: []
    };

    // Create birth marker if different from work location (but don't add to map)
    if (laureate.birth_lat !== laureate.work_lat || laureate.birth_lon !== laureate.work_lon) {
        const birthMarker = L.marker([laureate.birth_lat, laureate.birth_lon], { icon: birthIcon });
        birthMarker.bindPopup(createPopupContent(laureate, 'birth'));
        birthMarker.on('click', () => highlightLaureate(index));
        data.birthMarker = birthMarker;

        // Create line from birth to work location (but don't add to map)
        const birthToWorkLine = L.polyline(
            [[laureate.birth_lat, laureate.birth_lon], [laureate.work_lat, laureate.work_lon]],
            {
                color: '#48bb78',
                weight: 2,
                opacity: 0.4,
                dashArray: '5, 5'
            }
        );
        data.birthToWorkLine = birthToWorkLine;
    }

    // Create connection lines to co-laureates (but don't add to map)
    if (laureate.shared_with.length > 0) {
        laureate.shared_with.forEach(coLaureateId => {
            const coLaureate = currentLaureates.find(l => l.laureate_id === coLaureateId);
            if (coLaureate) {
                const connectionLine = L.polyline(
                    [[laureate.work_lat, laureate.work_lon], [coLaureate.work_lat, coLaureate.work_lon]],
                    {
                        color: '#764ba2',
                        weight: 3,
                        opacity: 0.5,
                        dashArray: '10, 5'
                    }
                );
                data.prizeConnections.push(connectionLine);
            }
        });
    }

    laureateData[index] = data;
}

function createGroupPopupContent(group, selectedIndex) {
    const content = document.createElement('div');
    content.className = 'popup-content';

    if (group.laureates.length === 1) {
        // Single laureate - show full details
        const laureate = group.laureates[0];
        const coLaureateLinks = laureate.shared_with.length > 0
            ? laureate.shared_with.map(id => {
                const coLaureate = currentLaureates.find(l => l.laureate_id === id);
                return coLaureate ? `<a href="#" class="popup-link" data-laureate-id="${id}">${coLaureate.name}</a>` : '';
            }).join(', ')
            : '';

        const wikiUrl = getWikipediaUrl(laureate.name);
        const nameColor = laureate.category ? getMarkerColor(laureate.category) : '#667eea';

        content.innerHTML = `
            <div class="popup-name" style="color: ${nameColor};">
                ${laureate.name}
                <a href="${wikiUrl}" target="_blank" rel="noopener noreferrer" class="wiki-link" title="View Wikipedia page" style="margin-left: 5px;">📖</a>
            </div>
            <div class="popup-year">Nobel Prize ${laureate.prize_year}</div>
            <div class="popup-section">
                <div class="popup-label">Work Location:</div>
                <div class="popup-value">${laureate.work_location}</div>
                <div class="popup-label">Work Years:</div>
                <div class="popup-value">${laureate.work_years}</div>
            </div>
            <div class="popup-achievement">${laureate.achievement}</div>
            ${coLaureateLinks ? `<div class="popup-shared">Shared with: ${coLaureateLinks}</div>` : ''}
        `;
    } else {
        // Multiple laureates - show list
        const location = group.laureates[0].work_location;
        const laureatesList = group.laureates.map((laureate, i) => {
            const index = group.indices[i];
            const wikiUrl = getWikipediaUrl(laureate.name);
            const isSelected = selectedIndex !== null && index === selectedIndex;

            // Always use category color, but bold if selected
            const categoryColor = laureate.category ? getMarkerColor(laureate.category) : '#667eea';
            const fontWeight = isSelected ? 'bold' : 'normal';

            return `
                <div class="popup-laureate-item" style="padding: 8px 0; border-bottom: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <a href="#" class="popup-link" data-laureate-index="${index}" style="font-weight: ${fontWeight}; color: ${categoryColor}; text-decoration: none; flex: 1;">
                            ${laureate.name}
                        </a>
                        <a href="${wikiUrl}" target="_blank" rel="noopener noreferrer" class="wiki-link" title="View Wikipedia page" style="margin-left: 5px;">📖</a>
                    </div>
                    <div style="font-size: 12px; color: #718096; margin-top: 2px;">
                        Nobel Prize ${laureate.prize_year}
                    </div>
                </div>
            `;
        }).join('');

        content.innerHTML = `
            <div class="popup-name">${location}</div>
            <div style="font-size: 13px; color: #718096; margin-bottom: 10px;">
                ${group.laureates.length} laureates worked here
            </div>
            <div style="max-height: 300px; overflow-y: auto;">
                ${laureatesList}
            </div>
        `;
    }

    // Add click handlers to links in popup
    content.querySelectorAll('.popup-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (link.dataset.laureateIndex) {
                const index = parseInt(link.dataset.laureateIndex);
                highlightLaureate(index, true); // Pass true to indicate click from popup
            } else if (link.dataset.laureateId) {
                const laureateId = link.dataset.laureateId;
                const targetIndex = currentLaureates.findIndex(l => l.laureate_id === laureateId);
                if (targetIndex !== -1) {
                    highlightLaureate(targetIndex, true); // Pass true to indicate click from popup
                }
            }
        });
    });

    return content;
}

function createPopupContent(laureate, type) {
    const coLaureateLinks = laureate.shared_with.length > 0
        ? laureate.shared_with.map(id => {
            const coLaureate = currentLaureates.find(l => l.laureate_id === id);
            return coLaureate ? `<a href="#" class="popup-link" data-laureate-id="${id}">${coLaureate.name}</a>` : '';
        }).join(', ')
        : '';

    const locationInfo = type === 'work'
        ? `<div class="popup-section">
               <div class="popup-label">Work Location:</div>
               <div class="popup-value">${laureate.work_location}</div>
               <div class="popup-label">Work Years:</div>
               <div class="popup-value">${laureate.work_years}</div>
           </div>`
        : `<div class="popup-section">
               <div class="popup-label">Birth Location:</div>
               <div class="popup-value">${laureate.birth_location}</div>
           </div>`;

    const wikiUrl = getWikipediaUrl(laureate.name);

    const content = document.createElement('div');
    content.className = 'popup-content';
    content.innerHTML = `
        <div class="popup-name">
            ${laureate.name}
            <a href="${wikiUrl}" target="_blank" rel="noopener noreferrer" class="wiki-link" title="View Wikipedia page" style="margin-left: 5px;">📖</a>
        </div>
        <div class="popup-year">Nobel Prize ${laureate.prize_year}</div>
        ${locationInfo}
        <div class="popup-achievement">${laureate.achievement}</div>
        ${coLaureateLinks ? `<div class="popup-shared">Shared with: ${coLaureateLinks}</div>` : ''}
    `;

    // Add click handlers to links in popup
    content.querySelectorAll('.popup-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const laureateId = e.target.dataset.laureateId;
            const targetIndex = currentLaureates.findIndex(l => l.laureate_id === laureateId);
            if (targetIndex !== -1) {
                highlightLaureate(targetIndex);
            }
        });
    });

    return content;
}

function clearActiveHighlights() {
    // Remove all currently visible birth markers and connection lines
    activeHighlightElements.forEach(element => map.removeLayer(element));
    activeHighlightElements = [];
}

function highlightLaureate(index, keepPopupOpen = false) {
    // Clear any previously highlighted elements (birth markers and connections)
    clearActiveHighlights();

    // Store the currently selected laureate index
    currentSelectedLaureateIndex = index;

    // Remove active class from all cards
    document.querySelectorAll('.laureate-card').forEach(card => {
        card.classList.remove('active');
    });

    // Add active class to selected card
    const selectedCard = document.querySelector(`.laureate-card[data-index="${index}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
        selectedCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Highlight the work marker for this laureate
    const markerInfo = laureateToMarkerMap[index];
    if (markerInfo) {
        highlightMarker(markerInfo.marker, markerInfo.count, markerInfo.category, markerInfo.isMultiCategory);

        // Check if popup is currently open
        const popupWasOpen = markerInfo.marker.isPopupOpen();

        // Update popup content with the selected laureate highlighted
        const newPopupContent = createGroupPopupContent(markerInfo.group, index);
        markerInfo.marker.setPopupContent(newPopupContent);

        // If popup was already open or we're keeping it open, ensure it stays open
        if (keepPopupOpen || popupWasOpen) {
            // Use a small timeout to ensure the content is updated before opening
            setTimeout(() => {
                markerInfo.marker.openPopup();
            }, 10);
        } else {
            markerInfo.marker.openPopup();
        }
    }

    // Show birth marker and connections for selected laureate
    const data = laureateData[index];
    if (data) {
        // Add birth marker to map
        if (data.birthMarker) {
            data.birthMarker.addTo(map);
            activeHighlightElements.push(data.birthMarker);
        }

        // Add birth-to-work line to map
        if (data.birthToWorkLine) {
            data.birthToWorkLine.addTo(map);
            activeHighlightElements.push(data.birthToWorkLine);
        }

        // Add prize connection lines to map
        data.prizeConnections.forEach(line => {
            line.addTo(map);
            activeHighlightElements.push(line);
        });
    }

    // Pan to work location marker (but only if not keeping popup open to avoid jarring movement)
    if (!keepPopupOpen) {
        const laureate = currentLaureates[index];
        if (laureate) {
            map.setView([laureate.work_lat, laureate.work_lon], 6, { animate: true });
        }
    }
}

// Load "All Categories" by default on page load
window.addEventListener('DOMContentLoaded', async () => {
    const category = categorySelect.value; // Should be "all" by default
    if (category) {
        // Set initial dropdown color
        updateDropdownColor(category);

        try {
            const response = await fetch(`/api/laureates/${category}`);
            const data = await response.json();

            if (data.error) {
                console.error('Error loading default category:', data.error);
                return;
            }

            displayLaureates(data);
        } catch (error) {
            console.error('Error fetching default laureates:', error);
        }
    }
});
