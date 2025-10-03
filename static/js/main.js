document.addEventListener('DOMContentLoaded', function() {
    const dropdownItems = document.querySelectorAll('.nav-item-dropdown');
    dropdownItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const isActive = item.classList.contains('active');
            dropdownItems.forEach(openItem => {
                openItem.classList.remove('active');
            });

            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    document.addEventListener('click', function(event) {
        if (!event.target.closest('.nav-item-dropdown')) {
            dropdownItems.forEach(item => {
                item.classList.remove('active');
            });
        }
    });
});