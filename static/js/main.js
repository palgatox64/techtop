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
        cartBackdrop.classList.add('is-active');
        cartOffcanvas.classList.add('is-open');
    }

    function closeCartPanel() {
        cartBackdrop.classList.remove('is-active');
        cartOffcanvas.classList.remove('is-open');
    }

    if(cartIconButton) cartIconButton.addEventListener('click', (e) => { e.preventDefault(); openCartPanel(); });
    if(closeCartBtn) closeCartBtn.addEventListener('click', closeCartPanel);
    if(cartBackdrop) cartBackdrop.addEventListener('click', closeCartPanel);

    
    function updateCartPanel(data) {
        const cartBody = document.getElementById('cart-offcanvas-body');
        const cartSubtotal = document.getElementById('cart-subtotal');
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
            .then(response => {
                if (!response.ok) { throw new Error('Network response was not ok'); }
                return response.json();
            })
            .then(data => {
                console.log('Respuesta del servidor:', data); 
                if (data.success) {
                    const cartCountSpan = document.getElementById('cart-item-count');
                    cartCountSpan.textContent = data.cart_item_count;
                    cartCountSpan.style.display = data.cart_item_count > 0 ? 'block' : 'none';
                    
                    updateCartPanel(data);

                    Swal.fire({
                        icon: 'success', title: '¡Producto Agregado!', toast: true,
                        position: 'top-end', showConfirmButton: false, timer: 2000, timerProgressBar: true
                    });

                    openCartPanel();
                } else {
                    Swal.fire({ icon: 'error', title: 'Oops...', text: data.message || 'Ocurrió un error.' });
                }
            })
            .catch(error => {
                console.error('Error en la petición AJAX:', error);
                Swal.fire({ icon: 'error', title: 'Error de Conexión', text: 'No se pudo comunicar con el servidor.' });
            });
        }
    });
});