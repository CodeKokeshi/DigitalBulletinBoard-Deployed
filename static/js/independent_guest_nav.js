function filterAnnouncements(query) {
    const searchQuery = query.toLowerCase();
    if (!searchQuery) {
        filteredItems = [...originalOrder]; // Reset to original order if search is empty
    } else {
        filteredItems = originalOrder.filter(item =>
            item.title.toLowerCase().includes(searchQuery) ||
            (item.date && item.date.toLowerCase().includes(searchQuery))
        );
    }
    renderPage(1); // Render from the first page after filtering
}

document.addEventListener('DOMContentLoaded', () => {
    loadData();

    const hamburgerButton = document.getElementById('hamburger');
    const menuDropdown = document.getElementById('menuDropdown');

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
});