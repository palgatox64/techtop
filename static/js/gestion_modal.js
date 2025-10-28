console.log('🔍 Archivo gestion_modal.js iniciando...');

class GestionModal {
    constructor() {
        console.log('🔧 Constructor de GestionModal ejecutándose...');
        this.modal = null;
        this.init();
    }

    init() {
        console.log('🚀 Inicializando GestionModal...');
        this.createModal();
        this.attachEditButtonListeners();
        this.attachAddButtonListeners(); // 👈 Nueva línea
        this.attachOutsideClickListener();
        console.log('✅ GestionModal inicializado correctamente');
    }

    createModal() {
        console.log('📋 Creando modal...');
        
        if (document.getElementById('edit-modal')) {
            this.modal = document.getElementById('edit-modal');
            console.log('ℹ️ Modal ya existe, reutilizando...');
            return;
        }

        const modalHTML = `
            <div id="edit-modal" class="modal-overlay">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2 id="modal-title">Editar Item</h2>
                        <button type="button" class="modal-close" id="modal-close">
                            <i class='bx bx-x'></i>
                        </button>
                    </div>
                    <div class="modal-body">
                        <div id="modal-loading" style="text-align: center; padding: 40px;">
                            <i class='bx bx-loader-alt bx-spin' style="font-size: 2rem;"></i>
                            <p>Cargando formulario...</p>
                        </div>
                        <div id="modal-form-container" style="display: none;">
                            <!-- El formulario se cargará aquí -->
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('edit-modal');
        console.log('✅ Modal creado e insertado en el DOM');

        document.getElementById('modal-close').addEventListener('click', () => {
            console.log('❌ Botón cerrar modal clickeado');
            this.closeModal();
        });
    }

    attachEditButtonListeners() {
        console.log('🎯 Configurando listeners para botones de editar...');
        
        // Buscar todos los enlaces de editar existentes
        const editLinks = document.querySelectorAll('a[href*="/editar/"]');
        console.log(`🔍 Encontrados ${editLinks.length} enlaces de editar:`, editLinks);

        // Interceptar TODOS los clics en el documento
        document.addEventListener('click', (e) => {
            console.log('🖱️ Click detectado en:', e.target);
            
            // Buscar el enlace de edición más cercano
            const editLink = e.target.closest('a[href*="/editar/"]');
            
            if (editLink && editLink.href.includes('/gestion/')) {
                console.log('🎯 ¡ENLACE DE EDITAR INTERCEPTADO!', editLink.href);
                e.preventDefault();
                e.stopPropagation();
                
                const itemType = this.getItemTypeFromUrl(editLink.href);
                this.openEditModal(editLink.href, itemType);
                return false;
            } else {
                console.log('⚪ Click no es en enlace de editar');
            }
        });

        console.log('✅ Listeners configurados');
    }

    // 👇 NUEVA FUNCIÓN PARA BOTONES DE AGREGAR
    attachAddButtonListeners() {
        console.log('🎯 Configurando listeners para botones de agregar...');
        
        // Interceptar clics en enlaces de agregar
        document.addEventListener('click', (e) => {
            // Buscar el enlace de agregar más cercano
            const addLink = e.target.closest('a[href*="/agregar"], a[href*="/nuevo"], a[href*="/crear"]');
            
            if (addLink && addLink.href.includes('/gestion/')) {
                console.log('🎯 ¡ENLACE DE AGREGAR INTERCEPTADO!', addLink.href);
                e.preventDefault();
                e.stopPropagation();
                
                const itemType = this.getItemTypeFromUrl(addLink.href);
                this.openAddModal(addLink.href, itemType);
                return false;
            }
        });

        console.log('✅ Listeners de agregar configurados');
    }

    getItemTypeFromUrl(url) {
        if (url.includes('/productos/')) return 'Producto';
        if (url.includes('/categorias/')) return 'Categoría';
        if (url.includes('/marcas/')) return 'Marca';
        return 'Item';
    }

    // 👇 NUEVA FUNCIÓN PARA ABRIR MODAL DE AGREGAR
    async openAddModal(addUrl, itemType) {
        console.log('🔓 Abriendo modal para agregar:', addUrl, 'tipo:', itemType);
        
        this.modal.classList.add('show');
        document.getElementById('modal-title').textContent = `Agregar ${itemType}`;
        document.getElementById('modal-loading').style.display = 'block';
        document.getElementById('modal-form-container').style.display = 'none';

        try {
            console.log('📡 Haciendo fetch a:', addUrl);
            const response = await fetch(addUrl);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const html = await response.text();
            console.log('📄 HTML recibido, longitud:', html.length);
            
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const formElement = doc.querySelector('.gestion-form');
            
            console.log('🔍 Formulario encontrado:', formElement);
            
            if (formElement) {
                document.getElementById('modal-loading').style.display = 'none';
                document.getElementById('modal-form-container').style.display = 'block';
                document.getElementById('modal-form-container').innerHTML = formElement.outerHTML;
                
                const modalForm = document.querySelector('#modal-form-container .gestion-form');
                modalForm.classList.add('modal-form');
                
                console.log('✅ Formulario de agregar cargado en modal');
                this.setupModalFormButtons(modalForm, addUrl);
            } else {
                throw new Error('No se encontró el formulario .gestion-form en la respuesta');
            }
        } catch (error) {
            console.error('❌ Error al cargar el formulario:', error);
            document.getElementById('modal-loading').innerHTML = `
                <i class='bx bx-error' style="font-size: 2rem; color: #dc3545;"></i>
                <p>Error al cargar el formulario: ${error.message}</p>
            `;
        }
    }

    async openEditModal(editUrl, itemType) {
        console.log('🔓 Abriendo modal para:', editUrl, 'tipo:', itemType);
        
        this.modal.classList.add('show');
        document.getElementById('modal-title').textContent = `Editar ${itemType}`;
        document.getElementById('modal-loading').style.display = 'block';
        document.getElementById('modal-form-container').style.display = 'none';

        try {
            console.log('📡 Haciendo fetch a:', editUrl);
            const response = await fetch(editUrl);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const html = await response.text();
            console.log('📄 HTML recibido, longitud:', html.length);
            
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const formElement = doc.querySelector('.gestion-form');
            
            console.log('🔍 Formulario encontrado:', formElement);
            
            if (formElement) {
                document.getElementById('modal-loading').style.display = 'none';
                document.getElementById('modal-form-container').style.display = 'block';
                document.getElementById('modal-form-container').innerHTML = formElement.outerHTML;
                
                const modalForm = document.querySelector('#modal-form-container .gestion-form');
                modalForm.classList.add('modal-form');
                
                console.log('✅ Formulario cargado en modal');
                this.setupModalFormButtons(modalForm, editUrl);
            } else {
                throw new Error('No se encontró el formulario .gestion-form en la respuesta');
            }
        } catch (error) {
            console.error('❌ Error al cargar el formulario:', error);
            document.getElementById('modal-loading').innerHTML = `
                <i class='bx bx-error' style="font-size: 2rem; color: #dc3545;"></i>
                <p>Error al cargar el formulario: ${error.message}</p>
            `;
        }
    }

    setupModalFormButtons(form, editUrl) {
        console.log('🔧 Configurando botones del formulario modal');
        
        const cancelButton = form.querySelector('.btn-cancel');
        if (cancelButton) {
            cancelButton.type = 'button';
            cancelButton.addEventListener('click', (e) => {
                e.preventDefault();
                console.log('❌ Botón cancelar clickeado');
                this.closeModal();
            });
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('📤 Formulario enviado');
            await this.handleFormSubmit(form, editUrl);
        });
    }

    async handleFormSubmit(form, editUrl) {
        console.log('💾 Manejando envío del formulario');
        
        const submitButton = form.querySelector('.btn-submit');
        const originalText = submitButton.textContent;
        
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Guardando...';

        try {
            const formData = new FormData(form);
            
            const response = await fetch(editUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });

            if (response.ok) {
                console.log('✅ Formulario enviado exitosamente');
                const isAdding = editUrl.includes('/agregar') || editUrl.includes('/nuevo') || editUrl.includes('/crear');
                const successMessage = isAdding ? 'creado' : 'actualizado';
                
                await Swal.fire({
                    icon: 'success',
                    title: `¡${isAdding ? 'Creado' : 'Actualizado'}!`,
                    text: `Los cambios se han ${successMessage} exitosamente.`,
                    timer: 2000,
                    showConfirmButton: false
                });

                this.closeModal();
                location.reload();
            } else {
                console.log('⚠️ Error en la respuesta del servidor');
                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newForm = doc.querySelector('.gestion-form');
                
                if (newForm) {
                    document.getElementById('modal-form-container').innerHTML = newForm.outerHTML;
                    const modalForm = document.querySelector('#modal-form-container .gestion-form');
                    modalForm.classList.add('modal-form');
                    this.setupModalFormButtons(modalForm, editUrl);
                }
            }
        } catch (error) {
            console.error('❌ Error al enviar el formulario:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Ocurrió un error al guardar los cambios.'
            });
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    }

    attachOutsideClickListener() {
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                console.log('🖱️ Click fuera del modal, cerrando...');
                this.closeModal();
            }
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                console.log('⌨️ Tecla Escape presionada, cerrando modal...');
                this.closeModal();
            }
        });
    }

    closeModal() {
        console.log('🔒 Cerrando modal...');
        this.modal.classList.remove('show');
        setTimeout(() => {
            document.getElementById('modal-form-container').innerHTML = '';
            document.getElementById('modal-loading').style.display = 'block';
            document.getElementById('modal-form-container').style.display = 'none';
            console.log('🧹 Modal limpiado');
        }, 300);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('🏁 DOM listo, inicializando GestionModal...');
    
    // Verificar si existen los enlaces de editar y agregar
    const editLinks = document.querySelectorAll('a[href*="/editar/"]');
    const addLinks = document.querySelectorAll('a[href*="/agregar"], a[href*="/nuevo"], a[href*="/crear"]');
    console.log('🔍 Enlaces de editar encontrados:', editLinks.length);
    console.log('🔍 Enlaces de agregar encontrados:', addLinks.length);
    editLinks.forEach((link, index) => {
        console.log(`  ${index + 1}. ${link.href}`);
    });
    addLinks.forEach((link, index) => {
        console.log(`  Agregar ${index + 1}. ${link.href}`);
    });
    
    // Crear instancia del modal
    new GestionModal();
    console.log('🎉 GestionModal inicializado completamente');
});

console.log('📄 Final del archivo gestion_modal.js');