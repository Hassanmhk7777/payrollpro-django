// ==========================================================================
// JAVASCRIPT UNIFIÉ ET CORRIGÉ - GESTION DES EMPLOYÉS
// ==========================================================================

// Variables globales
let currentFilters = {
    search: '',
    site: '',
    department: '',
    status: ''
};

// Fonction principale de filtrage UNIFIÉE
function filterEmployees() {
    console.log('🔍 Filtrage des employés');
    
    // Récupérer les valeurs des filtres
    const searchTerm = document.getElementById('searchInput')?.value.toLowerCase() || '';
    const selectedSite = document.getElementById('siteFilter')?.value || '';
    const selectedDept = document.getElementById('departmentFilter')?.value || '';
    const selectedStatus = document.getElementById('statusFilter')?.value || '';
    
    // Mettre à jour l'objet filtres
    currentFilters = {
        search: searchTerm,
        site: selectedSite,
        department: selectedDept,
        status: selectedStatus
    };
    
    // Obtenir toutes les lignes d'employés
    const rows = document.querySelectorAll('.employee-row');
    let visibleCount = 0;
    
    // Appliquer les filtres
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const siteId = row.getAttribute('data-site');
        const deptId = row.getAttribute('data-dept');
        const status = row.getAttribute('data-status');
        
        // Tests de correspondance
        const matchesSearch = !searchTerm || text.includes(searchTerm);
        const matchesSite = !selectedSite || siteId === selectedSite;
        const matchesDept = !selectedDept || deptId === selectedDept;
        const matchesStatus = !selectedStatus || status === selectedStatus;
        
        // Afficher/masquer la ligne
        if (matchesSearch && matchesSite && matchesDept && matchesStatus) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Gérer l'affichage du message "aucun résultat"
    updateEmptyState(visibleCount);
    
    // Mettre à jour le compteur
    updateResultCount(visibleCount);
    
    // Notification
    showNotification(`${visibleCount} employé(s) trouvé(s)`, 'info');
}

// Fonction pour gérer l'état vide
function updateEmptyState(visibleCount) {
    const noEmployeesRow = document.getElementById('noEmployeesRow');
    const hasEmployees = document.querySelectorAll('.employee-row').length > 0;
    
    if (hasEmployees && visibleCount === 0) {
        // Créer ligne "aucun résultat" si elle n'existe pas
        if (!document.getElementById('noResultsRow')) {
            const tbody = document.getElementById('employeeTableBody');
            const noResultsRow = document.createElement('tr');
            noResultsRow.id = 'noResultsRow';
            noResultsRow.innerHTML = `
                <td colspan="9" class="text-center py-4">
                    <div class="empty-state">
                        <i class="fas fa-search fa-3x text-muted mb-3"></i>
                        <h5 class="text-muted">Aucun employé ne correspond aux critères</h5>
                        <p class="text-muted">Essayez de modifier vos filtres</p>
                    </div>
                </td>
            `;
            tbody.appendChild(noResultsRow);
        }
        document.getElementById('noResultsRow').style.display = '';
    } else {
        // Masquer la ligne "aucun résultat"
        const noResultsRow = document.getElementById('noResultsRow');
        if (noResultsRow) {
            noResultsRow.style.display = 'none';
        }
    }
}

// Fonction pour mettre à jour le compteur de résultats
function updateResultCount(count) {
    const resultCountElement = document.getElementById('resultCount');
    if (resultCountElement) {
        resultCountElement.textContent = `${count} résultats`;
    }
}

// Fonction pour réinitialiser les filtres
function resetFilters() {
    console.log('🧹 Réinitialisation des filtres');
    
    // Réinitialiser les champs
    document.getElementById('searchInput').value = '';
    document.getElementById('siteFilter').value = '';
    document.getElementById('departmentFilter').value = '';
    document.getElementById('statusFilter').value = '';
    
    // Réinitialiser l'objet filtres
    currentFilters = {
        search: '',
        site: '',
        department: '',
        status: ''
    };
    
    // Réappliquer les filtres (afficher tout)
    filterEmployees();
    
    showNotification('Filtres réinitialisés', 'success');
}

// Fonctions pour les actions sur les employés
function viewEmployeeDetails(id) {
    console.log(`👁️ Voir détails employé ${id}`);
    showNotification(`Affichage des détails de l'employé #${id}`, 'info');
    // TODO: Implémenter la modal de détails
}

function editEmployee(id) {
    console.log(`✏️ Modifier employé ${id}`);
    showNotification(`Modification de l'employé #${id}`, 'info');
    // TODO: Rediriger vers le formulaire d'édition
    window.location.href = `/employes/modifier/${id}/`;
}

function toggleEmployeeStatus(id, name, isActive) {
    const action = isActive ? 'désactiver' : 'activer';
    const actionCap = isActive ? 'Désactivation' : 'Activation';
    
    if (confirm(`Êtes-vous sûr de vouloir ${action} l'employé ${name} ?`)) {
        console.log(`🔄 ${actionCap} employé ${id}`);
        
        // Afficher le loading
        showNotification(`${actionCap} en cours...`, 'info');
        
        // Faire la requête AJAX
        const url = isActive ? `/api/employes/${id}/desactiver/` : `/api/employes/${id}/activer/`;
        
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                // Recharger la ligne ou la page
                location.reload();
            } else {
                showNotification(data.error || `Erreur lors de la ${action}`, 'error');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            showNotification(`Erreur lors de la ${action}`, 'error');
        });
    }
}

// Fonction d'export Excel
function exportToExcel() {
    console.log('📥 Export Excel des employés');
    showNotification('Export en cours...', 'info');
    
    fetch('/api/employes/export/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Erreur lors de l\'export');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `employes_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        showNotification('Export terminé avec succès', 'success');
    })
    .catch(error => {
        console.error('Erreur export:', error);
        showNotification('Erreur lors de l\'export', 'error');
    });
}

// Utilitaires
function getCsrfToken() {
    const cookie = document.cookie.split(';')
        .find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

function showNotification(message, type = 'info') {
    // Créer le conteneur de notifications s'il n'existe pas
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    // Créer la notification
    const notification = document.createElement('div');
    const bgClass = {
        'success': 'bg-success',
        'error': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-info';
    
    notification.className = `alert ${bgClass} text-white alert-dismissible fade show mb-2`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close btn-close-white" aria-label="Close"></button>
    `;
    
    // Ajouter la notification
    container.appendChild(notification);
    
    // Gérer la fermeture
    const closeBtn = notification.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => {
        notification.remove();
    });
    
    // Auto-suppression après 5 secondes
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Gestion de la sélection multiple
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initialisation de la gestion des employés');
    
    // Gestion du "Tout sélectionner"
    const selectAllCheckbox = document.getElementById('selectAll');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const checkboxes = document.querySelectorAll('.employee-checkbox');
            checkboxes.forEach(cb => {
                if (cb.closest('.employee-row').style.display !== 'none') {
                    cb.checked = this.checked;
                }
            });
        });
    }
    
    // Initialiser les filtres si des paramètres URL sont présents
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('site')) {
        document.getElementById('siteFilter').value = urlParams.get('site');
    }
    if (urlParams.get('search')) {
        document.getElementById('searchInput').value = urlParams.get('search');
    }
    
    // Appliquer les filtres initiaux
    filterEmployees();
});

console.log('✅ JavaScript de gestion des employés chargé');
