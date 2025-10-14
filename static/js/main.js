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

    const cartIconButton = document.getElementById('cart-icon-button');
    const cartOffcanvas = document.getElementById('cart-offcanvas');
    const cartBackdrop = document.getElementById('cart-backdrop');
    const closeCartBtn = document.getElementById('close-cart-btn');

    function openCartPanel() {
        if(cartBackdrop) cartBackdrop.classList.add('is-active');
        if(cartOffcanvas) cartOffcanvas.classList.add('is-open');
    }

    function closeCartPanel() {
        if(cartBackdrop) cartBackdrop.classList.remove('is-active');
        if(cartOffcanvas) cartOffcanvas.classList.remove('is-open');
    }

    if(cartIconButton) cartIconButton.addEventListener('click', (e) => { e.preventDefault(); openCartPanel(); });
    if(closeCartBtn) closeCartBtn.addEventListener('click', closeCartPanel);
    if(cartBackdrop) cartBackdrop.addEventListener('click', closeCartPanel);
    function updateCartUI(data) {
        const cartCountSpan = document.getElementById('cart-item-count');
        const cartBody = document.getElementById('cart-offcanvas-body');
        const cartSubtotal = document.getElementById('cart-subtotal');
        
        if (!cartCountSpan || !cartBody || !cartSubtotal) {
            console.error("Elementos del carrito no encontrados en el DOM.");
            return;
        }

        cartCountSpan.textContent = data.cart_item_count;
        cartCountSpan.style.display = data.cart_item_count > 0 ? 'block' : 'none';
        cartBody.innerHTML = '';
        if (data.items && data.items.length > 0) {
            data.items.forEach(item => {
                const formattedPrice = item.price.toLocaleString('es-CL');
                const cartItemHTML = `
                    <div class="cart-offcanvas-item">
                        <img src="${item.image_url}" alt="${item.name}" class="item-image">
                        <div class="item-details">
                            <p class="item-name">${item.name}</p>
                            <p class="item-price">Cantidad: ${item.quantity} x $${formattedPrice}</p>
                        </div>
                    </div>
                `;
                cartBody.insertAdjacentHTML('beforeend', cartItemHTML);
            });
            cartSubtotal.textContent = '$' + data.subtotal.toLocaleString('es-CL');
        } else {
            cartBody.innerHTML = '<p>Tu carrito está vacío.</p>';
            cartSubtotal.textContent = '$0';
        }
    }

    document.body.addEventListener('submit', function(event) {
        if (event.target.matches('form[action*="/agregar/"]')) {
            event.preventDefault();
            
            const form = event.target;
            const url = form.action;
            const formData = new FormData(form);
            
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartUI(data);

                    Swal.fire({
                        icon: 'success', title: '¡Producto Agregado!', toast: true,
                        position: 'top-end', showConfirmButton: false, timer: 2000, timerProgressBar: true
                    });

                    openCartPanel();
                } else {
                    Swal.fire({ icon: 'error', title: 'Oops...', text: data.message || 'Ocurrió un error.' });
                }
            })
            .catch(error => console.error('Error en AJAX al agregar:', error));
        }
    });

    function loadInitialCart() {
        fetch('/api/get-cart/')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartUI(data);
                }
            })
            .catch(error => console.error('Error al cargar el carrito inicial:', error));
    }
    loadInitialCart();
});