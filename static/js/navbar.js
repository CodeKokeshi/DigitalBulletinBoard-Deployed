document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('logout-button').addEventListener('click', async () => {
        const response = await fetch('/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/';
        } else {
            console.error('Logout failed');
        }
    });

    document.getElementById('logout-button-mobile').addEventListener('click', async () => {
        const response = await fetch('/logout', { method: 'POST' });
        if (response.ok) {
            window.location.href = '/';
        } else {
            console.error('Logout failed');
        }
    });

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

function filterAnnouncements(query) {
    const sections = [
        { id: 'section-important', data: 'important_announcements', link: '/important' },
        { id: 'section-upcoming', data: 'upcoming_deadlines_events', link: '/upcoming' },
        { id: 'section-milestones', data: 'milestones', link: '/milestones' }
    ];

    sections.forEach(({ id, data, link }) => {
        const container = document.getElementById(id);
        const items = window.loadedData[data].filter(item =>
            item.title.toLowerCase().includes(query.toLowerCase())
        );

        updateSectionItems(container, items, true, link);
    });
}