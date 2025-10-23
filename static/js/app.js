// Initialize map
let map = L.map('map').setView([30, 0], 2);
let workMarkers = []; // Always visible work location markers
let laureateData = []; // Store birth markers and connections for each laureate
let currentLaureates = [];
let activeHighlightElements = []; // Currently visible birth markers and connection lines

// Add OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 18
}).addTo(map);

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

categorySelect.addEventListener('change', async (e) => {
    const category = e.target.value;

    if (!category) {
        resetView();
        return;
    }

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

function resetView() {
    laureateInfo.innerHTML = '<p class="placeholder">Select a category to explore Nobel Prize winners</p>';
    infoTitle.textContent = 'Laureates';
    clearMap();
    map.setView([30, 0], 2);
}

function clearMap() {
    // Remove work markers
    workMarkers.forEach(marker => map.removeLayer(marker));
    workMarkers = [];

    // Clear active highlight elements
    clearActiveHighlights();

    // Clear stored laureate data
    laureateData = [];
}

function getMarkerOffset(coords, existingMarkers) {
    // Check if any existing marker is at or very close to this location
    const [lat, lon] = coords;
    const threshold = 0.1; // Consider markers within this range as "same location"

    let offsetCount = 0;
    existingMarkers.forEach(marker => {
        const markerLatLng = marker.getLatLng();
        const latDiff = Math.abs(markerLatLng.lat - lat);
        const lonDiff = Math.abs(markerLatLng.lng - lon);

        if (latDiff < threshold && lonDiff < threshold) {
            offsetCount++;
        }
    });

    if (offsetCount === 0) {
        return { latOffset: 0, lonOffset: 0 };
    }

    // Create circular offset pattern for multiple markers at same location
    const angle = (offsetCount * 60) * (Math.PI / 180); // 60 degrees between markers for clear separation
    const radius = 0.3; // Much larger base radius for visibility at world zoom
    const ring = Math.floor((offsetCount - 1) / 6); // 6 markers per ring
    const distance = radius + (ring * 0.3); // Each ring is further out

    return {
        latOffset: Math.cos(angle) * distance,
        lonOffset: Math.sin(angle) * distance
    };
}

function displayLaureates(data) {
    currentLaureates = data.laureates;
    infoTitle.textContent = `${data.category} Laureates`;

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

        // Add work markers (always visible) and store birth markers/connections (hidden until selected)
        prepareLaureateData(laureate, index);
    });

    // Fit map to show all work markers
    if (workMarkers.length > 0) {
        const group = L.featureGroup(workMarkers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
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

    div.innerHTML = `
        <div class="laureate-name">${laureate.name}</div>
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
        // Don't trigger if clicking on a co-laureate link
        if (!e.target.classList.contains('co-laureate-link')) {
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
    // Check if another marker already exists at this location and offset if needed
    const offset = getMarkerOffset([laureate.work_lat, laureate.work_lon], workMarkers);
    const adjustedWorkLat = laureate.work_lat + offset.latOffset;
    const adjustedWorkLon = laureate.work_lon + offset.lonOffset;

    // Always add work location marker to map
    const workMarker = L.marker([adjustedWorkLat, adjustedWorkLon], { icon: workIcon });
    workMarker.bindPopup(createPopupContent(laureate, 'work'));
    workMarker.addTo(map);
    workMarker.on('click', () => highlightLaureate(index));
    workMarkers.push(workMarker);

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

    const content = document.createElement('div');
    content.className = 'popup-content';
    content.innerHTML = `
        <div class="popup-name">${laureate.name}</div>
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

function highlightLaureate(index) {
    // Clear any previously highlighted elements (birth markers and connections)
    clearActiveHighlights();

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

    // Pan to work location marker
    const laureate = currentLaureates[index];
    if (laureate) {
        map.setView([laureate.work_lat, laureate.work_lon], 6, { animate: true });
    }
}
