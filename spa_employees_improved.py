@login_required
def spa_employees_improved(request):
    """Vue SPA améliorée pour la gestion des employés - Intégration complète"""
    try:
        # Récupérer les employés avec leurs relations
        employes = Employe.objects.select_related('site', 'departement', 'user').order_by('nom', 'prenom')
        
        # Récupérer les sites et départements pour les filtres
        sites = Site.objects.filter(actif=True).order_by('nom')
        departements = Departement.objects.filter(actif=True).order_by('nom')
        
        # Construire le HTML des employés
        employes_html = ""
        for employe in employes:
            status_badge = "success" if employe.actif else "secondary"
            status_text = "Actif" if employe.actif else "Inactif"
            
            employes_html += f'''
            <tr class="employee-row" data-site="{employe.site_id or ''}" data-dept="{employe.departement_id or ''}">
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-circle bg-primary text-white d-flex align-items-center justify-content-center me-3">
                            {employe.nom[0]}{employe.prenom[0]}
                        </div>
                        <div>
                            <strong>{employe.nom} {employe.prenom}</strong>
                            <br><small class="text-muted">#{employe.matricule}</small>
                        </div>
                    </div>
                </td>
                <td>{employe.fonction or 'Non défini'}</td>
                <td><span class="text-success fw-bold">{float(employe.salaire_base):,.0f} DH</span></td>
                <td>{employe.site.nom if employe.site else 'Non assigné'}</td>
                <td>{employe.departement.nom if employe.departement else 'Non assigné'}</td>
                <td><span class="badge bg-{status_badge}">{status_text}</span></td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-info btn-action" onclick="viewEmployeeDetails({employe.id})" title="Voir détails">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-outline-warning btn-action" onclick="editEmployeeForm({employe.id})" title="Modifier">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-action" onclick="deactivateEmployee({employe.id}, '{employe.nom} {employe.prenom}')" title="Désactiver">
                            <i class="fas fa-user-times"></i>
                        </button>
                    </div>
                </td>
            </tr>
            '''

        # HTML complet de la page employés intégrée pour SPA
        html_content = f'''
        <div class="employees-management-spa">
            <!-- En-tête avec titre -->
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-gradient d-flex align-items-center">
                        <i class="fas fa-users text-primary me-3"></i>
                        Gestion des Employés
                        <span class="badge bg-info ms-3" id="employeeCount">{employes.count()}</span>
                    </h2>
                </div>
            </div>
            
            <!-- Section Filtres et Actions -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-light">
                            <h5 class="mb-0"><i class="fas fa-filter me-2"></i>Filtres et Actions</h5>
                        </div>
                        <div class="card-body">
                            <div class="row g-3 align-items-end">
                                <!-- Recherche -->
                                <div class="col-md-3">
                                    <label class="form-label fw-bold">Rechercher</label>
                                    <input type="text" id="searchInput" class="form-control" 
                                           placeholder="Nom, prénom, matricule..." 
                                           onkeyup="filterEmployees()">
                                </div>
                                
                                <!-- Site -->
                                <div class="col-md-3">
                                    <label class="form-label fw-bold">Site</label>
                                    <select id="siteFilter" class="form-select" onchange="filterEmployees(); updateDepartements();">
                                        <option value="">Tous les sites</option>
                                        {"".join([f'<option value="{site.id}">{site.nom}</option>' for site in sites])}
                                    </select>
                                </div>
                                
                                <!-- Département -->
                                <div class="col-md-3">
                                    <label class="form-label fw-bold">Département</label>
                                    <select id="deptFilter" class="form-select" onchange="filterEmployees()">
                                        <option value="">Tous les départements</option>
                                        {"".join([f'<option value="{dept.id}">{dept.nom}</option>' for dept in departements])}
                                    </select>
                                </div>
                                
                                <!-- Actions -->
                                <div class="col-md-3">
                                    <div class="d-grid gap-2">
                                        <button class="btn btn-success" onclick="addNewEmployee()">
                                            <i class="fas fa-plus me-2"></i>Ajouter Employé
                                        </button>
                                        <button class="btn btn-primary" onclick="exportToExcel()">
                                            <i class="fas fa-download me-2"></i>Export Excel
                                        </button>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Boutons utilitaires -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <button class="btn btn-outline-secondary btn-sm" onclick="clearAllFilters()">
                                        <i class="fas fa-times me-1"></i>Effacer les filtres
                                    </button>
                                    <button class="btn btn-outline-info btn-sm ms-2" onclick="loadSPAContent('employees')">
                                        <i class="fas fa-sync me-1"></i>Actualiser
                                    </button>
                                    <span id="filterResults" class="ms-3 text-muted"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Section Liste des Employés -->
            <div class="row">
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-white">
                            <h5 class="mb-0">
                                <i class="fas fa-list me-2"></i>Liste des Employés
                            </h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0" id="employeesTable">
                                    <thead class="table-light">
                                        <tr>
                                            <th width="250">Employé</th>
                                            <th>Fonction</th>
                                            <th>Salaire</th>
                                            <th>Site</th>
                                            <th>Département</th>
                                            <th>Statut</th>
                                            <th width="150">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="employeesTableBody">
                                        {employes_html}
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- Message si aucun résultat -->
                            <div id="noResults" class="text-center py-5" style="display: none;">
                                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                                <h5 class="text-muted">Aucun employé trouvé</h5>
                                <p class="text-muted">Essayez de modifier vos critères de recherche</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal pour Employé -->
        <div class="modal fade" id="employeeModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="employeeModalTitle">Gestion Employé</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="employeeModalBody">
                        <!-- Contenu dynamique chargé ici -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Modal Détails Employé -->
        <div class="modal fade" id="employeeDetailsModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Détails de l'Employé</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" id="employeeDetailsModalBody">
                        <!-- Contenu dynamique chargé ici -->
                    </div>
                </div>
            </div>
        </div>

        <style>
        .employees-management-spa {{
            padding: 0;
        }}
        .card {{
            border-radius: 12px;
        }}
        .btn-action {{
            padding: 0.25rem 0.5rem;
            font-size: 0.875rem;
            margin: 0 2px;
        }}
        .avatar-circle {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            font-size: 14px;
            font-weight: bold;
        }}
        .employee-row:hover {{
            background-color: #f8f9fa;
        }}
        .form-control:focus, .form-select:focus {{
            border-color: #007bff;
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        }}
        .text-gradient {{
            background: linear-gradient(45deg, #007bff, #6610f2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        </style>

        <script>
        console.log('📋 Script SPA Employés amélioré chargé');

        // Variables globales pour la SPA
        let allDepartements = [];

        // Charger les départements depuis l'API
        async function loadDepartements() {{
            try {{
                const response = await fetch('/api/departements/', {{
                    headers: {{ 'X-Requested-With': 'XMLHttpRequest' }}
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    allDepartements = data.departements || [];
                }}
            }} catch (error) {{
                console.log('Utilisation des départements par défaut');
            }}
        }}

        // Mettre à jour les départements selon le site sélectionné
        function updateDepartements() {{
            const siteId = document.getElementById('siteFilter').value;
            const deptFilter = document.getElementById('deptFilter');
            
            deptFilter.innerHTML = '<option value="">Tous les départements</option>';
            
            const departementsFiltered = siteId ? 
                allDepartements.filter(dept => dept.site_id == siteId) : 
                allDepartements;
            
            departementsFiltered.forEach(dept => {{
                const option = document.createElement('option');
                option.value = dept.id;
                option.textContent = dept.nom;
                deptFilter.appendChild(option);
            }});
        }}

        // Filtrer les employés
        function filterEmployees() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const selectedSite = document.getElementById('siteFilter').value;
            const selectedDept = document.getElementById('deptFilter').value;
            
            const rows = document.querySelectorAll('.employee-row');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                const siteId = row.getAttribute('data-site');
                const deptId = row.getAttribute('data-dept');
                
                const matchesSearch = !searchTerm || text.includes(searchTerm);
                const matchesSite = !selectedSite || siteId === selectedSite;
                const matchesDept = !selectedDept || deptId === selectedDept;
                
                if (matchesSearch && matchesSite && matchesDept) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            // Mettre à jour l'affichage
            document.getElementById('employeeCount').textContent = visibleCount;
            document.getElementById('filterResults').textContent = 
                visibleCount === rows.length ? 
                `${{visibleCount}} employé(s)` : 
                `${{visibleCount}} sur ${{rows.length}} employé(s)`;
            
            // Afficher/masquer le message "aucun résultat"
            const noResults = document.getElementById('noResults');
            if (visibleCount === 0 && rows.length > 0) {{
                noResults.style.display = 'block';
                document.getElementById('employeesTable').style.display = 'none';
            }} else {{
                noResults.style.display = 'none';
                document.getElementById('employeesTable').style.display = '';
            }}
        }}

        // Effacer tous les filtres
        function clearAllFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('siteFilter').value = '';
            document.getElementById('deptFilter').value = '';
            updateDepartements();
            filterEmployees();
            if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                PayrollPro.notify('Filtres effacés', 'info');
            }}
        }}

        // ===== ACTIONS SUR LES EMPLOYÉS =====

        // Ajouter un nouvel employé
        async function addNewEmployee() {{
            try {{
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.show();
                }}
                
                const response = await fetch('/creer_employe/', {{
                    method: 'GET',
                    headers: {{ 'X-Requested-With': 'XMLHttpRequest' }}
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    if (data.success) {{
                        document.getElementById('employeeModalTitle').textContent = 'Ajouter un Nouvel Employé';
                        document.getElementById('employeeModalBody').innerHTML = data.form_html;
                        new bootstrap.Modal(document.getElementById('employeeModal')).show();
                        if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                            PayrollPro.notify('Formulaire d\\'ajout chargé', 'success');
                        }}
                    }} else {{
                        throw new Error(data.error);
                    }}
                }} else {{
                    throw new Error('Erreur lors du chargement du formulaire');
                }}
                
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.hide();
                }}
            }} catch (error) {{
                if (typeof PayrollPro !== 'undefined') {{
                    if (PayrollPro.loading) PayrollPro.loading.hide();
                    if (PayrollPro.notify) PayrollPro.notify('Erreur: ' + error.message, 'error');
                }}
                console.error('Erreur ajout employé:', error);
            }}
        }}

        // Modifier un employé
        async function editEmployeeForm(employeeId) {{
            try {{
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.show();
                }}
                
                const response = await fetch(`/modifier_employe/${{employeeId}}/`, {{
                    method: 'GET',
                    headers: {{ 'X-Requested-With': 'XMLHttpRequest' }}
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    if (data.success) {{
                        document.getElementById('employeeModalTitle').textContent = 'Modifier l\\'Employé';
                        document.getElementById('employeeModalBody').innerHTML = data.form_html;
                        new bootstrap.Modal(document.getElementById('employeeModal')).show();
                        if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                            PayrollPro.notify('Formulaire de modification chargé', 'success');
                        }}
                    }} else {{
                        throw new Error(data.error);
                    }}
                }} else {{
                    throw new Error('Erreur lors du chargement du formulaire');
                }}
                
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.hide();
                }}
            }} catch (error) {{
                if (typeof PayrollPro !== 'undefined') {{
                    if (PayrollPro.loading) PayrollPro.loading.hide();
                    if (PayrollPro.notify) PayrollPro.notify('Erreur: ' + error.message, 'error');
                }}
                console.error('Erreur modification employé:', error);
            }}
        }}

        // Voir les détails d'un employé
        async function viewEmployeeDetails(employeeId) {{
            try {{
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.show();
                }}
                
                const response = await fetch(`/detail_employe/${{employeeId}}/`, {{
                    headers: {{ 'X-Requested-With': 'XMLHttpRequest' }}
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    if (data.success) {{
                        document.getElementById('employeeDetailsModalBody').innerHTML = generateEmployeeDetailsHTML(data);
                        new bootstrap.Modal(document.getElementById('employeeDetailsModal')).show();
                        if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                            PayrollPro.notify('Détails chargés', 'success');
                        }}
                    }} else {{
                        throw new Error(data.error);
                    }}
                }} else {{
                    throw new Error('Erreur lors du chargement des détails');
                }}
                
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.hide();
                }}
            }} catch (error) {{
                if (typeof PayrollPro !== 'undefined') {{
                    if (PayrollPro.loading) PayrollPro.loading.hide();
                    if (PayrollPro.notify) PayrollPro.notify('Erreur: ' + error.message, 'error');
                }}
                console.error('Erreur détails employé:', error);
            }}
        }}

        // Générer le HTML des détails de l'employé
        function generateEmployeeDetailsHTML(data) {{
            const emp = data.employe;
            return `
                <div class="row">
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header bg-primary text-white">
                                <h6 class="mb-0"><i class="fas fa-user me-2"></i>Informations Personnelles</h6>
                            </div>
                            <div class="card-body">
                                <table class="table table-sm table-borderless">
                                    <tr><th width="120">Matricule:</th><td><strong>${{emp.matricule}}</strong></td></tr>
                                    <tr><th>Nom complet:</th><td><strong>${{emp.nom}} ${{emp.prenom}}</strong></td></tr>
                                    <tr><th>Fonction:</th><td>${{emp.fonction || 'Non défini'}}</td></tr>
                                    <tr><th>Salaire de base:</th><td class="text-success fw-bold">${{emp.salaire_base.toLocaleString()}} DH</td></tr>
                                    <tr><th>Date d'embauche:</th><td>${{emp.date_embauche || 'Non défini'}}</td></tr>
                                    <tr><th>Téléphone:</th><td>${{emp.telephone || 'Non défini'}}</td></tr>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header bg-info text-white">
                                <h6 class="mb-0"><i class="fas fa-cog me-2"></i>Informations Système</h6>
                            </div>
                            <div class="card-body">
                                <table class="table table-sm table-borderless">
                                    <tr><th width="120">Site:</th><td>${{emp.site || 'Non assigné'}}</td></tr>
                                    <tr><th>Département:</th><td>${{emp.departement || 'Non assigné'}}</td></tr>
                                    <tr><th>Statut:</th><td><span class="badge bg-${{emp.actif ? 'success' : 'secondary'}}">${{emp.actif ? 'Actif' : 'Inactif'}}</span></td></tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }}

        // Supprimer/désactiver un employé
        async function deactivateEmployee(employeeId, employeeName) {{
            if (!confirm(`Êtes-vous sûr de vouloir désactiver l'employé ${{employeeName}} ?`)) {{
                return;
            }}

            try {{
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.show();
                }}
                
                const response = await fetch(`/api/employe/${{employeeId}}/delete/`, {{
                    method: 'POST',
                    headers: {{
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': getCSRFToken()
                    }}
                }});
                
                if (response.ok) {{
                    const data = await response.json();
                    if (data.success) {{
                        if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                            PayrollPro.notify(data.message, 'success');
                        }}
                        loadSPAContent('employees'); // Recharger la liste
                    }} else {{
                        throw new Error(data.error);
                    }}
                }} else {{
                    throw new Error('Erreur lors de la suppression');
                }}
                
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.hide();
                }}
            }} catch (error) {{
                if (typeof PayrollPro !== 'undefined') {{
                    if (PayrollPro.loading) PayrollPro.loading.hide();
                    if (PayrollPro.notify) PayrollPro.notify('Erreur: ' + error.message, 'error');
                }}
                console.error('Erreur suppression employé:', error);
            }}
        }}

        // Exporter vers Excel
        async function exportToExcel() {{
            try {{
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.show();
                }}
                if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                    PayrollPro.notify('Génération de l\\'export en cours...', 'info');
                }}
                
                const response = await fetch('/api/employees/export/', {{
                    headers: {{ 'X-Requested-With': 'XMLHttpRequest' }}
                }});
                
                if (response.ok) {{
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `employes_${{new Date().toISOString().split('T')[0]}}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    if (typeof PayrollPro !== 'undefined' && PayrollPro.notify) {{
                        PayrollPro.notify('Export terminé avec succès', 'success');
                    }}
                }} else {{
                    throw new Error('Erreur lors de l\\'export');
                }}
                
                if (typeof PayrollPro !== 'undefined' && PayrollPro.loading) {{
                    PayrollPro.loading.hide();
                }}
            }} catch (error) {{
                if (typeof PayrollPro !== 'undefined') {{
                    if (PayrollPro.loading) PayrollPro.loading.hide();
                    if (PayrollPro.notify) PayrollPro.notify('Erreur lors de l\\'export: ' + error.message, 'error');
                }}
                console.error('Erreur export:', error);
            }}
        }}

        // Utilitaires
        function getCSRFToken() {{
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {{
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {{
                    return value;
                }}
            }}
            return '';
        }}

        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {{
            loadDepartements();
            filterEmployees();
        }});

        // Charger au chargement de la section si elle est déjà visible
        if (document.getElementById('searchInput')) {{
            loadDepartements();
            filterEmployees();
        }}

        console.log('✅ Script SPA Employés amélioré initialisé avec succès');
        </script>
        '''

        return JsonResponse({
            'success': True,
            'content': html_content
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors du chargement des employés: {str(e)}'
        })
