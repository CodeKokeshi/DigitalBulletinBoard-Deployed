async function loadData() {
    try {
        const response = await fetch(`/static/data/data.json?cache_bust=${new Date().getTime()}`);
        const data = await response.json();
        window.loadedData = data;

        const importantAnnouncements = data.important_announcements.filter(item => item.guest_mode);
        const upcomingAnnouncements = data.upcoming_deadlines_events.filter(item => item.guest_mode);

        updateSectionItems(document.getElementById('section-important'), importantAnnouncements, true, '/important');
        updateSectionItems(document.getElementById('section-upcoming'), upcomingAnnouncements, true, '/upcoming');

        updateCarouselItems('important-carousel-inner', importantAnnouncements);
        updateCarouselItems('upcoming-carousel-inner', upcomingAnnouncements);

        setupSortingHandlers(importantAnnouncements, upcomingAnnouncements);
    } catch (error) {
        console.error("Error loading data:", error);
    }
}

function setupSortingHandlers(importantAnnouncements, upcomingAnnouncements) {
    const sortAllSelect = document.getElementById('sort-all');
    sortAllSelect.addEventListener('change', () => {
        const sortOrder = sortAllSelect.value;

        const sortedImportant = [...importantAnnouncements];
        const sortedUpcoming = [...upcomingAnnouncements];

        if (sortOrder !== "default") {
            sortItems(sortedImportant, sortOrder);
            sortItems(sortedUpcoming, sortOrder);
        }

        updateSectionItems(document.getElementById('section-important'), sortedImportant, true, '/important');
        updateSectionItems(document.getElementById('section-upcoming'), sortedUpcoming, true, '/upcoming');
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

function updateCarouselItems(containerId, items) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    if (items.length === 0) {
        container.innerHTML = '<div class="carousel-item active"><p class="text-center">No announcements available.</p></div>';
        return;
    }

    items.forEach((item, index) => {
        const carouselItem = document.createElement('div');
        carouselItem.className = `carousel-item ${index === 0 ? 'active' : ''}`;
        carouselItem.innerHTML = `
            <a href="${item.link}" target="_self">
                <img src="${item.image_attachment || '/static/images/default.png'}?v={{ version }}" class="d-block w-100" alt="${item.title}">
            </a>
            <div class="carousel-caption">
                <h5>${item.title}</h5>
                <p>${item.description?.substring(0, 20) || ''}...</p>
                <small>${item.date}</small>
            </div>
        `;
        container.appendChild(carouselItem);
    });
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

function filterAnnouncements(query) {
    const sections = [
        { id: 'section-important', data: 'important_announcements', link: '/important' },
        { id: 'section-upcoming', data: 'upcoming_deadlines_events', link: '/upcoming' }
    ];

    sections.forEach(({ id, data, link }) => {
        const container = document.getElementById(id);
        const items = window.loadedData[data].filter(item =>
            item.title.toLowerCase().includes(query.toLowerCase()) && item.guest_mode
        );

        updateSectionItems(container, items, true, link);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    loadData();

    const hamburgerButton = document.getElementById('hamburger');
    const menuDropdown = document.getElementById('menuDropdown');
    const searchBar = document.getElementById('search-bar');
    const searchButton = document.getElementById('search-button');
    const viewToggle = document.getElementById('viewToggle');

    // Disable search bar and button on startup
    searchBar.disabled = true;
    searchButton.disabled = true;

    hamburgerButton.addEventListener('click', () => {
        const isExpanded = hamburgerButton.getAttribute('aria-expanded') === 'true';
        hamburgerButton.setAttribute('aria-expanded', !isExpanded);

        menuDropdown.classList.toggle('show');
        menuDropdown.classList.toggle('collapse');
    });

    document.getElementById('search-button').addEventListener('click', () => {
        const query = document.getElementById('search-bar').value;
        filterAnnouncements(query);
    });

    document.getElementById('search-bar').addEventListener('input', () => {
        const query = document.getElementById('search-bar').value;
        filterAnnouncements(query);
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
});