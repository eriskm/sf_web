css_content = '''        :root {
            --primary: #3B82F6; /* Blue SaaS */
            --primary-light: #EFF6FF;
            --success: #10B981;
            --success-light: #ECFDF5;
            --warning: #F59E0B;
            --warning-light: #FFFBEB;
            --danger: #EF4444;
            --danger-light: #FEF2F2;
            --purple: #8B5CF6;
            --purple-light: #F5F3FF;
            --dark: #0f172a;
            --gray: #64748B;
            --gray-light: #f1f5f9;
            --bg-body: #f8fafc;
            --card-bg: #FFFFFF;
            --border: #e2e8f0;
            --sidebar-width: 250px;
            --font-main: 'Inter', sans-serif;
            --font-head: 'Poppins', sans-serif;
        }

        body { 
            font-family: var(--font-main); 
            margin: 0; 
            background: var(--bg-body); 
            color: var(--dark);
            display: flex;
            overflow-x: hidden;
        }

        h1, h2, h3, h4, .poppins { font-family: var(--font-head); margin: 0; }
        a { text-decoration: none; color: inherit; }
        
        /* Layout */
        .sidebar {
            width: var(--sidebar-width);
            background: var(--card-bg);
            border-right: 1px solid var(--border);
            height: 100vh;
            position: fixed;
            left: 0;
            top: 0;
            display: flex;
            flex-direction: column;
            z-index: 1000;
        }
        
        .main-content {
            margin-left: var(--sidebar-width);
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }

        /* Sidebar Elements */
        .sidebar-header {
            padding: 20px 24px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid var(--border);
        }
        .sidebar-logo {
            background: #ef4444;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 1em;
            font-family: var(--font-head);
        }
        .sidebar-title {
            font-family: var(--font-head);
            font-weight: 800;
            font-size: 1.1em;
            line-height: 1.2;
            text-transform: uppercase;
        }

        /* User Profile in Sidebar */
        .sidebar-user {
            padding: 20px 24px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 1px solid var(--border);
        }
        .sidebar-user img {
            width: 40px; height: 40px; border-radius: 50%; object-fit: cover;
        }
        .sidebar-user-info { display: flex; flex-direction: column; }
        .sidebar-user-name { font-weight: 700; font-size: 0.95em; display: flex; align-items: center; gap: 5px; }
        .user-role-badge { background: var(--primary-light); color: var(--primary); font-size: 0.7em; padding: 2px 6px; border-radius: 4px; font-weight: 600; }
        .sidebar-user-desc { font-size: 0.8em; color: var(--gray); margin-top: 2px; }

        .sidebar-menu { padding: 20px 16px; flex: 1; overflow-y: auto; }
        .menu-label { font-size: 0.75em; color: var(--gray); font-weight: 600; text-transform: uppercase; margin: 15px 0 10px 10px; letter-spacing: 0.5px; }
        
        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            color: var(--gray);
            border-radius: 10px;
            font-weight: 600;
            margin-bottom: 4px;
            transition: all 0.2s ease;
            font-size: 0.95em;
        }
        .menu-item:hover { background: var(--gray-light); color: var(--dark); }
        .menu-item.active { background: var(--primary-light); color: var(--primary); }
        .menu-item svg { width: 20px; height: 20px; stroke-width: 2; }
        
        .sidebar-footer {
            padding: 20px 16px;
            border-top: 1px solid var(--border);
        }

        /* Topbar */
        .topbar {
            height: 70px;
            background: var(--card-bg);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 32px;
            position: sticky;
            top: 0;
            z-index: 999;
        }
        .topbar-left h2 { font-size: 1.4em; color: var(--dark); margin-bottom: 2px; }
        .topbar-left p { color: var(--gray); font-size: 0.85em; margin: 0; }
        
        .topbar-right { display: flex; align-items: center; gap: 15px; }
        .date-badge {
            display: flex; align-items: center; gap: 8px;
            padding: 8px 12px; border: 1px solid var(--border); border-radius: 8px;
            font-size: 0.85em; font-weight: 500; color: var(--dark);
        }
        .btn-icon {
            width: 36px; height: 36px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            background: transparent; border: 1px solid transparent;
            cursor: pointer; color: var(--gray); transition: 0.2s;
            position: relative;
        }
        .btn-icon:hover { background: var(--gray-light); }
        .notif-dot {
            position: absolute; top: 4px; right: 6px;
            width: 16px; height: 16px; background: var(--danger);
            color: white; font-size: 0.6em; font-weight: bold;
            display: flex; align-items: center; justify-content: center;
            border-radius: 50%; border: 2px solid var(--card-bg);
        }

        /* Content Area */
        .content-body { padding: 32px; }

        /* Metric Cards */
        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr) 1.5fr; gap: 20px; margin-bottom: 30px; }
        .metric-card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
            display: flex; flex-direction: column; justify-content: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .metric-card:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); }
        .metric-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .metric-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2em; color: white; }
        .metric-title { color: var(--gray); font-size: 0.85em; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { font-size: 1.5em; font-weight: 800; color: var(--dark); font-family: var(--font-head); margin-bottom: 8px; }
        .metric-trend { display: inline-flex; align-items: center; gap: 5px; font-size: 0.75em; font-weight: 600; }
        .trend-up { color: var(--success); background: var(--success-light); padding: 2px 6px; border-radius: 4px; }
        .trend-down { color: var(--danger); background: var(--danger-light); padding: 2px 6px; border-radius: 4px; }
        .trend-text { color: var(--gray); font-weight: 500; }

        .target-card {
            background: var(--card-bg); border-radius: 16px; padding: 20px; border: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between;
        }
        .target-info { flex: 1; }
        .target-title { font-size: 0.75em; color: var(--gray); font-weight: 700; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.5px; }
        .target-val { font-size: 1.4em; font-weight: 800; color: var(--dark); font-family: var(--font-head); margin-bottom: 10px; }
        .target-bar-bg { width: 100%; height: 6px; background: var(--border); border-radius: 3px; overflow: hidden; margin-bottom: 6px; }
        .target-bar-fill { height: 100%; background: var(--primary); border-radius: 3px; }
        .target-desc { font-size: 0.75em; color: var(--gray); font-weight: 500; }
        
        .progress-ring { position: relative; width: 64px; height: 64px; border-radius: 50%; background: conic-gradient(var(--primary) var(--pct), var(--border) 0deg); display: flex; align-items: center; justify-content: center; }
        .progress-ring-inner { width: 52px; height: 52px; background: var(--card-bg); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.9em; color: var(--primary); font-family: var(--font-head); }

        /* Middle Grid (Aksi, Insight, Teknisi) */
        .middle-grid { display: grid; grid-template-columns: 1fr 1fr 0.6fr; gap: 20px; margin-bottom: 30px; }
        
        .section-box { background: var(--card-bg); border-radius: 16px; padding: 24px; border: 1px solid var(--border); }
        .section-title { font-size: 0.85em; color: var(--gray); font-weight: 700; text-transform: uppercase; margin-bottom: 20px; letter-spacing: 0.5px; display: flex; justify-content: space-between; align-items: center; }
        
        .action-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        .action-btn { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; padding: 20px 10px; border-radius: 12px; border: 1px solid var(--border); cursor: pointer; transition: 0.2s; background: white; text-align: center; }
        .action-btn:hover { border-color: var(--primary); box-shadow: 0 4px 12px rgba(59,130,246,0.1); transform: translateY(-2px); }
        .action-icon { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.3em; }
        .action-text { font-size: 0.8em; font-weight: 700; color: var(--dark); line-height: 1.2; }
        .action-sub { font-size: 0.65em; color: var(--gray); font-weight: 500; margin-top: 4px; }

        .insight-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
        .insight-card { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 15px 10px; border-radius: 12px; border: 1px solid var(--border); background: var(--bg-body); }
        .insight-title { font-size: 0.7em; font-weight: 700; margin-bottom: 10px; }
        .insight-icon { font-size: 1.5em; margin-bottom: 10px; }
        .insight-val { font-size: 1.3em; font-weight: 800; font-family: var(--font-head); color: var(--dark); margin-bottom: 2px; }
        .insight-unit { font-size: 0.7em; color: var(--gray); font-weight: 600; }

        .tech-card { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; position: relative; padding: 10px; }
        .tech-avatar-wrapper { position: relative; margin-bottom: 15px; }
        .tech-avatar { width: 70px; height: 70px; border-radius: 50%; border: 3px solid var(--primary-light); object-fit: cover; }
        .tech-crown { position: absolute; top: -12px; left: -10px; font-size: 1.5em; transform: rotate(-15deg); }
        .tech-name { font-weight: 800; font-size: 1.1em; color: var(--dark); margin-bottom: 4px; }
        .tech-stat { font-size: 0.8em; color: var(--gray); font-weight: 500; margin-bottom: 8px; }
        .tech-money { color: var(--success); font-weight: 800; font-size: 1.1em; background: var(--success-light); padding: 4px 12px; border-radius: 20px; }

        /* Charts & AI Grid */
        .bottom-grid { display: grid; grid-template-columns: 1fr 1fr 0.6fr; gap: 20px; margin-bottom: 30px; }
        .chart-container { height: 260px; position: relative; width: 100%; }

        /* AI Panel */
        .ai-panel { display: flex; flex-direction: column; height: 100%; border: 1px solid var(--border); border-radius: 16px; background: var(--card-bg); overflow: hidden; }
        .ai-header { padding: 15px 20px; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; }
        .ai-bot-info { display: flex; align-items: center; gap: 10px; }
        .ai-bot-icon { width: 36px; height: 36px; border-radius: 50%; background: var(--primary-light); color: var(--primary); display: flex; align-items: center; justify-content: center; font-size: 1.2em; }
        .ai-bot-name { font-weight: 700; font-size: 0.9em; color: var(--dark); }
        .ai-bot-sub { font-size: 0.7em; color: var(--gray); }
        .ai-status { display: flex; align-items: center; gap: 6px; font-size: 0.75em; color: var(--success); font-weight: 600; }
        .status-dot { width: 8px; height: 8px; background: var(--success); border-radius: 50%; }
        
        .ai-body { padding: 20px; flex: 1; background: #fafbfc; overflow-y: auto; }
        .ai-bubble { background: white; border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
        .ai-greet { font-weight: 600; font-size: 0.9em; margin-bottom: 8px; }
        .ai-msg { font-size: 0.85em; color: var(--gray); line-height: 1.5; margin-bottom: 15px; }
        .ai-list { display: flex; flex-direction: column; gap: 12px; margin-bottom: 15px; }
        .ai-list-item { display: flex; align-items: flex-start; gap: 10px; font-size: 0.8em; font-weight: 500; color: var(--dark); line-height: 1.4; }
        .ai-list-icon { width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-size: 0.9em; }
        .btn-ai { background: var(--primary); color: white; border: none; border-radius: 8px; padding: 10px; width: 100%; font-weight: 600; font-size: 0.8em; cursor: pointer; transition: 0.2s; }
        .btn-ai:hover { background: #2563eb; }

        .ai-footer { padding: 15px; border-top: 1px solid var(--border); background: white; }
        .ai-input-box { display: flex; align-items: center; background: var(--bg-body); border: 1px solid var(--border); border-radius: 20px; padding: 6px 6px 6px 15px; }
        .ai-input-box input { flex: 1; border: none; background: transparent; outline: none; font-size: 0.85em; color: var(--dark); }
        .ai-send { width: 32px; height: 32px; border-radius: 50%; background: var(--primary-light); color: var(--primary); border: none; display: flex; align-items: center; justify-content: center; cursor: pointer; }

        /* Modern Table Area */
        .table-section { background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border); overflow: hidden; grid-column: span 2; }
        .table-header { padding: 20px 24px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }
        .table-title { font-family: var(--font-head); font-weight: 700; font-size: 1.1em; color: var(--dark); text-transform: uppercase; }
        .table-actions { display: flex; gap: 10px; }
        .search-box { display: flex; align-items: center; gap: 8px; border: 1px solid var(--border); padding: 8px 12px; border-radius: 8px; font-size: 0.85em; width: 250px; }
        .search-box input { border: none; outline: none; width: 100%; background: transparent; font-family: var(--font-main); }
        .btn-outline { border: 1px solid var(--border); background: white; padding: 8px 15px; border-radius: 8px; font-weight: 600; font-size: 0.85em; cursor: pointer; display: flex; align-items: center; gap: 8px; color: var(--dark); transition: 0.2s; }
        .btn-outline:hover { background: var(--gray-light); }
        .btn-primary { background: var(--primary); color: white; border: none; padding: 8px 15px; border-radius: 8px; font-weight: 600; font-size: 0.85em; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.2s; }
        .btn-primary:hover { background: #2563eb; }

        table { width: 100%; border-collapse: collapse; text-align: left; }
        th { padding: 15px 24px; font-size: 0.75em; font-weight: 700; color: var(--gray); text-transform: uppercase; border-bottom: 1px solid var(--border); background: #fafbfc; letter-spacing: 0.5px; }
        td { padding: 16px 24px; font-size: 0.85em; border-bottom: 1px solid var(--border); color: var(--dark); font-weight: 500; vertical-align: middle; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #f8fafc; }
        
        .td-pelanggan { display: flex; flex-direction: column; }
        .td-name { font-weight: 700; color: var(--dark); }
        .td-phone { font-size: 0.85em; color: var(--gray); margin-top: 2px; font-weight: 500; }
        
        .td-device { display: flex; align-items: center; gap: 10px; font-weight: 600; }
        .device-icon { color: var(--gray); font-size: 1.2em; }
        
        .td-tek { display: flex; align-items: center; gap: 10px; font-weight: 600; }
        .td-tek img { width: 28px; height: 28px; border-radius: 50%; object-fit: cover; }
        
        .td-laba { font-weight: 700; color: var(--success); }
        .td-laba-empty { color: var(--gray); font-weight: 500; }

        .td-actions { display: flex; gap: 8px; }
        .btn-action { width: 32px; height: 32px; border-radius: 6px; border: 1px solid var(--border); background: white; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: 0.2s; }
        .btn-edit { color: var(--primary); }
        .btn-edit:hover { background: var(--primary-light); border-color: var(--primary); }
        .btn-delete { color: var(--danger); }
        .btn-delete:hover { background: var(--danger-light); border-color: var(--danger); }

        .table-footer { padding: 15px 24px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; font-size: 0.8em; color: var(--gray); font-weight: 500; }
        .pagination { display: flex; gap: 5px; }
        .page-btn { width: 28px; height: 28px; border-radius: 6px; border: none; background: transparent; cursor: pointer; font-weight: 600; color: var(--gray); transition: 0.2s; }
        .page-btn:hover { background: var(--gray-light); }
        .page-btn.active { background: var(--primary); color: white; }

        /* Badges */
        .badge { padding: 6px 12px; border-radius: 6px; font-size: 0.75em; font-weight: 700; display: inline-block; letter-spacing: 0.5px; }
        .status-cash { background: var(--success-light); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }
        .status-done { background: var(--primary-light); color: var(--primary); border: 1px solid rgba(59, 130, 246, 0.2); }
        .status-wait { background: var(--warning-light); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.2); }
        .status-konfirmasi { background: var(--warning-light); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.2); }
        .status-analisa { background: var(--gray-light); color: var(--gray); border: 1px solid var(--border); }
        .status-cancel { background: var(--danger-light); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2); }
        .status-repair { background: var(--success-light); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }

        /* Helper Utilities */
        .text-success { color: var(--success); }
        .text-danger { color: var(--danger); }

        /* RESPONSIVE MEDIA QUERIES */
        @media (max-width: 1400px) {
            .metrics-grid { grid-template-columns: repeat(3, 1fr); }
            .target-card { grid-column: span 3; }
            .middle-grid, .bottom-grid { grid-template-columns: 1fr; }
            .ai-panel { display: none; } /* Hide AI panel on smaller screens for simplicity */
        }

        @media (max-width: 992px) {
            .metrics-grid { grid-template-columns: repeat(2, 1fr); }
            .target-card { grid-column: span 2; }
            .action-grid, .insight-grid { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 768px) {
            .sidebar { transform: translateX(-100%); }
            .main-content { margin-left: 0; }
            .metrics-grid { grid-template-columns: 1fr; }
            .target-card { grid-column: span 1; }
            
            table, thead, tbody, th, td, tr { display: block; }
            thead tr { position: absolute; top: -9999px; left: -9999px; }
            tr { border: 1px solid var(--border); margin-bottom: 15px; border-radius: 12px; padding: 10px; background: var(--card-bg); }
            td { border: none; border-bottom: 1px solid var(--border); position: relative; padding-left: 45%; text-align: right; }
            td:last-child { border-bottom: none; }
            td:before { position: absolute; top: 16px; left: 15px; width: 40%; padding-right: 10px; white-space: nowrap; text-align: left; font-weight: 600; color: var(--gray); content: attr(data-label); font-size: 0.85em; }
        }
'''

with open('static/dashboard.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print("CSS OVERWRITTEN SUCCESSFULLY!")
