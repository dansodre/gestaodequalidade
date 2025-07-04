// Estado global da aplicação
let currentPlan = {
    actions: []
};

let currentSection = 'dashboard';

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    console.log('Aplicação iniciada');
    loadPlans();
    loadUsers();
    loadConfigurations();
});

// Navegação entre seções
function showSection(sectionName) {
    // Esconder todas as seções
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));
    
    // Remover classe active de todos os links de navegação
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => link.classList.remove('active'));
    
    // Mostrar seção selecionada
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Adicionar classe active ao link correspondente
    const activeLink = document.querySelector(`[onclick="showSection('${sectionName}')"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    currentSection = sectionName;
    
    // Carregar dados específicos da seção
    if (sectionName === 'users') {
        loadUsers();
    } else if (sectionName === 'config') {
        loadConfigurations();
    } else if (sectionName === 'dashboard') {
        loadPlans();
    }
}

// Função para logout
function logout() {
    if (confirm('Tem certeza que deseja sair?')) {
        // Limpar dados de sessão
        localStorage.clear();
        sessionStorage.clear();
        
        // Redirecionar para página de login
        window.location.href = '/login.html';
    }
}

// ===== FUNÇÕES DE PLANOS =====

// Função para abrir modal de criar plano
function openCreatePlanModal() {
    const modal = document.getElementById('create-plan-modal');
    if (modal) {
        modal.style.display = 'block';
        // Definir data atual
        const today = new Date().toISOString().split('T')[0];
        const dateInput = document.getElementById('creation-date');
        if (dateInput) {
            dateInput.value = today;
        }
        // Limpar ações
        currentPlan.actions = [];
        updateActionsDisplay();
    }
}

// Função para fechar modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Função para abrir modal de adicionar ação
function openAddActionModal() {
    const modal = document.getElementById('add-action-modal');
    if (modal) {
        modal.style.display = 'block';
        // Limpar formulário
        const form = document.getElementById('add-action-form');
        if (form) {
            form.reset();
        }
    }
}

// Função para adicionar ação ao plano
function addActionToPlan() {
    const title = document.getElementById('action-title').value;
    const responsible = document.getElementById('action-responsible').value;
    const description = document.getElementById('action-description').value;
    const justification = document.getElementById('action-justification').value;
    const email = document.getElementById('action-email').value;
    const cost = document.getElementById('action-cost').value;
    const resource = document.getElementById('action-resource').value;
    const date = document.getElementById('action-date').value;

    // Validação básica
    if (!title || !responsible || !justification || !email || !date) {
        alert('Por favor, preencha todos os campos obrigatórios.');
        return;
    }

    // Criar objeto da ação
    const action = {
        id: Date.now(), // ID temporário
        title: title,
        responsible_person: responsible,
        description: description,
        justification: justification,
        responsible_email: email,
        estimated_cost: parseFloat(cost) || 0,
        resource_source: resource,
        execution_date: date
    };

    // Adicionar à lista de ações do plano atual
    currentPlan.actions.push(action);

    // Atualizar a exibição das ações
    updateActionsDisplay();

    // Fechar modal
    closeModal('add-action-modal');

    // Mostrar mensagem de sucesso
    showToast('Ação adicionada com sucesso!', 'success');
}

// Função para atualizar a exibição das ações
function updateActionsDisplay() {
    const actionsList = document.getElementById('actions-list');
    const actionsCount = document.getElementById('actions-count');
    
    if (actionsCount) {
        actionsCount.textContent = currentPlan.actions.length;
    }

    if (actionsList) {
        if (currentPlan.actions.length === 0) {
            actionsList.innerHTML = '<div class="empty-actions"><p>Nenhuma ação adicionada ainda.</p></div>';
        } else {
            actionsList.innerHTML = currentPlan.actions.map(action => `
                <div class="action-item">
                    <div class="action-header">
                        <h4>${action.title}</h4>
                        <button class="btn-remove" onclick="removeAction(${action.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <div class="action-details">
                        <p><strong>Responsável:</strong> ${action.responsible_person}</p>
                        <p><strong>E-mail:</strong> ${action.responsible_email}</p>
                        <p><strong>Data de Execução:</strong> ${formatDate(action.execution_date)}</p>
                        <p><strong>Custo:</strong> R$ ${action.estimated_cost.toFixed(2)}</p>
                        ${action.description ? `<p><strong>Descrição:</strong> ${action.description}</p>` : ''}
                        <p><strong>Justificativa:</strong> ${action.justification}</p>
                    </div>
                </div>
            `).join('');
        }
    }
}

// Função para remover ação
function removeAction(actionId) {
    currentPlan.actions = currentPlan.actions.filter(action => action.id !== actionId);
    updateActionsDisplay();
    showToast('Ação removida com sucesso!', 'success');
}

// Função para salvar plano
async function savePlan() {
    const planName = document.getElementById('plan-name').value;
    const sector = document.getElementById('responsible-sector').value;
    const responsiblePerson = document.getElementById('responsible-person').value;
    const responsibleEmail = document.getElementById('responsible-email').value;
    const creationDate = document.getElementById('creation-date').value;

    // Validação básica
    if (!planName || !sector || !responsiblePerson || !responsibleEmail || !creationDate) {
        alert('Por favor, preencha todos os campos obrigatórios do plano.');
        return;
    }

    if (currentPlan.actions.length === 0) {
        alert('Por favor, adicione pelo menos uma ação ao plano.');
        return;
    }

    // Criar objeto do plano
    const planData = {
        name: planName,
        sector: sector,
        responsible_person: responsiblePerson,
        responsible_email: responsibleEmail,
        creation_date: creationDate
    };

    try {
        // Salvar plano
        const planResponse = await fetch('/api/plans', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(planData),
            credentials: 'include'
        });

        if (!planResponse.ok) {
            throw new Error('Erro ao criar plano');
        }

        const planResult = await planResponse.json();
        const planId = planResult.plan.id;

        // Salvar ações
        for (const action of currentPlan.actions) {
            const actionResponse = await fetch(`/api/plans/${planId}/actions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(action),
                credentials: 'include'
            });

            if (!actionResponse.ok) {
                console.error('Erro ao criar ação:', action.title);
            }
        }

        // Limpar estado
        currentPlan.actions = [];
        
        // Fechar modal
        closeModal('create-plan-modal');
        
        // Recarregar lista de planos
        loadPlans();
        
        // Mostrar mensagem de sucesso
        showToast('Plano de ação criado com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao salvar plano:', error);
        showToast('Erro ao salvar plano. Tente novamente.', 'error');
    }
}

// Função para carregar planos
async function loadPlans() {
    try {
        const response = await fetch('/api/plans', {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao carregar planos');
        }

        const data = await response.json();
        updatePlansTable(data.plans);
        updateStats(data.plans);

    } catch (error) {
        console.error('Erro ao carregar planos:', error);
        showToast('Erro ao carregar planos', 'error');
    }
}

// Função para atualizar tabela de planos
function updatePlansTable(plans) {
    const tableBody = document.getElementById('plans-table-body');
    const emptyState = document.getElementById('empty-state');

    if (!tableBody) return;

    if (plans.length === 0) {
        tableBody.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
    } else {
        if (emptyState) emptyState.style.display = 'none';
        tableBody.innerHTML = plans.map(plan => `
            <tr>
                <td>${plan.name}</td>
                <td>${plan.sector}</td>
                <td>${plan.responsible_person}</td>
                <td>${formatDate(plan.creation_date)}</td>
                <td><span class="status-badge status-${plan.status}">${getStatusText(plan.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="viewPlan(${plan.id})">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="editPlan(${plan.id})">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                </td>
            </tr>
        `).join('');
    }
}

// Função para atualizar estatísticas
function updateStats(plans) {
    const totalPlans = document.getElementById('total-plans');
    const pendingPlans = document.getElementById('pending-plans');
    const completedPlans = document.getElementById('completed-plans');

    if (totalPlans) totalPlans.textContent = plans.length;
    if (pendingPlans) pendingPlans.textContent = plans.filter(p => p.status === 'pending').length;
    if (completedPlans) completedPlans.textContent = plans.filter(p => p.status === 'completed').length;
}

// ===== FUNÇÕES DE USUÁRIOS =====

// Função para abrir modal de criar usuário
function openCreateUserModal() {
    const modal = document.getElementById('create-user-modal');
    if (modal) {
        modal.style.display = 'block';
        // Limpar formulário
        const form = document.getElementById('create-user-form');
        if (form) {
            form.reset();
        }
    }
}

// Função para criar usuário
async function createUser() {
    const username = document.getElementById('user-username').value;
    const email = document.getElementById('user-email').value;
    const password = document.getElementById('user-password').value;
    const role = document.getElementById('user-role').value;

    // Validação básica
    if (!username || !email || !password || !role) {
        alert('Por favor, preencha todos os campos obrigatórios.');
        return;
    }

    const userData = {
        username: username,
        email: email,
        password: password,
        role: role
    };

    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao criar usuário');
        }

        // Fechar modal
        closeModal('create-user-modal');
        
        // Recarregar lista de usuários
        loadUsers();
        
        // Mostrar mensagem de sucesso
        showToast('Usuário criado com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao criar usuário:', error);
        showToast('Erro ao criar usuário. Tente novamente.', 'error');
    }
}

// Função para carregar usuários
async function loadUsers() {
    try {
        const response = await fetch('/api/users', {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao carregar usuários');
        }

        const data = await response.json();
        updateUsersTable(data.users);
        updateUsersStats(data.users);

    } catch (error) {
        console.error('Erro ao carregar usuários:', error);
        showToast('Erro ao carregar usuários', 'error');
    }
}

// Função para atualizar tabela de usuários
function updateUsersTable(users) {
    const tableBody = document.getElementById('users-table-body');
    if (!tableBody) return;

    if (users.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="6" class="text-center">Nenhum usuário encontrado</td></tr>';
    } else {
        tableBody.innerHTML = users.map(user => `
            <tr>
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td><span class="role-badge role-${user.role}">${getRoleText(user.role)}</span></td>
                <td><span class="status-badge status-${user.is_active ? 'active' : 'inactive'}">${user.is_active ? 'Ativo' : 'Inativo'}</span></td>
                <td>${user.last_login ? formatDate(user.last_login) : 'Nunca'}</td>
                <td>
                    <button class="btn btn-sm btn-outline" onclick="editUser(${user.id})">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteUser(${user.id})">
                        <i class="fas fa-trash"></i> Excluir
                    </button>
                </td>
            </tr>
        `).join('');
    }
}

// Função para atualizar estatísticas de usuários
function updateUsersStats(users) {
    const totalUsers = document.getElementById('total-users');
    const adminUsers = document.getElementById('admin-users');
    const activeUsers = document.getElementById('active-users');

    if (totalUsers) totalUsers.textContent = users.length;
    if (adminUsers) adminUsers.textContent = users.filter(u => u.role === 'admin').length;
    if (activeUsers) activeUsers.textContent = users.filter(u => u.is_active).length;
}

// Função para editar usuário
function editUser(userId) {
    // Implementar edição de usuário
    console.log('Editar usuário:', userId);
    showToast('Funcionalidade de edição em desenvolvimento', 'info');
}

// Função para excluir usuário
async function deleteUser(userId) {
    if (!confirm('Tem certeza que deseja excluir este usuário?')) {
        return;
    }

    try {
        const response = await fetch(`/api/users/${userId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao excluir usuário');
        }

        // Recarregar lista de usuários
        loadUsers();
        
        // Mostrar mensagem de sucesso
        showToast('Usuário excluído com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao excluir usuário:', error);
        showToast('Erro ao excluir usuário. Tente novamente.', 'error');
    }
}

// Função para atualizar usuários
function refreshUsers() {
    loadUsers();
    showToast('Lista de usuários atualizada!', 'success');
}

// ===== FUNÇÕES DE CONFIGURAÇÕES =====

// Função para mostrar aba de configuração
function showConfigTab(tabName) {
    // Esconder todas as abas
    const tabs = document.querySelectorAll('.config-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remover classe active de todos os botões
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => btn.classList.remove('active'));
    
    // Mostrar aba selecionada
    const targetTab = document.getElementById(tabName + '-config');
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    // Adicionar classe active ao botão correspondente
    const activeBtn = document.querySelector(`[onclick="showConfigTab('${tabName}')"]`);
    if (activeBtn) {
        activeBtn.classList.add('active');
    }
}

// Função para carregar configurações
async function loadConfigurations() {
    try {
        const response = await fetch('/api/config', {
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao carregar configurações');
        }

        const config = await response.json();
        populateConfigFields(config);

    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        showToast('Erro ao carregar configurações', 'error');
    }
}

// Função para popular campos de configuração
function populateConfigFields(config) {
    // Configurações de email
    if (config.email) {
        document.getElementById('smtp-server').value = config.email.smtp_server || '';
        document.getElementById('smtp-port').value = config.email.smtp_port || '';
        document.getElementById('smtp-username').value = config.email.smtp_username || '';
        document.getElementById('smtp-password').value = config.email.smtp_password || '';
        document.getElementById('email-from').value = config.email.email_from || '';
    }

    // Configurações do sistema
    if (config.system) {
        document.getElementById('system-name').value = config.system.system_name || '';
        document.getElementById('company-name').value = config.system.company_name || '';
        document.getElementById('timezone').value = config.system.timezone || '';
        document.getElementById('language').value = config.system.language || '';
        document.getElementById('maintenance-mode').checked = config.system.maintenance_mode || false;
    }

    // Configurações do banco de dados
    if (config.database) {
        document.getElementById('db-type').value = config.database.db_type || '';
        document.getElementById('supabase-url').value = config.database.supabase_url || '';
        document.getElementById('supabase-key').value = config.database.supabase_key || '';
        document.getElementById('supabase-service-key').value = config.database.supabase_service_key || '';
    }

    // Configurações de segurança
    if (config.security) {
        document.getElementById('session-timeout').value = config.security.session_timeout || '';
        document.getElementById('require-uppercase').checked = config.security.require_uppercase || false;
        document.getElementById('require-numbers').checked = config.security.require_numbers || false;
        document.getElementById('require-special').checked = config.security.require_special || false;
        document.getElementById('min-password-length').value = config.security.min_password_length || '';
    }
}

// Função para salvar configurações de email
async function saveEmailConfig() {
    const emailConfig = {
        smtp_server: document.getElementById('smtp-server').value,
        smtp_port: parseInt(document.getElementById('smtp-port').value),
        smtp_username: document.getElementById('smtp-username').value,
        smtp_password: document.getElementById('smtp-password').value,
        email_from: document.getElementById('email-from').value
    };

    try {
        const response = await fetch('/api/config/email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emailConfig),
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao salvar configurações de email');
        }

        showToast('Configurações de email salvas com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao salvar configurações de email:', error);
        showToast('Erro ao salvar configurações de email', 'error');
    }
}

// Função para testar configurações de email
async function testEmailConfig() {
    try {
        const response = await fetch('/api/config/email/test', {
            method: 'POST',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao testar configurações de email');
        }

        showToast('Email de teste enviado com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao testar email:', error);
        showToast('Erro ao testar configurações de email', 'error');
    }
}

// Função para salvar configurações do sistema
async function saveSystemConfig() {
    const systemConfig = {
        system_name: document.getElementById('system-name').value,
        company_name: document.getElementById('company-name').value,
        timezone: document.getElementById('timezone').value,
        language: document.getElementById('language').value,
        maintenance_mode: document.getElementById('maintenance-mode').checked
    };

    try {
        const response = await fetch('/api/config/system', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(systemConfig),
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao salvar configurações do sistema');
        }

        showToast('Configurações do sistema salvas com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao salvar configurações do sistema:', error);
        showToast('Erro ao salvar configurações do sistema', 'error');
    }
}

// Função para salvar configurações do banco de dados
async function saveDatabaseConfig() {
    const databaseConfig = {
        db_type: document.getElementById('db-type').value,
        supabase_url: document.getElementById('supabase-url').value,
        supabase_key: document.getElementById('supabase-key').value,
        supabase_service_key: document.getElementById('supabase-service-key').value
    };

    try {
        const response = await fetch('/api/config/database', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(databaseConfig),
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao salvar configurações do banco de dados');
        }

        showToast('Configurações do banco de dados salvas com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao salvar configurações do banco de dados:', error);
        showToast('Erro ao salvar configurações do banco de dados', 'error');
    }
}

// Função para testar conexão com banco de dados
async function testDatabaseConnection() {
    try {
        const response = await fetch('/api/config/database/test', {
            method: 'POST',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao testar conexão com banco de dados');
        }

        showToast('Conexão com banco de dados testada com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao testar conexão:', error);
        showToast('Erro ao testar conexão com banco de dados', 'error');
    }
}

// Função para salvar configurações de segurança
async function saveSecurityConfig() {
    const securityConfig = {
        session_timeout: parseInt(document.getElementById('session-timeout').value),
        require_uppercase: document.getElementById('require-uppercase').checked,
        require_numbers: document.getElementById('require-numbers').checked,
        require_special: document.getElementById('require-special').checked,
        min_password_length: parseInt(document.getElementById('min-password-length').value)
    };

    try {
        const response = await fetch('/api/config/security', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(securityConfig),
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Erro ao salvar configurações de segurança');
        }

        showToast('Configurações de segurança salvas com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao salvar configurações de segurança:', error);
        showToast('Erro ao salvar configurações de segurança', 'error');
    }
}

// Função para salvar todas as configurações
async function saveAllConfigurations() {
    await saveEmailConfig();
    await saveSystemConfig();
    await saveDatabaseConfig();
    await saveSecurityConfig();
    
    showToast('Todas as configurações foram salvas!', 'success');
}

// ===== FUNÇÕES AUXILIARES =====

// Função para mostrar toast
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.querySelector('.toast-message');
    const toastIcon = document.querySelector('.toast-icon');

    if (toast && toastMessage && toastIcon) {
        toastMessage.textContent = message;
        
        // Definir ícone baseado no tipo
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };
        
        toastIcon.className = `toast-icon ${icons[type] || icons.info}`;
        toast.className = `toast toast-${type}`;
        toast.style.display = 'block';

        // Auto-hide após 3 segundos
        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }
}

// Funções auxiliares
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'Pendente',
        'in-progress': 'Em Andamento',
        'completed': 'Concluído'
    };
    return statusMap[status] || status;
}

function getRoleText(role) {
    const roleMap = {
        'admin': 'Administrador',
        'user': 'Usuário'
    };
    return roleMap[role] || role;
}

function refreshPlans() {
    loadPlans();
    showToast('Lista de planos atualizada!', 'success');
}

function viewPlan(planId) {
    // Implementar visualização do plano
    console.log('Ver plano:', planId);
    showToast('Funcionalidade de visualização em desenvolvimento', 'info');
}

function editPlan(planId) {
    // Implementar edição do plano
    console.log('Editar plano:', planId);
    showToast('Funcionalidade de edição em desenvolvimento', 'info');
}

// Funções para relatórios
function openGeneralReportModal() {
    const modal = document.getElementById('general-report-modal');
    if (modal) {
        modal.style.display = 'block';
        // Atualizar dados do relatório
        loadPlans().then(() => {
            // Dados serão atualizados automaticamente
        });
    }
}

function openDetailedReportModal() {
    const modal = document.getElementById('detailed-report-modal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function generateDetailedReport() {
    showToast('Funcionalidade de relatório detalhado em desenvolvimento', 'info');
}

function exportToPDF() {
    showToast('Funcionalidade de exportação PDF em desenvolvimento', 'info');
}

function exportToExcel() {
    showToast('Funcionalidade de exportação Excel em desenvolvimento', 'info');
}

// Event listeners para fechar modais clicando fora
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});

// Event listeners para botões de fechar
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('close-btn') || event.target.closest('.close-btn')) {
        const modal = event.target.closest('.modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
});

console.log('Script carregado com sucesso');

