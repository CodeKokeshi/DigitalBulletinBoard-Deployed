async function loadAnnouncements() {
    const response = await fetch(`/static/data/data.json?cache_bust=${new Date().getTime()}`);
    const data = await response.json();

    const carousels = [
        { id: 'important-carousel-inner', items: data.important_announcements },
        { id: 'upcoming-carousel-inner', items: data.upcoming_deadlines_events },
        { id: 'milestone-carousel-inner', items: data.milestones }
    ];

    carousels.forEach(({ id, items }) => {
        const container = document.getElementById(id);
        if (!items.length) {
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
    });
}

document.addEventListener('DOMContentLoaded', loadAnnouncements);