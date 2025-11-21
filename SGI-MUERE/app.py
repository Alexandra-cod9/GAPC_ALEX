<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard GAPC - Grupo de Ahorro</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #6f42c1;
            --primary-dark: #3d1f6b;
            --secondary: #28a745; /* Verde más suave */
            --light: #f8f9fa;
            --dark: #343a40;
            --gray: #6c757d;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --info: #17a2b8;
            --border-radius: 8px;
            --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --transition: all 0.3s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background-color: #f5f7fb;
            color: var(--dark);
            line-height: 1.6;
        }

        .container {
            display: flex;
            min-height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            width: 250px;
            background: linear-gradient(to bottom, var(--primary), var(--primary-dark));
            color: white;
            padding: 20px 0;
            transition: var(--transition);
            box-shadow: var(--box-shadow);
        }

        .logo {
            text-align: center;
            padding: 0 20px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }

        .logo h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        .logo p {
            font-size: 14px;
            opacity: 0.8;
        }

        .user-profile {
            display: flex;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }

        .user-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-size: 20px;
        }

        .user-info h3 {
            font-size: 16px;
            margin-bottom: 5px;
        }

        .user-info p {
            font-size: 12px;
            opacity: 0.8;
        }

        .menu {
            list-style: none;
            padding: 0 15px;
        }

        .menu-item {
            margin-bottom: 5px;
        }

        .menu-link {
            display: flex;
            align-items: center;
            padding: 12px 15px;
            color: white;
            text-decoration: none;
            border-radius: var(--border-radius);
            transition: var(--transition);
        }

        .menu-link:hover, .menu-link.active {
            background-color: rgba(255, 255, 255, 0.1);
        }

        .menu-link i {
            margin-right: 10px;
            font-size: 18px;
            width: 24px;
            text-align: center;
        }

        /* Main Content */
        .main-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
        }

        .welcome-section h1 {
            font-size: 24px;
            margin-bottom: 5px;
            color: var(--primary);
        }

        .welcome-section p {
            color: var(--gray);
            font-size: 14px;
        }

        .date-time {
            text-align: right;
        }

        .date-time .date {
            font-size: 16px;
            font-weight: 600;
        }

        .date-time .time {
            font-size: 14px;
            color: var(--gray);
        }

        /* Dashboard Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }

        .card {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 20px;
            transition: var(--transition);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--dark);
        }

        .card-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
        }

        .card-content {
            margin-bottom: 10px;
        }

        .card-value {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .card-description {
            font-size: 14px;
            color: var(--gray);
        }

        .finance-summary {
            background: linear-gradient(to right, var(--primary), var(--primary-dark));
            color: white;
        }

        .finance-summary .card-icon {
            background-color: rgba(255, 255, 255, 0.2);
        }

        .members-summary .card-icon {
            background-color: var(--info);
        }

        .loans-summary .card-icon {
            background-color: var(--warning);
        }

        .meeting-summary .card-icon {
            background-color: var(--secondary);
        }

        /* Modules Grid */
        .modules-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .module-card {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 20px 15px;
            text-align: center;
            transition: var(--transition);
            cursor: pointer;
        }

        .module-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }

        .module-icon {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            color: white;
            font-size: 20px;
        }

        .module-icon.members {
            background-color: var(--info);
        }

        .module-icon.meetings {
            background-color: var(--secondary);
        }

        .module-icon.contributions {
            background-color: var(--success);
        }

        .module-icon.loans {
            background-color: var(--warning);
        }

        .module-icon.fines {
            background-color: var(--danger);
        }

        .module-icon.reports {
            background-color: var(--primary);
        }

        .module-icon.cycle {
            background-color: var(--primary-dark);
        }

        .module-icon.settings {
            background-color: var(--gray);
        }

        .module-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .module-description {
            font-size: 12px;
            color: var(--gray);
        }

        /* Notifications & Stats */
        .notifications-stats {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
        }

        .notifications {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 20px;
        }

        .section-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--dark);
            display: flex;
            align-items: center;
        }

        .section-title i {
            margin-right: 10px;
            color: var(--primary);
        }

        .notification-item {
            display: flex;
            align-items: flex-start;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }

        .notification-item:last-child {
            border-bottom: none;
        }

        .notification-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            color: white;
            font-size: 14px;
            flex-shrink: 0;
        }

        .notification-icon.warning {
            background-color: var(--warning);
        }

        .notification-icon.danger {
            background-color: var(--danger);
        }

        .notification-icon.info {
            background-color: var(--info);
        }

        .notification-icon.secondary {
            background-color: var(--secondary);
        }

        .notification-content h4 {
            font-size: 14px;
            margin-bottom: 5px;
        }

        .notification-content p {
            font-size: 13px;
            color: var(--gray);
        }

        .stats {
            background: white;
            border-radius: var(--border-radius);
            box-shadow: var(--box-shadow);
            padding: 20px;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }

        .stat-item:last-child {
            border-bottom: none;
        }

        .stat-info h4 {
            font-size: 14px;
            margin-bottom: 5px;
        }

        .stat-info p {
            font-size: 13px;
            color: var(--gray);
        }

        .stat-value {
            font-size: 18px;
            font-weight: 700;
        }

        .stat-value.positive {
            color: var(--success);
        }

        .stat-value.warning {
            color: var(--warning);
        }

        .stat-value.danger {
            color: var(--danger);
        }

        /* Responsive */
        @media (max-width: 992px) {
            .notifications-stats {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .container {
                flex-direction: column;
            }
            
            .sidebar {
                width: 100%;
                height: auto;
            }
            
            .dashboard-grid {
                grid-template-columns: 1fr 1fr;
            }
            
            .modules-grid {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }
        }

        @media (max-width: 576px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .modules-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="logo">
                <h1>🏦 GAPC</h1>
                <p>Sistema de Gestión de Grupos de Ahorro</p>
            </div>
            
            <div class="user-profile">
                <div class="user-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="user-info">
                    <h3>María López</h3>
                    <p>Presidenta</p>
                </div>
            </div>
            
            <ul class="menu">
                <li class="menu-item">
                    <a href="#" class="menu-link active">
                        <i class="fas fa-home"></i>
                        <span>Inicio</span>
                    </a>
                </li>
                <li class="menu-item">
                    <a href="#" class="menu-link">
                        <i class="fas fa-users"></i>
                        <span>Miembros</span>
                    </a>
                </li>
                <li class="menu-item">
                    <a href="#" class="menu-link">
                        <i class="fas fa-calendar-alt"></i>
                        <span>Reuniones</span>
                    </a>
                </li>
                <li class="menu-item">
                    <a href="#" class="menu-link">
                        <i class="fas fa-hand-holding-usd"></i>
                        <span>Finanzas</span>
                    </a>
                </li>
                <li class="menu-item">
                    <a href="#" class="menu-link">
                        <i class="fas fa-chart-bar"></i>
                        <span>Reportes</span>
                    </a>
                </li>
                <li class="menu-item">
                    <a href="#" class="menu-link">
                        <i class="fas fa-sync-alt"></i>
                        <span>Cierre de Ciclo</span>
                    </a>
                </li>
                <li class="menu-item">
                    <a href="#" class="menu-link">
                        <i class="fas fa-cog"></i>
                        <span>Configuración</span>
                    </a>
                </li>
                <li class="menu-item">
                    <a href="#" class="menu-link">
                        <i class="fas fa-sign-out-alt"></i>
                        <span>Cerrar Sesión</span>
                    </a>
                </li>
            </ul>
        </aside>
        
        <!-- Main Content -->
        <main class="main-content">
            <div class="header">
                <div class="welcome-section">
                    <h1>¡Bienvenido/a, María López!</h1>
                    <p>Presidenta - Grupo Las Mariposas</p>
                </div>
                <div class="date-time">
                    <div class="date">Miércoles, 20 de Noviembre de 2024</div>
                    <div class="time">14:30</div>
                </div>
            </div>
            
            <!-- Dashboard Summary -->
            <div class="dashboard-grid">
                <div class="card finance-summary">
                    <div class="card-header">
                        <div class="card-title">SALDO ACTUAL</div>
                        <div class="card-icon">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                    </div>
                    <div class="card-content">
                        <div class="card-value">$15,450.00</div>
                        <div class="card-description">Disponible en caja</div>
                    </div>
                </div>
                
                <div class="card members-summary">
                    <div class="card-header">
                        <div class="card-title">MIEMBROS</div>
                        <div class="card-icon">
                            <i class="fas fa-users"></i>
                        </div>
                    </div>
                    <div class="card-content">
                        <div class="card-value">25</div>
                        <div class="card-description">Miembros activos</div>
                    </div>
                </div>
                
                <div class="card loans-summary">
                    <div class="card-header">
                        <div class="card-title">PRÉSTAMOS ACTIVOS</div>
                        <div class="card-icon">
                            <i class="fas fa-hand-holding-usd"></i>
                        </div>
                    </div>
                    <div class="card-content">
                        <div class="card-value">8</div>
                        <div class="card-description">Préstamos vigentes</div>
                    </div>
                </div>
                
                <div class="card meeting-summary">
                    <div class="card-header">
                        <div class="card-title">PRÓXIMA REUNIÓN</div>
                        <div class="card-icon">
                            <i class="fas fa-calendar-alt"></i>
                        </div>
                    </div>
                    <div class="card-content">
                        <div class="card-value">22/11/2024</div>
                        <div class="card-description">Viernes - 14:00</div>
                    </div>
                </div>
            </div>
            
            <!-- Modules -->
            <h2 class="section-title"><i class="fas fa-th-large"></i> Módulos del Sistema</h2>
            <div class="modules-grid">
                <div class="module-card">
                    <div class="module-icon members">
                        <i class="fas fa-users"></i>
                    </div>
                    <div class="module-title">Miembros</div>
                    <div class="module-description">Gestión de miembros del grupo</div>
                </div>
                
                <div class="module-card">
                    <div class="module-icon meetings">
                        <i class="fas fa-calendar-alt"></i>
                    </div>
                    <div class="module-title">Reuniones</div>
                    <div class="module-description">Calendario y registro de reuniones</div>
                </div>
                
                <div class="module-card">
                    <div class="module-icon contributions">
                        <i class="fas fa-hand-holding-usd"></i>
                    </div>
                    <div class="module-title">Aportes</div>
                    <div class="module-description">Registro de aportes y ahorros</div>
                </div>
                
                <div class="module-card">
                    <div class="module-icon loans">
                        <i class="fas fa-file-invoice-dollar"></i>
                    </div>
                    <div class="module-title">Préstamos</div>
                    <div class="module-description">Gestión de préstamos y pagos</div>
                </div>
                
                <div class="module-card">
                    <div class="module-icon fines">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="module-title">Multas</div>
                    <div class="module-description">Control de multas y sanciones</div>
                </div>
                
                <div class="module-card">
                    <div class="module-icon reports">
                        <i class="fas fa-chart-bar"></i>
                    </div>
                    <div class="module-title">Reportes</div>
                    <div class="module-description">Reportes financieros y estadísticas</div>
                </div>
                
                <div class="module-card">
                    <div class="module-icon cycle">
                        <i class="fas fa-sync-alt"></i>
                    </div>
                    <div class="module-title">Cierre de Ciclo</div>
                    <div class="module-description">Cierre de período y reparto</div>
                </div>
                
                <div class="module-card">
                    <div class="module-icon settings">
                        <i class="fas fa-cog"></i>
                    </div>
                    <div class="module-title">Configuración</div>
                    <div class="module-description">Ajustes del grupo y reglamento</div>
                </div>
            </div>
            
            <!-- Notifications & Stats -->
            <div class="notifications-stats">
                <div class="notifications">
                    <h2 class="section-title"><i class="fas fa-bell"></i> Notificaciones y Alertas</h2>
                    
                    <div class="notification-item">
                        <div class="notification-icon warning">
                            <i class="fas fa-exclamation"></i>
                        </div>
                        <div class="notification-content">
                            <h4>Préstamo próximo a vencer</h4>
                            <p>Ana García - Vence en 3 días ($500.00)</p>
                        </div>
                    </div>
                    
                    <div class="notification-item">
                        <div class="notification-icon danger">
                            <i class="fas fa-times"></i>
                        </div>
                        <div class="notification-content">
                            <h4>Préstamo VENCIDO</h4>
                            <p>Rosa Martínez - $750.00</p>
                        </div>
                    </div>
                    
                    <div class="notification-item">
                        <div class="notification-icon info">
                            <i class="fas fa-calendar"></i>
                        </div>
                        <div class="notification-content">
                            <h4>Próxima Reunión</h4>
                            <p>En 2 días - 22/11/2024 a las 14:00</p>
                        </div>
                    </div>
                    
                    <div class="notification-item">
                        <div class="notification-icon secondary">
                            <i class="fas fa-money-bill-wave"></i>
                        </div>
                        <div class="notification-content">
                            <h4>Multas Pendientes</h4>
                            <p>3 multas pendientes - Total: $45.00</p>
                        </div>
                    </div>
                </div>
                
                <div class="stats">
                    <h2 class="section-title"><i class="fas fa-chart-line"></i> Estadísticas Rápidas</h2>
                    
                    <div class="stat-item">
                        <div class="stat-info">
                            <h4>Asistencia Promedio</h4>
                            <p>Último mes</p>
                        </div>
                        <div class="stat-value positive">92%</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-info">
                            <h4>Total Ahorrado</h4>
                            <p>Este mes</p>
                        </div>
                        <div class="stat-value positive">$3,250.00</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-info">
                            <h4>Préstamos en Mora</h4>
                            <p>Actualmente</p>
                        </div>
                        <div class="stat-value danger">2</div>
                    </div>
                    
                    <div class="stat-item">
                        <div class="stat-info">
                            <h4>Reuniones</h4>
                            <p>Este mes</p>
                        </div>
                        <div class="stat-value">4</div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Actualizar hora en tiempo real
        function updateTime() {
            const now = new Date();
            const timeElement = document.querySelector('.time');
            
            const hours = now.getHours().toString().padStart(2, '0');
            const minutes = now.getMinutes().toString().padStart(2, '0');
            
            timeElement.textContent = `${hours}:${minutes}`;
        }
        
        // Actualizar cada minuto
        setInterval(updateTime, 60000);
        
        // Inicializar
        updateTime();
        
        // Efectos de interacción
        document.querySelectorAll('.module-card').forEach(card => {
            card.addEventListener('click', function() {
                alert(`Accediendo al módulo: ${this.querySelector('.module-title').textContent}`);
            });
        });
    </script>
</body>
</html>
