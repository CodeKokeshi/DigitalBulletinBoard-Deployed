document.addEventListener('DOMContentLoaded', () => {
    const viewToggle = document.getElementById('viewToggle');
    const listView = document.getElementById('listView');
    const carouselView = document.getElementById('carouselView');

    function updateView() {
        if (viewToggle.checked) {
            listView.classList.add('d-none');
            carouselView.classList.remove('d-none');
        } else {
            carouselView.classList.add('d-none');
            listView.classList.remove('d-none');
        }
    }

    viewToggle.addEventListener('change', updateView);
    updateView(); // Ensure the default view is set
});