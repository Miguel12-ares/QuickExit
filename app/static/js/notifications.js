/**
 * Sistema de Notificaciones Elegantes - QuickExit
 * Este archivo es independiente y no interfiere con los modales existentes
 */

// Sistema de Notificaciones Elegantes - QuickExit
(function() {
    class QuickExitNotifications {
        constructor() {
            this.container = null;
            this.notifications = [];
            this.init();
        }

        /**
         * Inicializa el sistema de notificaciones
         */
        init() {
            // Crear contenedor si no existe
            if (!document.querySelector('.quickexit-notifications-container')) {
                this.container = document.createElement('div');
                this.container.className = 'quickexit-notifications-container';
                document.body.appendChild(this.container);
            } else {
                this.container = document.querySelector('.quickexit-notifications-container');
            }

            // Cargar CSS si no está cargado
            this.loadCSS();
        }

        /**
         * Carga el CSS de notificaciones si no está presente
         */
        loadCSS() {
            if (!document.querySelector('link[href*="notifications.css"]')) {
                const link = document.createElement('link');
                link.rel = 'stylesheet';
                link.href = '/static/css/global/notifications.css';
                document.head.appendChild(link);
            }
        }

        /**
         * Muestra una notificación
         * @param {Object} options - Opciones de la notificación
         * @param {string} options.type - Tipo: 'success', 'error', 'warning', 'info'
         * @param {string} options.title - Título de la notificación
         * @param {string} options.message - Mensaje de la notificación
         * @param {number} options.duration - Duración en milisegundos (default: 5000)
         * @param {boolean} options.dismissible - Si se puede cerrar (default: true)
         * @param {Array} options.actions - Array de acciones [{text, type, callback}]
         * @param {Function} options.onClose - Callback al cerrar
         */
        show(options) {
            const {
                type = 'info',
                title = '',
                message = '',
                duration = 5000,
                dismissible = true,
                actions = [],
                onClose = null
            } = options;

            const validTypes = ['success', 'error', 'warning', 'info', 'danger'];
            // Unificar error y danger
            let notificationType = validTypes.includes(type) ? type : 'info';
            if (notificationType === 'error') notificationType = 'danger';

            const notification = this.createNotificationElement({
                type: notificationType,
                title,
                message,
                dismissible,
                actions,
                onClose,
                duration
            });

            this.container.appendChild(notification);
            this.notifications.push(notification);

            if (duration > 0) {
                setTimeout(() => {
                    this.remove(notification);
                }, duration);
            }
            return notification;
        }

        /**
         * Crea el elemento HTML de la notificación
         */
        createNotificationElement({ type, title, message, dismissible, actions, onClose, duration }) {
            const notification = document.createElement('div');
            notification.className = `quickexit-notification quickexit-notification-${type}`;

            // Forzar contraste para error/danger
            let bgStyle = '';
            let textStyle = '';
            if (type === 'danger') {
                bgStyle = 'background: linear-gradient(135deg, #fff 0%, #ffeaea 100%) !important;';
                textStyle = 'color: #c62828 !important;';
            }

            const iconMap = {
                success: 'fas fa-check-circle',
                error: 'fas fa-exclamation-circle',
                danger: 'fas fa-exclamation-triangle',
                warning: 'fas fa-exclamation-triangle',
                info: 'fas fa-info-circle'
            };
            const titleMap = {
                success: 'Éxito',
                error: 'Error',
                danger: 'Error',
                warning: 'Advertencia',
                info: 'Información'
            };
            const icon = iconMap[type] || iconMap.info;
            const defaultTitle = title || titleMap[type] || titleMap.info;

            let html = `
                <div class="quickexit-notification-header">
                    <div class="quickexit-notification-title">
                        <i class="${icon}"></i>
                        <span>${defaultTitle}</span>
                    </div>
                    ${dismissible ? '<button class="quickexit-notification-close" aria-label="Cerrar"><i class="fas fa-times"></i></button>' : ''}
                </div>
                <div class="quickexit-notification-content" style="${bgStyle}${textStyle}">
                    ${message}
                </div>
            `;
            if (actions && actions.length > 0) {
                html += '<div class="quickexit-notification-footer">';
                actions.forEach(action => {
                    const btnClass = action.type === 'primary' ? 'quickexit-notification-btn-primary' : 'quickexit-notification-btn-secondary';
                    html += `
                        <button class="quickexit-notification-btn ${btnClass}" data-action="${action.text}">
                            ${action.icon ? `<i class="${action.icon}"></i>` : ''}
                            ${action.text}
                        </button>
                    `;
                });
                html += '</div>';
            }
            if (duration > 0) {
                html += '<div class="quickexit-notification-progress"></div>';
            }
            notification.innerHTML = html;
            this.addEventListeners(notification, { dismissible, actions, onClose });
            return notification;
        }

        /**
         * Agrega event listeners a la notificación
         */
        addEventListeners(notification, { dismissible, actions, onClose }) {
            // Botón de cerrar
            const closeBtn = notification.querySelector('.quickexit-notification-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    this.remove(notification);
                    if (onClose) onClose();
                });
            }

            // Botones de acción
            const actionBtns = notification.querySelectorAll('.quickexit-notification-btn');
            actionBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    const actionText = btn.dataset.action;
                    const action = actions.find(a => a.text === actionText);
                    if (action && action.callback) {
                        action.callback();
                    }
                    this.remove(notification);
                });
            });

            // Cerrar al hacer clic fuera del contenido (opcional)
            notification.addEventListener('click', (e) => {
                if (e.target === notification && dismissible) {
                    this.remove(notification);
                    if (onClose) onClose();
                }
            });
        }

        /**
         * Remueve una notificación
         */
        remove(notification) {
            if (!notification || !notification.parentNode) return;

            // Agregar clase de salida
            notification.classList.add('quickexit-notification-exiting');

            // Remover después de la animación
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                
                // Remover del array
                const index = this.notifications.indexOf(notification);
                if (index > -1) {
                    this.notifications.splice(index, 1);
                }
            }, 300);
        }

        /**
         * Remueve todas las notificaciones
         */
        clear() {
            this.notifications.forEach(notification => {
                this.remove(notification);
            });
        }

        /**
         * Métodos de conveniencia para tipos específicos
         */
        success(message, title = 'Éxito', options = {}) {
            return this.show({ type: 'success', title, message, ...options });
        }

        error(message, title = 'Error', options = {}) {
            return this.show({ type: 'danger', title, message, ...options });
        }

        warning(message, title = 'Advertencia', options = {}) {
            return this.show({ type: 'warning', title, message, ...options });
        }

        info(message, title = 'Información', options = {}) {
            return this.show({ type: 'info', title, message, ...options });
        }

        danger(message, title = 'Error', options = {}) {
            return this.show({ type: 'danger', title, message, ...options });
        }

        /**
         * Reemplaza alert() nativo con notificaciones elegantes
         */
        replaceNativeAlerts() {
            // Guardar referencia al alert original
            const originalAlert = window.alert;
            
            // Reemplazar alert nativo
            window.alert = (message) => {
                this.info(message, 'Aviso', {
                    duration: 0,
                    dismissible: true,
                    actions: [{
                        text: 'Aceptar',
                        type: 'primary',
                        icon: 'fas fa-check',
                        callback: () => {}
                    }]
                });
            };

            // Retornar función para restaurar alert original
            return () => {
                window.alert = originalAlert;
            };
        }
    }

    // Exportar SIEMPRE a window y como variable global
    window.QuickExitNotifications = new QuickExitNotifications();
    window.showNotification = (type, message, title, options) => {
        return window.QuickExitNotifications.show({ type, message, title, ...options });
    };
    window.showSuccess = (message, title, options) => {
        return window.QuickExitNotifications.success(message, title, options);
    };
    window.showError = (message, title, options) => {
        return window.QuickExitNotifications.error(message, title, options);
    };
    window.showWarning = (message, title, options) => {
        return window.QuickExitNotifications.warning(message, title, options);
    };
    window.showInfo = (message, title, options) => {
        return window.QuickExitNotifications.info(message, title, options);
    };
    // Para compatibilidad avanzada
    window.QuickExitNotificationsShow = (...args) => window.QuickExitNotifications.show(...args);

    // Integración con mensajes flash de Flask
    document.addEventListener('DOMContentLoaded', function() {
        // Buscar mensajes flash existentes y convertirlos a notificaciones
        const flashMessages = document.querySelectorAll('.alert');
        
        flashMessages.forEach(alert => {
            const message = alert.textContent.trim();
            let type = 'info';
            
            // Determinar tipo basado en las clases CSS
            if (alert.classList.contains('alert-danger')) {
                type = 'danger';
            } else if (alert.classList.contains('alert-warning')) {
                type = 'warning';
            } else if (alert.classList.contains('alert-success')) {
                type = 'success';
            } else if (alert.classList.contains('alert-info')) {
                type = 'info';
            }

            // Mostrar notificación
            window.QuickExitNotifications.show({
                type,
                message,
                duration: 6000,
                dismissible: true
            });

            // Remover el alert original
            alert.remove();
        });
    });

    // Exportar para uso en módulos
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = QuickExitNotifications;
    }
})(); 