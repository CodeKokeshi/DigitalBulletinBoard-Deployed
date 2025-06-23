async function loadData() {
    try {
        const response = await fetch(`/static/data/data.json?cache_bust=${new Date().getTime()}`);
        const data = await response.json();
        window.loadedData = data;

        // Default rendering
        updateSectionItems(document.getElementById('section-important'), data.important_announcements, true, '/important');
        updateSectionItems(document.getElementById('section-upcoming'), data.upcoming_deadlines_events, true, '/upcoming');
        updateSectionItems(document.getElementById('section-milestones'), data.milestones, true, '/milestones');

        // Attach sorting handlers
        setupSortingHandlers();
    } catch (error) {
        console.error("Error loading data:", error);
    }
}

function setupSortingHandlers() {
    const sortAllSelect = document.getElementById('sort-all');
    sortAllSelect.addEventListener('change', () => {
        const sortOrder = sortAllSelect.value;

        const importantData = [...window.loadedData.important_announcements];
        const upcomingData = [...window.loadedData.upcoming_deadlines_events];
        const milestonesData = [...window.loadedData.milestones];

        if (sortOrder !== "default") {
            sortItems(importantData, sortOrder);
            sortItems(upcomingData, sortOrder);
            sortItems(milestonesData, sortOrder);
        }

        updateSectionItems(document.getElementById('section-important'), importantData, true, '/important');
        updateSectionItems(document.getElementById('section-upcoming'), upcomingData, true, '/upcoming');
        updateSectionItems(document.getElementById('section-milestones'), milestonesData, true, '/milestones');
    });
}

function generateSection(sectionId, items, showDate, link, sortSelectId) {
    const container = document.getElementById(sectionId);
    const sortSelect = document.getElementById(sortSelectId);

    const initialOrder = [...items];

    sortSelect.addEventListener('change', () => {
        if (sortSelect.value === "default") {
            items = [...initialOrder];
        } else {
            sortItems(items, sortSelect.value);
        }
        updateSectionItems(container, items, showDate, link);
    });

    // Ensure the section is updated with the default sorting on load
    updateSectionItems(container, items, showDate, link);
}

function updateSectionItems(container, items, showDate, link) {
    container.innerHTML = '';

    if (items.length === 0) {
        container.innerHTML = '<p class="text-center text-muted fst-italic">No announcements</p>';
    } else {
        items.slice(0, 5).forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'd-flex flex-column align-items-center mb-2';

            if (showDate && item.date) {
                const dateSpan = document.createElement('span');
                dateSpan.className = 'fw-bold text-muted mb-1';
                dateSpan.textContent = item.date;
                itemDiv.appendChild(dateSpan);
            }

            const titleLink = document.createElement('a');
            titleLink.className = 'text-decoration-none text-center fw-bold';
            titleLink.href = item.link || '#';
            titleLink.target = '_blank';
            titleLink.textContent = item.title;
            itemDiv.appendChild(titleLink);

            container.appendChild(itemDiv);
        });

        if (items.length > 5) {
            const viewMoreButton = document.createElement('button');
            viewMoreButton.className = 'btn btn-outline-primary mt-2 view-more';
            viewMoreButton.textContent = 'View More';
            viewMoreButton.onclick = () => (window.location.href = link);
            container.appendChild(viewMoreButton);
        }
    }
}

function sortItems(items, sortOrder) {
    items.sort((a, b) => {
        const dateA = new Date(a.sorting_date);
        const dateB = new Date(b.sorting_date);
        return sortOrder === "nearest"
            ? dateA - dateB
            : dateB - dateA;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const sortAllSelect = document.getElementById('sort-all');
    const viewToggle = document.getElementById('viewToggle');
    const searchBar = document.getElementById('search-bar');
    const searchButton = document.getElementById('search-button');

    // Disable search bar and button on startup
    searchBar.disabled = true;
    searchButton.disabled = true;

    sortAllSelect.addEventListener('change', () => {
        const sortOrder = sortAllSelect.value;

        // Update Important and Upcoming sections
        const importantData = [...window.loadedData.important_announcements];
        const upcomingData = [...window.loadedData.upcoming_deadlines_events];
        const milestonesData = [...window.loadedData.milestones];

        if (sortOrder !== "default") {
            sortItems(importantData, sortOrder);
            sortItems(upcomingData, sortOrder);
            sortItems(milestonesData, sortOrder);
        }

        updateSectionItems(document.getElementById('section-important'), importantData, true, '/important');
        updateSectionItems(document.getElementById('section-upcoming'), upcomingData, true, '/upcoming');
        updateSectionItems(document.getElementById('section-milestones'), milestonesData, true, '/milestones');
    });

    viewToggle.addEventListener('change', () => {
        if (viewToggle.checked) {
            searchBar.disabled = true;
            searchButton.disabled = true;
        } else {
            searchBar.disabled = false;
            searchButton.disabled = false;
        }
    });

    loadData();
});