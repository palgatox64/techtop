document.addEventListener('DOMContentLoaded', function() {
    const swiper = new Swiper('.swiper', {
        direction: 'horizontal',
        loop: true,
        pagination: {
            el: '.swiper-pagination',
            clickable: true,
        },
        navigation: {
            nextEl: '.swiper-button-next',
            prevEl: '.swiper-button-prev',
        },
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
    });

    const userMenuButton = document.getElementById('user-menu-button');
    const userMenuDropdown = document.getElementById('user-menu-dropdown');
    const userMenuButtonLoggedIn = document.getElementById('user-menu-button-loggedin');
    const userMenuDropdownLoggedIn = document.getElementById('user-menu-dropdown-loggedin');

    if (userMenuButton) {
        userMenuButton.addEventListener('click', function(event) {
            event.stopPropagation();
            userMenuDropdown.classList.toggle('show');
        });
    }
    if (userMenuButtonLoggedIn) {
        userMenuButtonLoggedIn.addEventListener('click', function(event) {
            event.stopPropagation();
            userMenuDropdownLoggedIn.classList.toggle('show');
        });
    }

    const dropdownItems = document.querySelectorAll('.nav-item-dropdown');
    dropdownItems.forEach(item => {
        const link = item.querySelector('.nav-link');
        link.addEventListener('click', function(event) {
            if (window.innerWidth <= 768) {
                if (!item.classList.contains('active')) {
                    event.preventDefault(); 
                    dropdownItems.forEach(openItem => {
                        if (openItem !== item) {
                            openItem.classList.remove('active');
                        }
                    });
                    
                    item.classList.add('active');
                }
            }
        });
    });

  
    window.addEventListener('click', function(event) {
        if (userMenuDropdown && userMenuDropdown.classList.contains('show') && !userMenuButton.contains(event.target)) {
            userMenuDropdown.classList.remove('show');
        }
        if (userMenuDropdownLoggedIn && userMenuDropdownLoggedIn.classList.contains('show') && !userMenuButtonLoggedIn.contains(event.target)) {
            userMenuDropdownLoggedIn.classList.remove('show');
        }
        dropdownItems.forEach(item => {
            if (!item.contains(event.target)) {
                item.classList.remove('active');
            }
        });
    });

    const openBtn = document.getElementById('open-filters-btn');
    const closeBtn = document.getElementById('close-filters-btn');
    const filterSidebar = document.getElementById('filter-sidebar');
    const backdrop = document.getElementById('filter-backdrop');

    if (openBtn) {
        openBtn.addEventListener('click', function() {
            filterSidebar.classList.add('is-open');
            backdrop.classList.add('is-active');
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            filterSidebar.classList.remove('is-open');
            backdrop.classList.remove('is-active');
        });
    }

    if (backdrop) {
        backdrop.addEventListener('click', function() {
            filterSidebar.classList.remove('is-open');
            backdrop.classList.remove('is-active');
        });
    }
});