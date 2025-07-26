// static/js/payrollpro-advanced.js
/**
 * PayrollPro - JavaScript avancé pour les interfaces modernes
 * Fonctionnalités: filtres dynamiques, pagination AJAX, animations
 */

class PayrollProAdvanced {
    constructor() {
        this.currentFilters = {};
        this.debounceTimer = null;
        this.loadingStates = new Set();
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupFilterDependencies();
        this.setupKeyboardShortcuts();
        this.setupAnimations();
        console.log('PayrollPro Advanced UI initialized');
    }

    // ===== GESTION DES FILTRES DYNAMIQUES =====

    setupEventListeners() {
        // Filtres en temps réel
        document.addEventListener('input', (e) => {
            if (e.target.matches('[data-filter="search"]')) {
                this.debounceFilter(() => this.applyFilters(), 300);
            }
        });

        // Changement de sélecteurs
        document.addEventListener('change', (e) => {
            if (e.target.matches('select[data-filter]')) {
                this.handleFilterChange(e.target);
            }
        });

        // Filtres de date
        document.addEventListener('change', (e) => {
            if (e.target.matches('input[type="date"][data-filter]')) {
                this.applyFilters();
            }
        });

        // Pagination AJAX
        document.addEventListener('click', (e) => {
            if (e.target.matches('.pagination a')) {
                e.preventDefault();
                this.changePage(e.target.href);
            }
        });
    }

    setupFilterDependencies() {
        // Site -> Département (cascade)
        const siteSelect = document.querySelector('select[data-filter="site"]');
        if (siteSelect) {
            siteSelect.addEventListener('change', (e) => {
                this.updateDepartmentOptions(e.target.value);
            });
        }
    }

    async updateDepartmentOptions(siteId) {
        const departmentSelect = document.querySelector('select[data-filter="departement"]');
        if (!departmentSelect) return;

        if (!siteId) {
            this.resetDepartmentOptions();
            return;
        }

        try {
            this.showLoading(departmentSelect);
            const response = await fetch(`/api/site/${siteId}/departements/`);
            const departements = await response.json();

            // Vider et repeupler
            departmentSelect.innerHTML = '<option value="">Tous les départements</option>';
            departements.forEach(dept => {
                const option = document.createElement('option');
                option.value = dept.id;
                option.textContent = `${dept.code} - ${dept.nom}`;
                departmentSelect.appendChild(option);
            });

            this.hideLoading(departmentSelect);
            this.applyFilters();

        } catch (error) {
            console.error('Erreur lors du chargement des départements:', error);
            this.showNotification('Erreur lors du chargement des départements', 'error');
            this.hideLoading(departmentSelect);
        }
    }

    resetDepartmentOptions() {
        const departmentSelect = document.querySelector('select[data-filter="departement"]');
        if (departmentSelect) {
            departmentSelect.innerHTML = '<option value="">Tous les départements</option>';
            // Ajouter toutes les options par défaut si nécessaire
        }
    }

    debounceFilter(func, delay) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(func, delay);
    }

    async applyFilters() {
        // Collecter tous les filtres
        this.currentFilters = this.collectFilters();
        
        // Construire l'URL avec les paramètres
        const url = new URL(window.location);
        Object.keys(this.currentFilters).forEach(key => {
            if (this.currentFilters[key]) {
                url.searchParams.set(key, this.currentFilters[key]);
            } else {
                url.searchParams.delete(key);
            }
        });

        try {
            this.showGlobalLoading();
            
            // Requête AJAX
            const response = await fetch(url.toString(), {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateResults(data);
                this.updateURL(url);
                this.updateStats(data.stats);
            } else {
                throw new Error('Erreur lors du filtrage');
            }

        } catch (error) {
            console.error('Erreur lors de l\'application des filtres:', error);
            this.showNotification('Erreur lors du filtrage', 'error');
        } finally {
            this.hideGlobalLoading();
        }
    }

    collectFilters() {
        const filters = {};
        
        // Sélecteurs
        document.querySelectorAll('select[data-filter]').forEach(select => {
            filters[select.dataset.filter] = select.value;
        });

        // Champs de recherche
        document.querySelectorAll('input[data-filter="search"]').forEach(input => {
            filters['recherche'] = input.value;
        });

        // Dates
        document.querySelectorAll('input[type="date"][data-filter]').forEach(input => {
            filters[input.dataset.filter] = input.value;
        });

        return filters;
    }

    updateResults(data) {
        // Mettre à jour le contenu principal
        const resultsContainer = document.querySelector('[data-results="main"]');
        if (resultsContainer && data.html) {
            resultsContainer.innerHTML = data.html;
            this.animateNewResults();
        }

        // Mettre à jour la pagination
        if (data.pagination) {
            this.updatePagination(data.pagination);
        }
    }

    updateStats(stats) {
        if (!stats) return;

        // Mettre à jour les cartes de statistiques
        Object.keys(stats).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                this.animateCounter(element, stats[key]);
            }
        });
    }

    updateURL(url) {
        // Mettre à jour l'URL sans recharger la page
        window.history.pushState({}, '', url.toString());
    }

    // ===== ANIMATIONS =====

    setupAnimations() {
        // Observer pour les animations d'entrée
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        });

        // Observer tous les éléments animables
        document.querySelectorAll('.slide-in, .fade-in').forEach(el => {
            this.observer.observe(el);
        });
    }

    animateNewResults() {
        // Animer les nouveaux résultats
        const newElements = document.querySelectorAll('[data-results="main"] .employee-card, [data-results="main"] .absence-card');
        newElements.forEach((el, index) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            setTimeout(() => {
                el.style.transition = 'all 0.3s ease';
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }

    animateCounter(element, targetValue) {
        const startValue = parseInt(element.textContent.replace(/[^\d]/g, '')) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.round(startValue + (targetValue - startValue) * easeOutQuart);
            
            // Formater selon le type de donnée
            if (element.dataset.format === 'currency') {
                element.textContent = currentValue.toLocaleString() + ' DH';
            } else {
                element.textContent = currentValue.toLocaleString();
            }

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    // ===== GESTION DU LOADING =====

    showGlobalLoading() {
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Chargement...</span>
                </div>
                <div class="mt-2">Filtrage en cours...</div>
            </div>
        `;
        document.body.appendChild(loadingOverlay);
    }

    hideGlobalLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }

    showLoading(element) {
        element.classList.add('loading');
        this.loadingStates.add(element);
    }

    hideLoading(element) {
        element.classList.remove('loading');
        this.loadingStates.delete(element);
    }

    // ===== NOTIFICATIONS =====

    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        const colors = {
            'success': 'bg-success',
            'error': 'bg-danger',
            'warning': 'bg-warning',
            'info': 'bg-info'
        };

        notification.className = `notification position-fixed top-0 end-0 m-3 p-3 rounded text-white ${colors[type]}`;
        notification.style.zIndex = '9999';
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        
        const icons = {
            'success': 'check-circle',
            'error': 'x-circle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };

        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${icons[type]} me-2"></i>
                ${message}
                <button type="button" class="btn-close btn-close-white ms-2" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;

        document.body.appendChild(notification);

        // Animation d'entrée
        setTimeout(() => {
            notification.style.transition = 'all 0.3s ease';
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 100);

        // Suppression automatique
        if (duration > 0) {
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }, duration);
        }
    }

    // ===== RACCOURCIS CLAVIER =====

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl + F : Focus sur la recherche
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault();
                const searchInput = document.querySelector('input[data-filter="search"]');
                if (searchInput) {
                    searchInput.focus();
                    searchInput.select();
                }
            }

            // Escape : Réinitialiser les filtres
            if (e.key === 'Escape') {
                this.resetAllFilters();
            }

            // Ctrl + Enter : Appliquer les filtres
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.applyFilters();
            }
        });
    }

    resetAllFilters() {
        // Réinitialiser tous les filtres
        document.querySelectorAll('select[data-filter]').forEach(select => {
            select.value = '';
        });

        document.querySelectorAll('input[data-filter]').forEach(input => {
            input.value = '';
        });

        this.applyFilters();
        this.showNotification('Filtres réinitialisés', 'info');
    }

    // ===== PAGINATION AJAX =====

    async changePage(url) {
        try {
            this.showGlobalLoading();
            
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateResults(data);
                this.updateURL(new URL(url));
                
                // Scroll vers le haut des résultats
                const resultsContainer = document.querySelector('[data-results="main"]');
                if (resultsContainer) {
                    resultsContainer.scrollIntoView({ behavior: 'smooth' });
                }
            }
        } catch (error) {
            console.error('Erreur lors du changement de page:', error);
            this.showNotification('Erreur lors du changement de page', 'error');
        } finally {
            this.hideGlobalLoading();
        }
    }

    updatePagination(paginationData) {
        const paginationContainer = document.querySelector('.pagination-container');
        if (paginationContainer && paginationData) {
            // Mettre à jour les informations de pagination
            const pageInfo = document.querySelector('.page-info');
            if (pageInfo) {
                pageInfo.textContent = `Page ${paginationData.page} sur ${paginationData.total_pages} (${paginationData.total_items} éléments)`;
            }
        }
    }

    // ===== UTILITAIRES =====

    static formatCurrency(amount) {
        return new Intl.NumberFormat('fr-MA', {
            style: 'currency',
            currency: 'MAD',
            minimumFractionDigits: 0
        }).format(amount).replace('MAD', 'DH');
    }

    static formatNumber(number) {
        return new Intl.NumberFormat('fr-MA').format(number);
    }

    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// ===== COMPOSANTS SPÉCIALISÉS =====

class EmployeeFilters extends PayrollProAdvanced {
    constructor() {
        super();
        this.setupEmployeeSpecificFeatures();
    }

    setupEmployeeSpecificFeatures() {
        // Filtres spécifiques aux employés
        this.setupSalaryRangeFilter();
        this.setupBulkActions();
    }

    setupSalaryRangeFilter() {
        const salaryMin = document.querySelector('#salaryMin');
        const salaryMax = document.querySelector('#salaryMax');
        
        if (salaryMin && salaryMax) {
            [salaryMin, salaryMax].forEach(input => {
                input.addEventListener('input', this.debounce(() => {
                    this.applyFilters();
                }, 500));
            });
        }
    }

    setupBulkActions() {
        // Sélection multiple
        const selectAllCheckbox = document.querySelector('#selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                const checkboxes = document.querySelectorAll('.employee-checkbox');
                checkboxes.forEach(cb => cb.checked = e.target.checked);
                this.updateBulkActionButtons();
            });
        }

        // Mise à jour des boutons d'actions groupées
        document.addEventListener('change', (e) => {
            if (e.target.matches('.employee-checkbox')) {
                this.updateBulkActionButtons();
            }
        });
    }

    updateBulkActionButtons() {
        const selectedCount = document.querySelectorAll('.employee-checkbox:checked').length;
        const bulkButtons = document.querySelectorAll('.bulk-action-btn');
        
        bulkButtons.forEach(btn => {
            btn.disabled = selectedCount === 0;
            const countSpan = btn.querySelector('.selected-count');
            if (countSpan) {
                countSpan.textContent = selectedCount;
            }
        });
    }
}

// ===== INITIALISATION =====

document.addEventListener('DOMContentLoaded', function() {
    // Détecter la page et initialiser le bon composant
    if (document.querySelector('[data-page="employes"]')) {
        window.payrollPro = new EmployeeFilters();
    } else {
        window.payrollPro = new PayrollProAdvanced();
    }

    // Initialiser les tooltips Bootstrap si disponible
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// ===== CSS POUR LES ANIMATIONS =====
const style = document.createElement('style');
style.textContent = `
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(2px);
    }

    .loading-spinner {
        background: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }

    .loading {
        position: relative;
        pointer-events: none;
        opacity: 0.6;
    }

    .loading::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 20px;
        height: 20px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        transform: translate(-50%, -50%);
        z-index: 1000;
    }

    @keyframes spin {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }

    .animate-in {
        animation: slideInUp 0.6s ease forwards;
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .notification {
        animation: slideInRight 0.3s ease;
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    /* Amélioration des filtres */
    .filter-section {
        transition: all 0.3s ease;
    }

    .filter-section:hover {
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }

    /* Responsive amélioré */
    @media (max-width: 768px) {
        .loading-spinner {
            margin: 0 20px;
            padding: 20px;
        }

        .notification {
            margin: 10px !important;
            left: 10px;
            right: 10px;
        }
    }
`;

document.head.appendChild(style);