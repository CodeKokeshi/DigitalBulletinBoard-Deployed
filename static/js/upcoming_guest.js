const itemsPerPage = 10;
let currentPage = 1;
let upcomingDeadlines = [];
let originalOrder = [];
let filteredItems = []; // Tracks filtered data

async function loadData() {
    try {
        const response = await fetch(`/static/data/data.json?cache_bust=${new Date().getTime()}`);
        const data = await response.json();
        upcomingDeadlines = data.upcoming_deadlines_events.filter(item => item.guest_mode === true);
        originalOrder = [...upcomingDeadlines];
        filteredItems = [...upcomingDeadlines]; // Initialize filteredItems
        renderPage(currentPage);
    } catch (error) {
        console.error("Error loading data:", error);
    }
}

function sortItems(sortOrder) {
    if (sortOrder === "default") {
        filteredItems = [...originalOrder]; // Restore original order
    } else if (sortOrder === "nearest") {
        filteredItems.sort((a, b) => new Date(a.sorting_date) - new Date(b.sorting_date));
    } else if (sortOrder === "farthest") {
        filteredItems.sort((a, b) => new Date(b.sorting_date) - new Date(a.sorting_date));
    }
    renderPage(1); // Render from the first page after sorting
}

function renderPage(page) {
    const contentContainer = document.getElementById('content');
    contentContainer.innerHTML = ''; // Clear previous content

    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const pageItems = filteredItems.slice(start, end);

    pageItems.forEach(item => {
        const card = document.createElement('div');
        card.className = 'announcement-card';

        const title = document.createElement('h5');
        title.textContent = item.title;
        card.appendChild(title);

        if (item.date) {
            const date = document.createElement('p');
            date.textContent = item.date;
            date.className = 'mb-2 text-muted';
            card.appendChild(date);
        }

        if (item.description) {
            const description = document.createElement('p');
            description.textContent = item.description.length > 72
                ? item.description.substring(0, 72) + '...'
                : item.description;
            description.className = 'mb-2';
            card.appendChild(description);
        }

        const image = document.createElement('img');
        image.src = item.image_attachment || '/static/images/default.png?v={{ version }}';
        image.alt = item.title;
        image.style.height = '250px';
        image.style.border = '1px solid #ccc'; // Add border
        image.style.borderRadius = '10px'; // Make corners rounder
        image.style.maxWidth = '100%'; // Ensure image does not exceed container width
        image.className = 'mb-2';
        card.appendChild(image);

        if (item.link) {
            const link = document.createElement('a');
            link.href = item.link;
            link.target = '_blank';
            link.textContent = 'Read More';
            link.className = 'd-block mt-2'; // Ensure the link is displayed as a block element
            card.appendChild(link);
        }

        contentContainer.appendChild(card);
    });

    renderPagination(page);
}

function renderPagination(currentPage) {
    const paginationContainer = document.querySelector('.pagination-container');
    if (paginationContainer) {
        paginationContainer.remove();
    }

    const newPagination = document.createElement('div');
    newPagination.className = 'pagination-container';

    const homeButton = document.createElement('button');
    homeButton.className = 'home-button';
    homeButton.innerHTML = '<i class="bi bi-house"></i>';
    homeButton.addEventListener('click', () => {
        window.location.href = '/';
    });
    newPagination.appendChild(homeButton);

    const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    const maxVisibleButtons = 3;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisibleButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxVisibleButtons - 1);

    if (endPage - startPage < maxVisibleButtons - 1) {
        startPage = Math.max(1, endPage - maxVisibleButtons + 1);
    }

    if (currentPage > 1) {
        const prevButton = document.createElement('button');
        prevButton.className = 'pagination-button prev';
        prevButton.innerHTML = '<i class="bi bi-arrow-left"></i>';
        prevButton.addEventListener('click', () => {
            renderPage(currentPage - 1);
        });
        newPagination.appendChild(prevButton);
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.className = 'pagination-button';
        if (i === currentPage) {
            pageButton.classList.add('active');
        }
        pageButton.textContent = i;
        pageButton.addEventListener('click', () => {
            renderPage(i);
        });
        newPagination.appendChild(pageButton);
    }

    if (currentPage < totalPages) {
        const nextButton = document.createElement('button');
        nextButton.className = 'pagination-button next';
        nextButton.innerHTML = '<i class="bi bi-arrow-right"></i>';
        nextButton.addEventListener('click', () => {
            renderPage(currentPage + 1);
        });
        newPagination.appendChild(nextButton);
    }

    document.querySelector('.container').appendChild(newPagination);
}

document.addEventListener('DOMContentLoaded', () => {
    loadData();

    const sortOptions = document.getElementById('sort-options');
    sortOptions.addEventListener('change', (event) => {
        sortItems(event.target.value);
    });
});