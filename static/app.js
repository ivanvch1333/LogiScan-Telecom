/* ==========================================
   LogiScan Telecom - Application Logic
   Single Page Application Controller
   ========================================== */

// ==========================================
// GLOBAL STATE
// ==========================================
const APP = {
    token: localStorage.getItem('teletrack_token'),
    user: JSON.parse(localStorage.getItem('teletrack_user') || 'null'),
    config: { nombre_empresa: 'LogiScan Telecom', logo_url: null, banner_url: null },
    equipos: [],
    usuarios: [],
    logs: []
};

const LOG_BADGE = {
    INFO: 'badge-operativo',
    WARNING: 'badge-mantenimiento',
    CRITICAL: 'badge-emergencia'
};

// ==========================================
// ENUM LABELS (display-friendly)
// ==========================================
const LABELS = {
    categoria: {
        router: 'Router', switch: 'Switch', olt: 'OLT', edfa: 'EDFA',
        enlace_radio: 'Enlace Radio', otro: 'Otro'
    },
    estado: {
        disponible: 'Disponible', asignado: 'Asignado',
        en_mantenimiento: 'En Mantenimiento', baja: 'De Baja'
    },
    ubicacion: {
        '1000': '1000', '2000': '2000', '1010': '1010',
        'Almacén Central': 'Almacén Central'
    },
    movimiento: {
        ingreso_almacen: 'Ingreso Almacén', instalacion_nodo: 'Instalación Nodo',
        retiro_mantenimiento: 'Retiro Mantenimiento', reemplazo_emergencia: 'Reemplazo Emergencia'
    },
    rol: { admin: 'Administrador', tecnico: 'Técnico / Bodeguero' }
};

const ESTADO_BADGE = {
    disponible: 'badge-operativo', 
    asignado: 'badge-admin', // Azul
    en_mantenimiento: 'badge-mantenimiento', // Naranja
    baja: 'badge-baja' // Gris
};

const UBICACIONES = ['1000', '2000', '1010', 'Almacén Central'];
const CATEGORIAS = ['router', 'switch', 'olt', 'edfa', 'enlace_radio', 'otro'];
const ESTADOS = ['disponible', 'asignado', 'en_mantenimiento', 'baja'];

// ==========================================
// API HELPER
// ==========================================
async function api(method, path, body = null, isFormData = false) {
    const headers = {};
    if (APP.token) headers['Authorization'] = `Bearer ${APP.token}`;
    if (!isFormData && body) headers['Content-Type'] = 'application/json';

    const opts = { method, headers };
    if (body) opts.body = isFormData ? body : JSON.stringify(body);

    try {
        const res = await fetch(path, opts);
        if (res.status === 401) {
            logout();
            return null;
        }
        if (res.status === 204) return null;
        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || 'Error en la solicitud');
        }
        return data;
    } catch (err) {
        if (err.message !== 'Failed to fetch') showToast(err.message, 'error');
        throw err;
    }
}

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span>${type === 'success' ? '✓' : '✕'}</span>
        <span>${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ==========================================
// DATE FORMATTER
// ==========================================
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    const months = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
    const day = d.getDate();
    const month = months[d.getMonth()];
    const year = d.getFullYear();
    const h = String(d.getHours()).padStart(2, '0');
    const m = String(d.getMinutes()).padStart(2, '0');
    return `${day} ${month} ${year}, ${h}:${m}`;
}

// ==========================================
// NAVIGATION
// ==========================================
function navigateTo(section) {
    // Hide scanner if open
    stopCameraScanner();

    // Hide all view sections
    document.querySelectorAll('.view-section').forEach(el => {
        el.classList.remove('active');
    });
    // Show target
    const target = document.getElementById(`view-${section}`);
    if (target) target.classList.add('active');

    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const navItem = document.querySelector(`.nav-item[data-section="${section}"]`);
    if (navItem) navItem.classList.add('active');

    // Close mobile sidebar
    document.querySelector('.sidebar')?.classList.remove('open');
    document.querySelector('.sidebar-overlay')?.classList.remove('show');

    // Load section data
    switch (section) {
        case 'dashboard': loadDashboard(); break;
        case 'equipos': loadEquipos(); break;
        case 'movimientos': loadMovimientos(); break;
        case 'busqueda-qr': loadBusquedaQR(); break;
        case 'usuarios': loadUsuarios(); break;
        case 'logs': loadLogs(); break;
        case 'ajustes': loadAjustes(); break;
    }
}

// ==========================================
// LOGIN FLOW
// ==========================================
function showLogin() {
    document.getElementById('login-page').classList.remove('hidden');
    document.getElementById('app-layout').classList.add('hidden');
    loadConfig().then(() => updateLoginBranding());
}

function updateLoginBranding() {
    const logoEl = document.getElementById('login-logo-img');
    const titleEl = document.getElementById('login-company-name');
    if (APP.config.logo_url) {
        logoEl.src = APP.config.logo_url;
        logoEl.style.display = 'block';
    } else {
        logoEl.style.display = 'none';
    }
    titleEl.textContent = APP.config.nombre_empresa;
}

function initLoginForm() {
    const form = document.getElementById('login-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errorEl = document.getElementById('login-error');
        errorEl.classList.add('hidden');
        errorEl.classList.remove('show', 'block');

        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;

        if (!username || !password) {
            errorEl.innerHTML = '<div class="flex items-center gap-2"><span>⚠️</span><span>Ingrese su usuario y contraseña</span></div>';
            errorEl.classList.remove('hidden');
            errorEl.classList.add('block');
            return;
        }

        try {
            const tokenData = await api('POST', '/api/usuarios/login', { username, password });
            if (!tokenData) return;
            APP.token = tokenData.access_token;
            localStorage.setItem('teletrack_token', APP.token);

            const user = await api('GET', '/api/usuarios/me');
            if (!user) return;
            APP.user = user;
            localStorage.setItem('teletrack_user', JSON.stringify(user));

            initApp();
        } catch (err) {
            const msg = err.message || 'Error al iniciar sesión';
            errorEl.innerHTML = `<div class="flex items-start gap-2 text-left">
                <span class="text-base leading-none mt-0.5">🚨</span>
                <div class="flex-1">${msg}</div>
            </div>`;
            errorEl.classList.remove('hidden');
            errorEl.classList.add('block');
        }
    });
}

// ==========================================
// APP INITIALIZATION
// ==========================================
async function initApp() {
    document.getElementById('login-page').classList.add('hidden');
    document.getElementById('app-layout').classList.remove('hidden');

    await loadConfig();
    updateAppBranding();
    buildSidebar();
    navigateTo('dashboard');

    // Dynamic field logic for client details in movements
    document.getElementById('mov-tipo').addEventListener('change', function() {
        const fields = document.getElementById('mov-cliente-fields');
        const nameInput = document.getElementById('mov-cliente-nombre');
        const addrInput = document.getElementById('mov-cliente-direccion');
        
        if (this.value === 'instalacion_nodo') {
            fields.style.display = 'grid';
            nameInput.required = true;
            addrInput.required = true;
        } else {
            fields.style.display = 'none';
            nameInput.required = false;
            addrInput.required = false;
        }
    });
}

async function loadConfig() {
    try {
        APP.config = await api('GET', '/api/config') || APP.config;
    } catch (e) {
        // Use defaults
    }
}

function updateAppBranding() {
    // Sidebar logo
    const sidebarLogo = document.getElementById('sidebar-logo-img');
    const sidebarText = document.getElementById('sidebar-logo-text');
    if (APP.config.logo_url) {
        sidebarLogo.src = APP.config.logo_url;
        sidebarLogo.style.display = 'block';
    } else {
        sidebarLogo.style.display = 'none';
    }
    sidebarText.textContent = APP.config.nombre_empresa;

    // Top bar
    document.getElementById('top-bar-company').textContent = APP.config.nombre_empresa;
    document.getElementById('top-bar-user').textContent = APP.user?.nombre_completo || '';

    // User info in sidebar
    const avatar = document.getElementById('sidebar-avatar');
    avatar.textContent = (APP.user?.nombre_completo || 'U').charAt(0).toUpperCase();
    document.getElementById('sidebar-user-name').textContent = APP.user?.nombre_completo || '';
    document.getElementById('sidebar-user-role').textContent = LABELS.rol[APP.user?.rol] || '';

    // Banner
    const bannerArea = document.getElementById('banner-area');
    const bannerImg = document.getElementById('banner-img');
    if (APP.config.banner_url) {
        bannerImg.src = APP.config.banner_url;
        bannerArea.classList.remove('hidden');
    } else {
        bannerArea.classList.add('hidden');
    }
}

function buildSidebar() {
    const nav = document.getElementById('sidebar-nav');
    const isAdmin = APP.user?.rol === 'admin';

    let html = `
        <div class="nav-section-label">Principal</div>
        <div class="nav-item active" data-section="dashboard" onclick="navigateTo('dashboard')">
            <span class="nav-icon">📊</span> Dashboard
        </div>
        <div class="nav-item" data-section="equipos" onclick="navigateTo('equipos')">
            <span class="nav-icon">📡</span> Equipos
        </div>
        <div class="nav-item" data-section="movimientos" onclick="navigateTo('movimientos')">
            <span class="nav-icon">🔄</span> Movimientos
        </div>
        <div class="nav-item" data-section="busqueda-qr" onclick="navigateTo('busqueda-qr')">
            <span class="nav-icon">🔍</span> Lector QR / Cámara
        </div>
    `;

    if (isAdmin) {
        html += `
            <div class="nav-section-label">Administración</div>
            <div class="nav-item" data-section="usuarios" onclick="navigateTo('usuarios')">
                <span class="nav-icon">👥</span> Usuarios
            </div>
            <div class="nav-item" data-section="logs" onclick="navigateTo('logs')">
                <span class="nav-icon">📜</span> Logs del Sistema
            </div>
            <div class="nav-item" data-section="ajustes" onclick="navigateTo('ajustes')">
                <span class="nav-icon">⚙️</span> Ajustes
            </div>
        `;
    }

    nav.innerHTML = html;
}

// ==========================================
// LOGOUT
// ==========================================
function logout() {
    APP.token = null;
    APP.user = null;
    localStorage.removeItem('teletrack_token');
    localStorage.removeItem('teletrack_user');
    showLogin();
}

// ==========================================
// DASHBOARD
// ==========================================
async function loadDashboard() {
    try {
        APP.equipos = await api('GET', '/api/equipos') || [];
    } catch { APP.equipos = []; }

    const total = APP.equipos.length;
    const disponibles = APP.equipos.filter(e => e.estado === 'disponible').length;
    const asignados = APP.equipos.filter(e => e.estado === 'asignado').length;
    const mantenimiento = APP.equipos.filter(e => e.estado === 'en_mantenimiento').length;
    const bajas = APP.equipos.filter(e => e.estado === 'baja').length;

    document.getElementById('stat-total').textContent = total;
    document.getElementById('stat-disponibles').textContent = disponibles;
    document.getElementById('stat-asignados').textContent = asignados;
    document.getElementById('stat-mantenimiento').textContent = mantenimiento;
    document.getElementById('stat-bajas').textContent = bajas;

    // Category distribution
    renderCategoryChart();
    // Location distribution
    renderLocationChart();
    // Recent equipment
    renderRecentEquipos();
}

function renderCategoryChart() {
    const container = document.getElementById('chart-categorias');
    const counts = {};
    CATEGORIAS.forEach(c => counts[c] = 0);
    APP.equipos.forEach(e => { if (counts[e.categoria] !== undefined) counts[e.categoria]++; });
    const max = Math.max(...Object.values(counts), 1);

    let html = '';
    CATEGORIAS.forEach(cat => {
        const pct = (counts[cat] / max) * 100;
        html += `
            <div class="bar-item">
                <span class="bar-label">${LABELS.categoria[cat]}</span>
                <div class="bar-track">
                    <div class="bar-fill cat-${cat}" style="width:${pct}%">${counts[cat]}</div>
                </div>
            </div>`;
    });
    container.innerHTML = html;
}

function renderLocationChart() {
    const container = document.getElementById('chart-ubicaciones');
    const counts = {};
    UBICACIONES.forEach(u => counts[u] = 0);
    APP.equipos.forEach(e => { if (counts[e.ubicacion_actual] !== undefined) counts[e.ubicacion_actual]++; });
    const max = Math.max(...Object.values(counts), 1);

    let html = '';
    UBICACIONES.forEach(loc => {
        const pct = (counts[loc] / max) * 100;
        html += `
            <div class="bar-item">
                <span class="bar-label">${loc}</span>
                <div class="bar-track">
                    <div class="bar-fill loc-default" style="width:${pct}%">${counts[loc]}</div>
                </div>
            </div>`;
    });
    container.innerHTML = html;
}

function renderRecentEquipos() {
    const container = document.getElementById('recent-equipos');
    const recent = [...APP.equipos].sort((a, b) => new Date(b.fecha_registro) - new Date(a.fecha_registro)).slice(0, 5);

    if (recent.length === 0) {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📡</div><div class="empty-state-title">Sin registros</div><div class="empty-state-text">Registre su primer material en la sección Equipos</div></div>';
        return;
    }

    let html = `<table class="data-table"><thead><tr><th>Material</th><th>Asset Tag</th><th>Serie</th><th>Qty SAP</th><th>Qty EAIM</th><th>Desviación</th><th>Cliente / Instalado</th><th>Estado</th></tr></thead><tbody>`;
    recent.forEach(e => {
        const dev = e.qty_sap - e.qty_eaim;
        const clienteInfo = e.cliente_nombre ? `<strong>${e.cliente_nombre}</strong><br><span style="font-size:0.75rem;color:var(--text-muted);">${e.cliente_direccion}</span>` : '—';
        html += `<tr>
            <td><strong>${e.material}</strong><br><span style="font-size:0.75rem;color:var(--text-secondary);">${e.nombre}</span></td>
            <td><code>${e.asset_tag}</code></td>
            <td><code>${e.numero_serie}</code></td>
            <td>${e.qty_sap}</td>
            <td>${e.qty_eaim}</td>
            <td style="font-weight:700;color:${dev !== 0 ? 'var(--color-mantenimiento)' : 'var(--color-operativo)'}">${dev}</td>
            <td>${clienteInfo}</td>
            <td><span class="badge ${ESTADO_BADGE[e.estado]}">${LABELS.estado[e.estado]}</span></td>
        </tr>`;
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

// ==========================================
// EQUIPOS SECTION
// ==========================================
async function loadEquipos() {
    try {
        APP.equipos = await api('GET', '/api/equipos') || [];
    } catch { APP.equipos = []; }
    renderEquiposTable(APP.equipos);
}

function filterEquipos() {
    const search = document.getElementById('filter-search').value.toLowerCase();
    const planta = document.getElementById('filter-planta').value.toLowerCase();
    const sloc = document.getElementById('filter-sloc').value;
    const est = document.getElementById('filter-estado').value;
    const mes = document.getElementById('filter-mes').value;
    const anio = document.getElementById('filter-anio').value;

    let filtered = APP.equipos;
    if (sloc) filtered = filtered.filter(e => e.ubicacion_actual === sloc);
    if (est) filtered = filtered.filter(e => e.estado === est);
    if (planta) filtered = filtered.filter(e => e.plant.toLowerCase().includes(planta));
    if (search) filtered = filtered.filter(e =>
        e.nombre.toLowerCase().includes(search) ||
        e.numero_serie.toLowerCase().includes(search) ||
        e.material.toLowerCase().includes(search) ||
        e.asset_tag.toLowerCase().includes(search) ||
        e.marca.toLowerCase().includes(search) ||
        e.modelo.toLowerCase().includes(search) ||
        (e.cliente_nombre && e.cliente_nombre.toLowerCase().includes(search))
    );
    if (mes) {
        filtered = filtered.filter(e => {
            const d = new Date(e.fecha_registro);
            return (d.getMonth() + 1) === parseInt(mes);
        });
    }
    if (anio) {
        filtered = filtered.filter(e => {
            const d = new Date(e.fecha_registro);
            return d.getFullYear() === parseInt(anio);
        });
    }
    renderEquiposTable(filtered);
}

function renderEquiposTable(equipos) {
    const container = document.getElementById('equipos-table-body');
    if (equipos.length === 0) {
        container.innerHTML = '<tr><td colspan="11"><div class="empty-state"><div class="empty-state-icon">📦</div><div class="empty-state-title">No se encontraron registros</div></div></td></tr>';
        return;
    }

    container.innerHTML = equipos.map(e => {
        const dev = e.qty_sap - e.qty_eaim;
        const slocDisplay = LABELS.ubicacion[e.ubicacion_actual] || e.ubicacion_actual;
        return `
        <tr>
            <td><code>${e.material}</code></td>
            <td>
                <strong>${e.nombre}</strong><br>
                <span style="font-size:0.75rem;color:var(--text-secondary);">${e.marca} ${e.modelo}</span>
                ${e.cliente_nombre ? `<br><span style="font-size:0.75rem;color:var(--accent-primary);font-weight:600;">👤 ${e.cliente_nombre}</span>` : ''}
            </td>
            <td>${e.plant}</td>
            <td>${slocDisplay}</td>
            <td><code>${e.asset_tag}</code></td>
            <td><code>${e.numero_serie}</code></td>
            <td>${e.qty_sap}</td>
            <td>${e.qty_eaim}</td>
            <td style="font-weight:700;color:${dev !== 0 ? 'var(--color-emergencia)' : 'var(--color-operativo)'}">${dev}</td>
            <td><span class="badge ${ESTADO_BADGE[e.estado]}">${LABELS.estado[e.estado]}</span></td>
            <td>
                <div class="table-actions">
                    <button class="btn btn-icon btn-sm" onclick="showEquipoDetail(${e.id})" title="Ver detalle">📋</button>
                    <button class="btn btn-icon btn-sm" onclick="showQRModal(${e.id}, '${e.nombre}')" title="Ver QR">📱</button>
                </div>
            </td>
        </tr>
    `;
    }).join('');
}

// ==========================================
// EQUIPO DETAIL MODAL
// ==========================================
async function showEquipoDetail(id) {
    const equipo = APP.equipos.find(e => e.id === id);
    if (!equipo) return;

    let historial = [];
    try {
        historial = await api('GET', `/api/movimientos/equipo/${id}`) || [];
    } catch {}

    const dev = equipo.qty_sap - equipo.qty_eaim;
    const body = document.getElementById('detail-modal-body');
    body.innerHTML = `
        <div class="detail-grid">
            <div class="detail-item"><label>Descripción</label><span>${equipo.nombre}</span></div>
            <div class="detail-item"><label>Material SAP</label><span><code>${equipo.material}</code></span></div>
            <div class="detail-item"><label>Nº Serie</label><span><code>${equipo.numero_serie}</code></span></div>
            <div class="detail-item"><label>Asset Tag (Placa)</label><span><code>${equipo.asset_tag}</code></span></div>
            <div class="detail-item"><label>Plant (Planta)</label><span>${equipo.plant}</span></div>
            <div class="detail-item"><label>SLOC (Ubicación)</label><span>${LABELS.ubicacion[equipo.ubicacion_actual] || equipo.ubicacion_actual}</span></div>
            <div class="detail-item"><label>Cantidad SAP</label><span>${equipo.qty_sap}</span></div>
            <div class="detail-item"><label>Cantidad EAIM (Real)</label><span>${equipo.qty_eaim}</span></div>
            <div class="detail-item"><label>Desviación</label><span style="font-weight:700;color:${dev !== 0 ? 'var(--color-emergencia)' : 'var(--color-operativo)'}">${dev}</span></div>
            <div class="detail-item"><label>Estado</label><span class="badge ${ESTADO_BADGE[equipo.estado]}">${LABELS.estado[equipo.estado]}</span></div>
            <div class="detail-item"><label>Cliente Asignado</label><span>${equipo.cliente_nombre || '—'}</span></div>
            <div class="detail-item"><label>Dirección Instalación</label><span>${equipo.cliente_direccion || '—'}</span></div>
            <div class="detail-item"><label>Marca / Modelo</label><span>${equipo.marca} / ${equipo.modelo}</span></div>
            <div class="detail-item"><label>Fecha Registro</label><span>${formatDate(equipo.fecha_registro)}</span></div>
        </div>
        <div class="qr-container">
            <img src="/api/equipos/${equipo.id}/qr" alt="Código QR">
            <a class="btn btn-secondary btn-sm" href="/api/equipos/${equipo.id}/qr" download="QR_${equipo.numero_serie}.png">⬇ Descargar QR</a>
        </div>
        <h3 style="font-size:1rem;font-weight:600;margin:var(--space-lg) 0 var(--space-md);color:var(--text-primary);">Historial de Movimientos y Novedades</h3>
        ${historial.length === 0
            ? '<div class="empty-state"><div class="empty-state-text">Sin movimientos registrados</div></div>'
            : `<div class="timeline">${historial.map(h => `
                <div class="timeline-item">
                    <div class="timeline-date">${formatDate(h.fecha_movimiento)}</div>
                    <div class="timeline-content">
                        <div class="timeline-type">${LABELS.movimiento[h.tipo_movimiento] || h.tipo_movimiento}</div>
                        <div class="timeline-detail">
                            ${h.ubicacion_origen ? `${LABELS.ubicacion[h.ubicacion_origen] || h.ubicacion_origen} → ` : ''}${LABELS.ubicacion[h.ubicacion_destino] || h.ubicacion_destino}
                            ${h.cliente_nombre ? `<br><strong>Instalado en:</strong> ${h.cliente_nombre} (${h.cliente_direccion})` : ''}
                            ${h.observaciones ? `<br><strong style="color:var(--color-mantenimiento);">Novedad:</strong> <em>${h.observaciones}</em>` : ''}
                        </div>
                    </div>
                </div>`).join('')}</div>`
        }
    `;

    document.getElementById('detail-modal-title').textContent = equipo.nombre;
    openModal('detail-modal');
}

// ==========================================
// QR MODAL
// ==========================================
function showQRModal(id, nombre) {
    document.getElementById('qr-modal-title').textContent = `QR - ${nombre}`;
    document.getElementById('qr-modal-body').innerHTML = `
        <div class="qr-container">
            <img src="/api/equipos/${id}/qr" alt="Código QR ${nombre}">
            <a class="btn btn-primary" href="/api/equipos/${id}/qr" download="QR_${nombre}.png">⬇ Descargar QR</a>
        </div>
    `;
    openModal('qr-modal');
}

// ==========================================
// NEW EQUIPO MODAL
// ==========================================
function showNewEquipoModal() {
    document.getElementById('new-equipo-form').reset();
    openModal('new-equipo-modal');
}

async function submitNewEquipo(e) {
    e.preventDefault();
    const form = e.target;
    const body = {
        nombre: form.nombre.value.trim(),
        marca: form.marca.value.trim(),
        modelo: form.modelo.value.trim(),
        numero_serie: form.numero_serie.value.trim(),
        plant: form.plant.value.trim(),
        material: form.material.value.trim(),
        asset_tag: form.asset_tag.value.trim(),
        qty_sap: parseInt(form.qty_sap.value),
        qty_eaim: parseInt(form.qty_eaim.value),
        cliente_nombre: form.cliente_nombre.value.trim() || null,
        cliente_direccion: form.cliente_direccion.value.trim() || null,
        categoria: form.categoria.value,
        estado: form.estado.value || 'disponible',
        ubicacion_actual: form.ubicacion_actual.value || 'Almacén Central'
    };

    if (!body.nombre || !body.marca || !body.modelo || !body.numero_serie || !body.categoria || !body.plant || !body.material || !body.asset_tag) {
        showToast('Complete todos los campos obligatorios', 'error');
        return;
    }

    try {
        await api('POST', '/api/equipos', body);
        showToast('Activo registrado exitosamente');
        closeAllModals();
        loadEquipos();
    } catch {}
}

// ==========================================
// MOVIMIENTOS SECTION
// ==========================================
async function loadMovimientos() {
    try {
        APP.equipos = await api('GET', '/api/equipos') || [];
    } catch { APP.equipos = []; }

    const select = document.getElementById('mov-equipo');
    select.innerHTML = '<option value="">-- Seleccionar equipo --</option>' +
        APP.equipos.map(e => `<option value="${e.id}">${e.nombre} - Material: ${e.material} (SN: ${e.numero_serie})</option>`).join('');
    
    // Reset client inputs display
    document.getElementById('mov-cliente-fields').style.display = 'none';
    document.getElementById('mov-cliente-nombre').required = false;
    document.getElementById('mov-cliente-direccion').required = false;
}

async function submitMovimiento(e) {
    e.preventDefault();
    const form = e.target;
    const body = {
        equipo_id: parseInt(form.equipo_id.value),
        tipo_movimiento: form.tipo_movimiento.value,
        ubicacion_destino: form.ubicacion_destino.value,
        nuevo_estado: form.nuevo_estado.value || null,
        observaciones: form.observaciones.value.trim() || null,
        cliente_nombre: form.cliente_nombre.value.trim() || null,
        cliente_direccion: form.cliente_direccion.value.trim() || null
    };

    if (!body.equipo_id || !body.tipo_movimiento || !body.ubicacion_destino) {
        showToast('Complete los campos obligatorios', 'error');
        return;
    }

    if (body.tipo_movimiento === 'instalacion_nodo' && (!body.cliente_nombre || !body.cliente_direccion)) {
        showToast('Complete el nombre y dirección del cliente para la instalación', 'error');
        return;
    }

    try {
        await api('POST', '/api/movimientos', body);
        showToast('Movimiento y novedad registrados exitosamente');
        form.reset();
        loadMovimientos();
    } catch {}
}

// ==========================================
// BÚSQUEDA QR
// ==========================================
function loadBusquedaQR() {
    document.getElementById('qr-search-result').innerHTML = '';
    document.getElementById('qr-search-input').value = '';
    document.getElementById('qr-search-input').focus();
    stopCameraScanner();
}

async function buscarPorSerie() {
    const serie = document.getElementById('qr-search-input').value.trim();
    const container = document.getElementById('qr-search-result');

    if (!serie) {
        container.innerHTML = '';
        return;
    }

    try {
        const equipo = await api('GET', `/api/equipos/serie/${encodeURIComponent(serie)}`);
        if (!equipo) {
            container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔍</div><div class="empty-state-title">Equipo no encontrado</div><div class="empty-state-text">Verifique la placa o número de serie</div></div>';
            return;
        }

        let historial = [];
        try { historial = await api('GET', `/api/movimientos/equipo/${equipo.id}`) || []; } catch {}

        const dev = equipo.qty_sap - equipo.qty_eaim;
        container.innerHTML = `
            <div class="equipo-detail-card animate-fade-in-up">
                <div class="equipo-detail-header">
                    <span class="equipo-detail-name">${equipo.nombre}</span>
                    <span class="badge ${ESTADO_BADGE[equipo.estado]}">${LABELS.estado[equipo.estado]}</span>
                </div>
                <div class="equipo-detail-body">
                    <div class="detail-grid">
                        <div class="detail-item"><label>Material SAP</label><span><code>${equipo.material}</code></span></div>
                        <div class="detail-item"><label>Marca / Modelo</label><span>${equipo.marca} / ${equipo.modelo}</span></div>
                        <div class="detail-item"><label>Nº Serie</label><span><code>${equipo.numero_serie}</code></span></div>
                        <div class="detail-item"><label>Asset Tag (Placa)</label><span><code>${equipo.asset_tag}</code></span></div>
                        <div class="detail-item"><label>Plant</label><span>${equipo.plant}</span></div>
                        <div class="detail-item"><label>SLOC (Ubicación)</label><span>${LABELS.ubicacion[equipo.ubicacion_actual] || equipo.ubicacion_actual}</span></div>
                        <div class="detail-item"><label>Cantidad SAP</label><span>${equipo.qty_sap}</span></div>
                        <div class="detail-item"><label>Cantidad EAIM (Real)</label><span>${equipo.qty_eaim}</span></div>
                        <div class="detail-item"><label>Desviación</label><span style="font-weight:700;color:${dev !== 0 ? 'var(--color-emergencia)' : 'var(--color-operativo)'}">${dev}</span></div>
                        <div class="detail-item"><label>Cliente Asignado</label><span>${equipo.cliente_nombre || '—'}</span></div>
                        <div class="detail-item"><label>Dirección Instalación</label><span>${equipo.cliente_direccion || '—'}</span></div>
                        <div class="detail-item"><label>Fecha Registro</label><span>${formatDate(equipo.fecha_registro)}</span></div>
                    </div>
                    <div class="qr-container">
                        <img src="/api/equipos/${equipo.id}/qr" alt="QR">
                        <a class="btn btn-secondary btn-sm" href="/api/equipos/${equipo.id}/qr" download="QR_${equipo.numero_serie}.png">⬇ Descargar QR</a>
                    </div>
                    ${historial.length > 0 ? `
                        <h3 style="font-size:1rem;font-weight:600;margin:var(--space-lg) 0 var(--space-md);color:var(--text-primary);">Historial de Novedades</h3>
                        <div class="timeline">${historial.map(h => `
                            <div class="timeline-item">
                                <div class="timeline-date">${formatDate(h.fecha_movimiento)}</div>
                                <div class="timeline-content">
                                    <div class="timeline-type">${LABELS.movimiento[h.tipo_movimiento]}</div>
                                    <div class="timeline-detail">
                                        ${h.ubicacion_origen ? (LABELS.ubicacion[h.ubicacion_origen] || h.ubicacion_origen) + ' → ' : ''}${LABELS.ubicacion[h.ubicacion_destino] || h.ubicacion_destino}
                                        ${h.cliente_nombre ? `<br><strong>Instalado en:</strong> ${h.cliente_nombre} (${h.cliente_direccion})` : ''}
                                        ${h.observaciones ? '<br><strong>Novedad:</strong> <em>' + h.observaciones + '</em>' : ''}
                                    </div>
                                </div>
                            </div>`).join('')}
                        </div>` : ''}
                </div>
            </div>
        `;
    } catch {
        container.innerHTML = '<div class="empty-state"><div class="empty-state-icon">❌</div><div class="empty-state-title">Equipo no encontrado</div></div>';
    }
}

// ==========================================
// INTEGRACIÓN LECTOR QR CON CÁMARA (html5-qrcode)
// ==========================================
let html5QrCodeScanner = null;

function toggleCameraScanner() {
    const container = document.getElementById('qr-reader-container');
    const btn = document.getElementById('btn-toggle-camera');
    
    if (container.style.display === 'none') {
        container.style.display = 'block';
        btn.textContent = '✕ Detener Cámara';
        btn.className = 'btn btn-secondary';
        startCameraScanner();
    } else {
        stopCameraScanner();
    }
}

function startCameraScanner() {
    html5QrCodeScanner = new Html5QrcodeScanner(
        "qr-reader", 
        { fps: 10, qrbox: {width: 250, height: 250} },
        false
    );
    
    html5QrCodeScanner.render(
        (decodedText) => {
            document.getElementById('qr-search-input').value = decodedText;
            showToast(`QR detectado: ${decodedText}`);
            stopCameraScanner();
            buscarPorSerie();
        },
        (error) => {}
    );
}

function stopCameraScanner() {
    const container = document.getElementById('qr-reader-container');
    const btn = document.getElementById('btn-toggle-camera');
    if (container) container.style.display = 'none';
    if (btn) {
        btn.textContent = '📷 Iniciar Escáner de Cámara';
        btn.className = 'btn btn-primary';
    }
    
    if (html5QrCodeScanner) {
        html5QrCodeScanner.clear().catch(err => console.error("Error al detener lector QR", err));
        html5QrCodeScanner = null;
    }
}

// ==========================================
// USUARIOS SECTION (Admin)
// ==========================================
async function loadUsuarios() {
    try {
        APP.usuarios = await api('GET', '/api/usuarios') || [];
    } catch { APP.usuarios = []; }
    renderUsuariosTable();
}

function renderUsuariosTable() {
    const container = document.getElementById('usuarios-table-body');
    if (APP.usuarios.length === 0) {
        container.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="empty-state-title">Sin usuarios</div></div></td></tr>';
        return;
    }

    container.innerHTML = APP.usuarios.map(u => `
        <tr>
            <td><strong>${u.nombre_completo}</strong></td>
            <td><code>${u.username}</code></td>
            <td>${u.email}</td>
            <td><span class="badge badge-${u.rol}">${LABELS.rol[u.rol]}</span></td>
            <td>${formatDate(u.fecha_creacion)}</td>
            <td>
                <div class="table-actions">
                    ${u.id !== APP.user.id ? `
                        <button class="btn btn-icon btn-sm" onclick="toggleUserRole(${u.id}, '${u.rol}')" title="Cambiar rol">🔄</button>
                        <button class="btn btn-icon btn-sm" onclick="deleteUser(${u.id}, '${u.nombre_completo}')" title="Eliminar" style="color:var(--color-emergencia)">🗑</button>
                    ` : '<span style="font-size:0.75rem;color:var(--text-muted)">Tú</span>'}
                </div>
            </td>
        </tr>
    `).join('');
}

async function toggleUserRole(id, currentRole) {
    const newRole = currentRole === 'admin' ? 'tecnico' : 'admin';
    try {
        await api('PUT', `/api/usuarios/${id}/rol`, { rol: newRole });
        showToast(`Rol actualizado a ${LABELS.rol[newRole]}`);
        loadUsuarios();
    } catch {}
}

async function deleteUser(id, name) {
    if (!confirm(`¿Está seguro de eliminar al usuario "${name}"?`)) return;
    try {
        await api('DELETE', `/api/usuarios/${id}`);
        showToast('Usuario eliminado');
        loadUsuarios();
    } catch {}
}

// ==========================================
// NEW USER MODAL (Admin)
// ==========================================
function showNewUserModal() {
    document.getElementById('new-user-form').reset();
    openModal('new-user-modal');
}

async function submitNewUser(e) {
    e.preventDefault();
    const form = e.target;
    const body = {
        nombre_completo: form.nombre_completo.value.trim(),
        username: form.username.value.trim(),
        email: form.email.value.trim(),
        password: form.password.value,
        rol: form.rol.value
    };

    if (!body.nombre_completo || !body.username || !body.email || !body.password) {
        showToast('Complete todos los campos', 'error');
        return;
    }

    const regex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>_\-\[\]\\]).{8,}$/;
    if (!regex.test(body.password)) {
        showToast('La contraseña debe tener al menos 8 caracteres, incluir una mayúscula, un número y un carácter especial.', 'error');
        return;
    }

    try {
        await api('POST', '/api/usuarios/registro', body);
        showToast('Usuario creado exitosamente');
        closeAllModals();
        loadUsuarios();
    } catch {}
}

// ==========================================
// AJUSTES SECTION (Admin)
// ==========================================
function loadAjustes() {
    document.getElementById('config-nombre').value = APP.config.nombre_empresa || '';

    const logoPreview = document.getElementById('config-logo-preview');
    if (APP.config.logo_url) {
        logoPreview.innerHTML = `<img src="${APP.config.logo_url}" alt="Logo">`;
    } else {
        logoPreview.innerHTML = '<span style="font-size:0.8rem;color:var(--text-muted)">Sin logo cargado</span>';
    }

    const bannerPreview = document.getElementById('config-banner-preview');
    if (APP.config.banner_url) {
        bannerPreview.innerHTML = `<img src="${APP.config.banner_url}" alt="Banner">`;
    } else {
        bannerPreview.innerHTML = '<span style="font-size:0.8rem;color:var(--text-muted)">Sin banner cargado</span>';
    }
}

function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

async function submitConfig(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData();

    const nombre = form.nombre_empresa.value.trim();
    if (nombre) formData.append('nombre_empresa', nombre);

    const logoFile = form.logo.files[0];
    if (logoFile) formData.append('logo', logoFile);

    const bannerFile = form.banner.files[0];
    if (bannerFile) formData.append('banner', bannerFile);

    try {
        const config = await api('POST', '/api/config', formData, true);
        if (config) {
            APP.config = config;
            updateAppBranding();
            loadAjustes();
            showToast('Configuración actualizada');
        }
    } catch {}
}

// ==========================================
// LOGS Y AUDITORÍA DEL SISTEMA (Admin)
// ==========================================
async function loadLogs() {
    try {
        APP.logs = await api('GET', '/api/logs') || [];
    } catch { APP.logs = []; }
    renderLogsTable(APP.logs);
}

function filterLogs() {
    const search = document.getElementById('filter-log-search').value.toLowerCase();
    const nivel = document.getElementById('filter-log-nivel').value;

    let filtered = APP.logs;
    if (nivel) filtered = filtered.filter(l => l.nivel === nivel);
    if (search) filtered = filtered.filter(l =>
        (l.usuario_username && l.usuario_username.toLowerCase().includes(search)) ||
        l.accion.toLowerCase().includes(search) ||
        l.detalle.toLowerCase().includes(search)
    );
    renderLogsTable(filtered);
}

function renderLogsTable(logs) {
    const container = document.getElementById('logs-table-body');
    if (!logs || logs.length === 0) {
        container.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="empty-state-icon">📜</div><div class="empty-state-title">No hay registros de auditoría</div></div></td></tr>';
        return;
    }

    container.innerHTML = logs.map(l => `
        <tr>
            <td style="white-space:nowrap;font-size:0.8rem;color:var(--text-secondary);">${formatDate(l.fecha)}</td>
            <td><strong>${l.usuario_username || 'Sistema / Anon'}</strong></td>
            <td><span class="badge ${LOG_BADGE[l.nivel] || 'badge-operativo'}">${l.nivel}</span></td>
            <td><code>${l.accion}</code></td>
            <td style="font-size:0.85rem;">${l.detalle}</td>
            <td><code>${l.ip_origen || '127.0.0.1'}</code></td>
        </tr>
    `).join('');
}

// ==========================================
// MODAL HELPERS
// ==========================================
function openModal(id) {
    document.getElementById(id).classList.add('show');
}

function closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('show'));
    stopCameraScanner();
}

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) closeAllModals();
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeAllModals();
});

// ==========================================
// EXPORT: EXCEL
// ==========================================
function exportExcel() {
    if (!APP.equipos || APP.equipos.length === 0) {
        showToast('No hay equipos para exportar', 'error');
        return;
    }

    const rows = APP.equipos.map(e => ({
        'Material': e.material,
        'Nombre/Descripción': e.nombre,
        'Plant': e.plant,
        'SLOC (Ubicación)': e.ubicacion_actual,
        'Asset Tag': e.asset_tag,
        'Nº Serie': e.numero_serie,
        'Qty SAP': e.qty_sap,
        'Qty EAIM': e.qty_eaim,
        'Desviación': e.qty_sap - e.qty_eaim,
        'Cliente': e.cliente_nombre || '—',
        'Dirección Cliente': e.cliente_direccion || '—',
        'Estado': LABELS.estado[e.estado] || e.estado,
        'Fecha Registro': formatDate(e.fecha_registro)
    }));

    const ws = XLSX.utils.json_to_sheet(rows);

    ws['!cols'] = [
        { wch: 15 }, { wch: 28 }, { wch: 18 }, { wch: 18 },
        { wch: 18 }, { wch: 20 }, { wch: 10 }, { wch: 10 },
        { wch: 12 }, { wch: 25 }, { wch: 30 }, { wch: 15 }, { wch: 22 }
    ];

    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Inventario LogiScan');

    const fecha = new Date().toISOString().slice(0, 10);
    XLSX.writeFile(wb, `LogiScan_Inventario_${fecha}.xlsx`);
    showToast('Reporte Excel descargado');
}

// ==========================================
// EXPORT: PDF
// ==========================================
function exportPDF() {
    if (!APP.equipos || APP.equipos.length === 0) {
        showToast('No hay equipos para exportar', 'error');
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });

    const fecha = new Date();
    const fechaStr = formatDate(fecha.toISOString());
    const empresa = APP.config.nombre_empresa || 'LogiScan Telecom';

    doc.setFontSize(18);
    doc.setTextColor(30, 30, 30);
    doc.text(empresa, 14, 18);

    doc.setFontSize(11);
    doc.setTextColor(100, 100, 100);
    doc.text('Reporte de Conciliación de Inventario (SAP vs EAIM)', 14, 26);

    doc.setFontSize(9);
    doc.text(`Generado: ${fechaStr}`, 14, 32);
    doc.text(`Total de materiales: ${APP.equipos.length}`, 14, 37);

    const disponibles = APP.equipos.filter(e => e.estado === 'disponible').length;
    const asignados = APP.equipos.filter(e => e.estado === 'asignado').length;
    const mantenimiento = APP.equipos.filter(e => e.estado === 'en_mantenimiento').length;
    const bajas = APP.equipos.filter(e => e.estado === 'baja').length;

    doc.setFontSize(8);
    doc.setTextColor(39, 174, 96);
    doc.text(`Disponible: ${disponibles}`, 130, 37);
    doc.setTextColor(41, 128, 185);
    doc.text(`Asignado: ${asignados}`, 165, 37);
    doc.setTextColor(230, 126, 34);
    doc.text(`Mantenimiento: ${mantenimiento}`, 200, 37);
    doc.setTextColor(231, 76, 60);
    doc.text(`De Baja: ${bajas}`, 240, 37);

    doc.setDrawColor(200, 200, 200);
    doc.line(14, 39, 283, 39);

    const tableData = APP.equipos.map(e => [
        e.material,
        e.nombre,
        e.plant,
        e.ubicacion_actual,
        e.asset_tag,
        e.numero_serie,
        e.qty_sap,
        e.qty_eaim,
        e.qty_sap - e.qty_eaim,
        LABELS.estado[e.estado] || e.estado,
        e.cliente_nombre || '—',
        e.cliente_direccion || '—'
    ]);

    doc.autoTable({
        startY: 42,
        head: [['Material', 'Descripción', 'Plant', 'SLOC', 'Asset Tag', 'Nº Serie', 'Qty SAP', 'Qty EAIM', 'Desv.', 'Estado', 'Cliente', 'Dirección']],
        body: tableData,
        styles: {
            fontSize: 7,
            cellPadding: 1.5,
            lineColor: [220, 220, 220],
            lineWidth: 0.15,
        },
        headStyles: {
            fillColor: [31, 58, 86],
            textColor: 255,
            fontStyle: 'bold',
            fontSize: 7.5,
        },
        alternateRowStyles: {
            fillColor: [248, 250, 252],
        },
        columnStyles: {
            0: { cellWidth: 16 },
            1: { cellWidth: 32 },
            2: { cellWidth: 20 },
            3: { cellWidth: 15 },
            4: { cellWidth: 22 },
            5: { cellWidth: 22 },
            6: { cellWidth: 12, halign: 'center' },
            7: { cellWidth: 12, halign: 'center' },
            8: { cellWidth: 12, halign: 'center' },
            9: { cellWidth: 18 },
            10: { cellWidth: 25 },
            11: { cellWidth: 30 }
        },
        didParseCell: function (data) {
            if (data.section === 'body' && data.column.index === 8) {
                const val = parseInt(data.cell.raw);
                if (val !== 0) {
                    data.cell.styles.textColor = [231, 76, 60];
                    data.cell.styles.fontStyle = 'bold';
                } else {
                    data.cell.styles.textColor = [39, 174, 96];
                }
            }
            if (data.section === 'body' && data.column.index === 9) {
                const val = data.cell.raw;
                if (val === 'Disponible') data.cell.styles.textColor = [39, 174, 96];
                else if (val === 'Asignado') data.cell.styles.textColor = [41, 128, 185];
                else if (val === 'En Mantenimiento') data.cell.styles.textColor = [230, 126, 34];
                else if (val === 'De Baja') data.cell.styles.textColor = [231, 76, 60];
            }
        },
        margin: { left: 14, right: 14 },
    });

    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(7);
        doc.setTextColor(150, 150, 150);
        doc.text(`${empresa} - Reporte de Auditoría generado el ${fechaStr} — Página ${i} de ${pageCount}`, 14, doc.internal.pageSize.height - 8);
    }

    const fechaFile = fecha.toISOString().slice(0, 10);
    doc.save(`LogiScan_Auditoria_${fechaFile}.pdf`);
    showToast('Reporte PDF descargado');
}

// ==========================================
// INIT ON DOM LOAD
// ==========================================
document.addEventListener('DOMContentLoaded', async () => {
    initLoginForm();

    // Check existing session
    if (APP.token) {
        try {
            const user = await api('GET', '/api/usuarios/me');
            if (user) {
                APP.user = user;
                localStorage.setItem('teletrack_user', JSON.stringify(user));
                initApp();
                return;
            }
        } catch {}
    }
    showLogin();
});
