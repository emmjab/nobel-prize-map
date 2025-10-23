// Table filtering and sorting functionality

const searchBox = document.getElementById('search');
const categoryFilter = document.getElementById('category-filter');
const yearSort = document.getElementById('year-sort');
const tableBody = document.querySelector('#laureates-table tbody');
const totalCount = document.getElementById('total-count');

let allRows = Array.from(tableBody.querySelectorAll('tr'));

// Search functionality
searchBox.addEventListener('input', filterTable);
categoryFilter.addEventListener('change', filterTable);
yearSort.addEventListener('change', sortTable);

function filterTable() {
    const searchTerm = searchBox.value.toLowerCase();
    const selectedCategory = categoryFilter.value;

    let visibleCount = 0;

    allRows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const category = row.dataset.category;

        const matchesSearch = text.includes(searchTerm);
        const matchesCategory = !selectedCategory || category === selectedCategory;

        if (matchesSearch && matchesCategory) {
            row.classList.remove('hidden');
            visibleCount++;
        } else {
            row.classList.add('hidden');
        }
    });

    totalCount.textContent = `Showing: ${visibleCount} of ${allRows.length} laureates`;
}

function sortTable() {
    const sortOrder = yearSort.value;

    allRows.sort((a, b) => {
        const yearA = parseInt(a.dataset.year);
        const yearB = parseInt(b.dataset.year);

        return sortOrder === 'desc' ? yearB - yearA : yearA - yearB;
    });

    // Re-append rows in new order
    allRows.forEach(row => tableBody.appendChild(row));
}

// Initialize count
totalCount.textContent = `Total: ${allRows.length} laureates`;
