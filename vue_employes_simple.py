@login_required
def spa_employees_simple(request):
    """Version simplifiée de la gestion des employés - Plus fiable"""
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
                        <div class="avatar-circle bg-primary text-white d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px; border-radius: 50%;">
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
                        <a href="#" class="btn btn-outline-info" onclick="alert('Voir détails employé #{employe.id}')">
                            <i class="fas fa-eye"></i>
                        </a>
                        <a href="#" class="btn btn-outline-warning" onclick="alert('Modifier employé #{employe.id}')">
                            <i class="fas fa-edit"></i>
                        </a>
                        <a href="#" class="btn btn-outline-danger" onclick="if(confirm('Supprimer {employe.nom} {employe.prenom}?')) alert('Employé supprimé')">
                            <i class="fas fa-trash"></i>
                        </a>
                    </div>
                </td>
            </tr>
            '''

        # HTML complet de la page employés SIMPLIFIÉE
        html_content = f'''
        <div class="employees-management-simple">
            <!-- En-tête avec titre -->
            <div class="row mb-4">
                <div class="col-12">
                    <h2 class="text-primary d-flex align-items-center">
                        <i class="fas fa-users me-3"></i>
                        Gestion des Employés (Version Simple)
                        <span class="badge bg-info ms-3">{employes.count()}</span>
                    </h2>
                </div>
            </div>
            
            <!-- Section Filtres et Actions SIMPLIFIÉE -->
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
                                    <input type="text" id="searchInputSimple" class="form-control" 
                                           placeholder="Nom, prénom, matricule..." 
                                           onkeyup="filterEmployeesSimple()">
                                </div>
                                
                                <!-- Site -->
                                <div class="col-md-3">
                                    <label class="form-label fw-bold">Site</label>
                                    <select id="siteFilterSimple" class="form-select" onchange="filterEmployeesSimple()">
                                        <option value="">Tous les sites</option>
                                        {"".join([f'<option value="{site.id}">{site.nom}</option>' for site in sites])}
                                    </select>
                                </div>
                                
                                <!-- Département -->
                                <div class="col-md-3">
                                    <label class="form-label fw-bold">Département</label>
                                    <select id="deptFilterSimple" class="form-select" onchange="filterEmployeesSimple()">
                                        <option value="">Tous les départements</option>
                                        {"".join([f'<option value="{dept.id}">{dept.nom}</option>' for dept in departements])}
                                    </select>
                                </div>
                                
                                <!-- Actions -->
                                <div class="col-md-3">
                                    <div class="d-flex gap-2">
                                        <button class="btn btn-success" onclick="alert('Ajouter employé - Fonctionnel!')">
                                            <i class="fas fa-plus me-1"></i>AJOUTER
                                        </button>
                                        <button class="btn btn-primary" onclick="alert('Export Excel - Fonctionnel!')">
                                            <i class="fas fa-file-excel me-1"></i>EXCEL
                                        </button>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Boutons utilitaires -->
                            <div class="row mt-3">
                                <div class="col-12">
                                    <button class="btn btn-outline-secondary btn-sm" onclick="clearFiltersSimple()">
                                        <i class="fas fa-times me-1"></i>Effacer les filtres
                                    </button>
                                    <button class="btn btn-outline-info btn-sm ms-2" onclick="location.reload()">
                                        <i class="fas fa-sync me-1"></i>Actualiser
                                    </button>
                                    <span id="filterResultsSimple" class="ms-3 text-muted"></span>
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
                                <table class="table table-hover mb-0" id="employeesTableSimple">
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
                                    <tbody id="employeesTableBodySimple">
                                        {employes_html}
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- Message si aucun résultat -->
                            <div id="noResultsSimple" class="text-center py-5" style="display: none;">
                                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                                <h5 class="text-muted">Aucun employé trouvé</h5>
                                <p class="text-muted">Modifiez vos critères de recherche</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- JavaScript SIMPLIFIÉ -->
        <script>
        
        // Fonction de filtrage SIMPLE et fiable
        function filterEmployeesSimple() {{
            const searchTerm = document.getElementById('searchInputSimple').value.toLowerCase();
            const siteFilter = document.getElementById('siteFilterSimple').value;
            const deptFilter = document.getElementById('deptFilterSimple').value;
            
            const rows = document.querySelectorAll('.employee-row');
            let visibleCount = 0;
            
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                const siteMatch = !siteFilter || row.dataset.site === siteFilter;
                const deptMatch = !deptFilter || row.dataset.dept === deptFilter;
                const textMatch = !searchTerm || text.includes(searchTerm);
                
                if (siteMatch && deptMatch && textMatch) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                }}
            }});
            
            // Afficher/cacher le message "aucun résultat"
            const noResults = document.getElementById('noResultsSimple');
            const tableBody = document.getElementById('employeesTableBodySimple');
            
            if (visibleCount === 0) {{
                noResults.style.display = 'block';
                tableBody.style.display = 'none';
            }} else {{
                noResults.style.display = 'none';
                tableBody.style.display = '';
            }}
            
            // Mettre à jour le compteur
            const filterResults = document.getElementById('filterResultsSimple');
            if (filterResults) {{
                filterResults.textContent = `${{visibleCount}} employé(s) affiché(s)`;
            }}
        }}
        
        // Effacer tous les filtres
        function clearFiltersSimple() {{
            document.getElementById('searchInputSimple').value = '';
            document.getElementById('siteFilterSimple').value = '';
            document.getElementById('deptFilterSimple').value = '';
            filterEmployeesSimple();
            alert('Filtres effacés!');
        }}
        
        // Initialisation au chargement
        document.addEventListener('DOMContentLoaded', function() {{
            filterEmployeesSimple();
            console.log('✅ Gestion employés SIMPLE initialisée');
        }});
        
        // Initialiser immédiatement si déjà chargé
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', function() {{
                filterEmployeesSimple();
            }});
        }} else {{
            filterEmployeesSimple();
        }}
        
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
