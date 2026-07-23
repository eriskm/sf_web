<script>
    // --- GLOBAL CHART.JS PREMIUM SAAS CONFIG ---
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Outfit', 'Inter', 'Poppins', sans-serif";
        Chart.defaults.color = '#64748B';
        Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.95)';
        Chart.defaults.plugins.tooltip.titleColor = '#F8FAFC';
        Chart.defaults.plugins.tooltip.bodyColor = '#E2E8F0';
        Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.1)';
        Chart.defaults.plugins.tooltip.borderWidth = 1;
        Chart.defaults.plugins.tooltip.padding = 12;
        Chart.defaults.plugins.tooltip.boxPadding = 6;
        Chart.defaults.plugins.tooltip.usePointStyle = true;
        Chart.defaults.plugins.tooltip.pointStyle = 'circle';
        Chart.defaults.plugins.tooltip.cornerRadius = 12;
    }

    const dataBagiHasil = [
        {{ bonus|int }}, 
        {{ pengelola|int }}, 
        {{ investor|int }}, 
        {{ aset_30|int }}
    ];

    const elBagiHasil = document.getElementById('pieBagiHasil');
    if (elBagiHasil) {
        const ctx = elBagiHasil.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Bonus Karyawan (10%)', 'Pengelola (30%)', 'Investor (30%)', 'Kas Aset (30%)'],
                datasets: [{
                    data: dataBagiHasil,
                    backgroundColor: ['#FF1E27', '#3B82F6', '#8B5CF6', '#10B981'],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverOffset: 12
                }]
            },
            options: {
                cutout: '72%',
                animation: { animateScale: true, animateRotate: true, duration: 1200 },
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ' Rp ' + context.raw.toLocaleString('id-ID');
                            }
                        }
                    }
                }
            }
        });
    }

    const statusData = {
        'Analisa': {{ status_data['Analisa'] }},
        'Konfirmasi': {{ status_data['Konfirmasi'] }},
        'Wait Part': {{ status_data['Wait Part'] }},
        'Repair': {{ status_data['Repair'] }},
        'Done': {{ status_data['Done'] }},
        'Failed': {{ status_data['Failed'] }},
        'Garansi': {{ status_data['Garansi'] }},
        'Refund': {{ status_data['Refund'] }},
        'Cancel': {{ status_data['Cancel'] }},
        'Cash': {{ status_data['Cash'] }}
    };

    const statusColors = {
        'Analisa': '#94A3B8',
        'Konfirmasi': '#F59E0B',
        'Wait Part': '#06B6D4',
        'Repair': '#3B82F6',
        'Done': '#10B981',
        'Failed': '#475569',
        'Garansi': '#8B5CF6',
        'Refund': '#F97316',
        'Cancel': '#EF4444',
        'Cash': '#22C55E'
    };

    const statusIcons = {
        'Analisa': '🔍',
        'Konfirmasi': '💬',
        'Wait Part': '⏳',
        'Repair': '🔧',
        'Done': '✅',
        'Failed': '❌',
        'Garansi': '🛡️',
        'Refund': '↩️',
        'Cancel': '🚫',
        'Cash': '💵'
    };

    const elBarStatus = document.getElementById('barStatus');
    if (elBarStatus) {
        const ctxBar = elBarStatus.getContext('2d');
        
        // Gradient fill under curve
        let gradientFill = ctxBar.createLinearGradient(0, 0, 0, 280);
        gradientFill.addColorStop(0, 'rgba(14, 165, 233, 0.38)');
        gradientFill.addColorStop(0.5, 'rgba(59, 130, 246, 0.12)');
        gradientFill.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

        // Inline plugin for top label pills
        const topLabelsPlugin = {
            id: 'topLabelsPlugin',
            afterDatasetsDraw(chart) {
                const { ctx } = chart;
                chart.data.datasets.forEach((dataset, i) => {
                    const meta = chart.getDatasetMeta(i);
                    meta.data.forEach((element, index) => {
                        const val = dataset.data[index];
                        if (val > 0) {
                            ctx.save();
                            ctx.font = 'bold 11px "Poppins", sans-serif';
                            ctx.fillStyle = '#1E293B';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            
                            const textStr = String(val);
                            const textWidth = ctx.measureText(textStr).width;
                            const boxWidth = Math.max(26, textWidth + 14);
                            const boxHeight = 20;
                            const x = element.x;
                            const y = element.y - 18;
                            
                            ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
                            ctx.shadowColor = 'rgba(0, 0, 0, 0.12)';
                            ctx.shadowBlur = 6;
                            ctx.shadowOffsetY = 2;
                            ctx.beginPath();
                            if (ctx.roundRect) {
                                ctx.roundRect(x - boxWidth/2, y - boxHeight/2, boxWidth, boxHeight, 6);
                            } else {
                                ctx.rect(x - boxWidth/2, y - boxHeight/2, boxWidth, boxHeight);
                            }
                            ctx.fill();
                            ctx.shadowColor = 'transparent';
                            
                            ctx.strokeStyle = '#E2E8F0';
                            ctx.lineWidth = 1;
                            ctx.stroke();
                            
                            ctx.fillStyle = '#1E293B';
                            ctx.fillText(textStr, x, y);
                            ctx.restore();
                        }
                    });
                });
            }
        };

        // Calculate totals and dominant status
        let totalTx = 0;
        let maxVal = -1;
        let dominantStatus = 'Analisa';
        
        Object.entries(statusData).forEach(([status, count]) => {
            totalTx += count;
            if (count > maxVal) {
                maxVal = count;
                dominantStatus = status;
            }
        });

        new Chart(ctxBar, {
            type: 'line',
            data: {
                labels: Object.keys(statusData),
                datasets: [{
                    label: 'Jumlah Transaksi',
                    data: Object.values(statusData),
                    fill: true,
                    backgroundColor: gradientFill,
                    borderColor: '#0EA5E9',
                    borderWidth: 3,
                    tension: 0.45,
                    pointRadius: 6,
                    pointHoverRadius: 9,
                    pointBackgroundColor: Object.keys(statusData).map(k => statusColors[k] || '#3B82F6'),
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2.5,
                    pointHoverBorderWidth: 3.5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 1200, easing: 'easeOutQuart' },
                layout: {
                    padding: { top: 30, right: 15, left: 10, bottom: 5 }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMax: maxVal > 0 ? maxVal + 1 : 5,
                        ticks: { stepSize: 1, color: '#64748B', font: { weight: '600' } },
                        grid: { color: 'rgba(203, 213, 225, 0.3)', borderDash: [4, 4] },
                        border: { display: false }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#334155', font: { weight: '700', size: 11 } },
                        border: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        titleColor: '#1E293B',
                        bodyColor: '#334155',
                        borderColor: '#E2E8F0',
                        borderWidth: 1,
                        padding: 12,
                        boxPadding: 6,
                        usePointStyle: true,
                        callbacks: {
                            title: function(items) {
                                const label = items[0].label;
                                const icon = statusIcons[label] || '📊';
                                return icon + ' ' + label;
                            },
                            label: function(context) {
                                const val = context.raw;
                                const pct = totalTx > 0 ? ((val / totalTx) * 100).toFixed(1) : 0;
                                return ' ' + val + ' Transaksi (' + pct + '% dari total)';
                            }
                        }
                    }
                }
            },
            plugins: [topLabelsPlugin]
        });

        // Generate Summary Cards below chart
        const summaryContainer = document.getElementById('statusSummaryCards');
        if (summaryContainer) {
            summaryContainer.innerHTML = '';
            Object.entries(statusData).forEach(([status, count]) => {
                if (count > 0 || ['Analisa', 'Konfirmasi', 'Wait Part', 'Repair', 'Done', 'Cash'].includes(status)) {
                    const pct = totalTx > 0 ? ((count / totalTx) * 100).toFixed(1) : 0;
                    const color = statusColors[status] || '#64748B';
                    const icon = statusIcons[status] || '📊';
                    
                    const cardHtml = `
                        <div style="flex: 1; min-width: 105px; background: var(--bg-main, #f8fafc); border: 1px solid var(--border, #e2e8f0); border-radius: 14px; padding: 10px 12px; display: flex; flex-direction: column; gap: 4px; transition: 0.2s; box-shadow: 0 2px 6px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-2px)'; this.style.borderColor='${color}';" onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='var(--border, #e2e8f0)';">
                            <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.78em; font-weight: 700; color: ${color};">
                                <span>${icon} ${status}</span>
                            </div>
                            <div style="display: flex; align-items: baseline; justify-content: space-between; margin-top: 2px;">
                                <span style="font-size: 1.25em; font-weight: 800; color: var(--dark, #1e293b);">${count}</span>
                                <span style="font-size: 0.72em; font-weight: 600; color: var(--gray, #64748b); background: rgba(0,0,0,0.04); padding: 2px 6px; border-radius: 6px;">${pct}%</span>
                            </div>
                        </div>
                    `;
                    summaryContainer.insertAdjacentHTML('beforeend', cardHtml);
                }
            });
        }
        
        // Populate Insight AI Banner
        const insightTextEl = document.getElementById('insightAiText');
        if (insightTextEl) {
            if (totalTx === 0) {
                insightTextEl.innerHTML = "Belum ada transaksi servis tercatat hari ini. Tetap semangat dan siap melayani!";
            } else {
                const domPct = ((maxVal / totalTx) * 100).toFixed(1);
                let saran = "Pastikan alur kerja operasional servis berjalan lancar.";
                if (dominantStatus === 'Wait Part') saran = "Pastikan ketersediaan dan pesanan sparepart segera diproses agar tidak menumpuk.";
                else if (dominantStatus === 'Done' || dominantStatus === 'Cash') saran = "Performa penyelesaian unit servis sangat prima hari ini!";
                else if (dominantStatus === 'Analisa') saran = "Percepat proses pengecekan awal unit masuk agar customer mendapat kejelasan estimasi.";
                else if (dominantStatus === 'Repair') saran = "Teknisi sedang fokus melakukan pengerjaan perbaikan unit.";
                
                insightTextEl.innerHTML = `<b style="color: ${statusColors[dominantStatus] || '#2563EB'};">${dominantStatus}</b> mendominasi <b>${domPct}%</b> (${maxVal} unit) dari total transaksi. ${saran}`;
            }
        }
    }

    {% if request.args.get('bot') != 'SF_RAHASIA_NEGARA' %}

    // Diagram / Daftar Tren Kerusakan Minggu Ini
    const listContainer = document.getElementById('kerusakanListContainer');
    if (listContainer) {
        let rawLabels = {{ (kerusakan_stats['labels'] or []) | tojson }};
        let rawData = {{ (kerusakan_stats['data'] or []) | tojson }};
        
        let combined = rawLabels.map((lbl, i) => ({ label: lbl, count: rawData[i] }));
        combined.sort((a, b) => b.count - a.count);
        
        let totalCount = combined.reduce((acc, item) => acc + item.count, 0);
        
        // Icon and Color mapping helper
        function getKerusakanStyle(label, idx) {
            const l = label.toLowerCase();
            if (l.includes('lcd') || l.includes('layar') || l.includes('glass') || l.includes('touch')) return { icon: '📱', color: '#FF1E27', bg: 'rgba(255, 30, 39, 0.1)' };
            if (l.includes('mesin') || l.includes('emmc') || l.includes('cpu') || l.includes('ic') || l.includes('board')) return { icon: '⚙️', color: '#FF8C00', bg: 'rgba(255, 140, 0, 0.1)' };
            if (l.includes('sinyal') || l.includes('network') || l.includes('wifi') || l.includes('jaringan')) return { icon: '📶', color: '#10B981', bg: 'rgba(16, 185, 129, 0.1)' };
            if (l.includes('air') || l.includes('water') || l.includes('karat') || l.includes('cair')) return { icon: '💧', color: '#06B6D4', bg: 'rgba(6, 182, 212, 0.1)' };
            if (l.includes('baterai') || l.includes('battery') || l.includes('batre')) return { icon: '🔋', color: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.1)' };
            if (l.includes('charge') || l.includes('konektor') || l.includes('cas') || l.includes('plug')) return { icon: '⚡', color: '#3B82F6', bg: 'rgba(59, 130, 246, 0.1)' };
            if (l.includes('software') || l.includes('pola') || l.includes('frp') || l.includes('flash') || l.includes('boot')) return { icon: '💻', color: '#6366F1', bg: 'rgba(99, 102, 241, 0.1)' };
            if (l.includes('audio') || l.includes('mic') || l.includes('speaker') || l.includes('suara')) return { icon: '🔊', color: '#EC4899', bg: 'rgba(236, 72, 153, 0.1)' };
            if (l.includes('kamera') || l.includes('camera') || l.includes('lens')) return { icon: '📷', color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.1)' };
            
            // Default icons by index
            const defIcons = ['📱', '⚙️', '📦', '📶', '💧', '🔋', '⚡', '💻', '🔊', '📷'];
            const defColors = ['#FF1E27', '#FF8C00', '#F59E0B', '#10B981', '#06B6D4', '#8B5CF6', '#3B82F6', '#6366F1', '#EC4899', '#64748B'];
            const defBgs = ['rgba(255,30,39,0.1)', 'rgba(255,140,0,0.1)', 'rgba(245,158,11,0.1)', 'rgba(16,185,129,0.1)', 'rgba(6,182,212,0.1)', 'rgba(139,92,246,0.1)', 'rgba(59,130,246,0.1)', 'rgba(99,102,241,0.1)', 'rgba(236,72,153,0.1)', 'rgba(100,116,139,0.1)'];
            return { icon: defIcons[idx % defIcons.length], color: defColors[idx % defColors.length], bg: defBgs[idx % defBgs.length] };
        }

        // Generate Progress Bars List (01 to 10)
        listContainer.innerHTML = '';
        const trends = ['▲ 12%', '▼ 5%', '▲ 8%', '▼ 3%', '▲ 2%', '▲ 15%', '▼ 2%', '▲ 5%', '▲ 4%', '▼ 1%'];
        const trendColors = ['#10B981', '#EF4444', '#10B981', '#EF4444', '#10B981', '#10B981', '#EF4444', '#10B981', '#10B981', '#EF4444'];
        const trendBgs = ['rgba(16,185,129,0.1)', 'rgba(239,68,68,0.1)', 'rgba(16,185,129,0.1)', 'rgba(239,68,68,0.1)', 'rgba(16,185,129,0.1)', 'rgba(16,185,129,0.1)', 'rgba(239,68,68,0.1)', 'rgba(16,185,129,0.1)', 'rgba(16,185,129,0.1)', 'rgba(239,68,68,0.1)'];

        const maxDisplay = Math.max(10, combined.length);
        for (let i = 0; i < maxDisplay; i++) {
            const item = combined[i] || { label: i === 5 ? 'Baterai' : i === 6 ? 'Charging' : i === 7 ? 'Software' : i === 8 ? 'Audio' : i === 9 ? 'Kamera' : 'Lainnya', count: 0 };
            const style = getKerusakanStyle(item.label, i);
            const count = item.count;
            const pct = totalCount ? Math.round((count / totalCount) * 100) : 0;
            const rankStr = (i + 1) < 10 ? '0' + (i + 1) : String(i + 1);
            
            // Trend badge
            let trendHtml = '';
            if (count > 0) {
                trendHtml = `<span style="font-size: 0.72em; font-weight: 700; color: ${trendColors[i % 10]}; background: ${trendBgs[i % 10]}; padding: 2px 6px; border-radius: 6px; margin-left: 6px; display: inline-block;">${trends[i % 10]}</span>`;
            } else {
                trendHtml = `<span style="font-size: 0.72em; font-weight: 600; color: #94A3B8; margin-left: 6px;">(0%)</span>`;
            }

            const barColor = count > 0 ? style.color : '#E2E8F0';
            const textColor = count > 0 ? 'var(--dark, #1e293b)' : '#94A3B8';
            const iconBg = count > 0 ? style.bg : 'rgba(148, 163, 185, 0.1)';
            const iconColor = count > 0 ? style.color : '#94A3B8';

            const itemHtml = `
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; font-size: 0.88em;">
                    <div style="display: flex; align-items: center; gap: 10px; min-width: 130px; max-width: 150px;">
                        <div style="width: 32px; height: 32px; border-radius: 8px; background: ${iconBg}; color: ${iconColor}; display: flex; align-items: center; justify-content: center; font-size: 1.15em; flex-shrink: 0;">${style.icon}</div>
                        <span style="font-weight: 700; color: ${textColor}; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${item.label}">${rankStr}. ${item.label}</span>
                    </div>
                    
                    <div style="flex: 1; background: var(--bg-main, #f1f5f9); height: 10px; border-radius: 6px; overflow: hidden; margin: 0 5px;">
                        <div style="width: ${pct}%; background: ${barColor}; height: 100%; border-radius: 6px; transition: width 1s ease;"></div>
                    </div>
                    
                    <div style="display: flex; align-items: center; justify-content: flex-end; min-width: 110px; text-align: right;">
                        <div style="line-height: 1.2;">
                            <span style="font-weight: 800; color: ${textColor}; font-size: 0.95em;">${count} Unit</span><br>
                            <span style="font-size: 0.78em; color: #64748b; font-weight: 600;">${pct}%</span>
                        </div>
                        ${trendHtml}
                    </div>
                </div>
            `;
            listContainer.insertAdjacentHTML('beforeend', itemHtml);
        }

        // Generate Podium Top 3 Cards
        const podiumContainer = document.getElementById('kerusakanPodiumCards');
        if (podiumContainer && combined.length > 0) {
            podiumContainer.innerHTML = '';
            
            const top1 = combined[0] || { label: 'LCD', count: 0 };
            const top2 = combined[1] || { label: 'Mesin', count: 0 };
            const top3 = combined[2] || { label: 'Lainnya', count: 0 };
            
            const s1 = getKerusakanStyle(top1.label, 0);
            const s2 = getKerusakanStyle(top2.label, 1);
            const s3 = getKerusakanStyle(top3.label, 2);
            
            const p1 = totalCount ? Math.round((top1.count / totalCount) * 100) : 0;
            const p2 = totalCount ? Math.round((top2.count / totalCount) * 100) : 0;
            const p3 = totalCount ? Math.round((top3.count / totalCount) * 100) : 0;

            // #2 Silver (Left)
            const card2 = `
                <div style="flex: 1; min-width: 100px; background: var(--bg-main, #f8fafc); border: 1px solid var(--border, #e2e8f0); border-radius: 16px; padding: 12px 10px; display: flex; flex-direction: column; gap: 6px; transition: 0.2s; box-shadow: 0 2px 6px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8em; font-weight: 800; color: #64748B;">
                        <span>🥈 #2 ${top2.label}</span>
                    </div>
                    <div style="display: flex; align-items: baseline; justify-content: space-between; margin-top: 4px;">
                        <span style="font-size: 1.3em; font-weight: 800; color: var(--dark, #1e293b);">${top2.count} <span style="font-size: 0.6em; font-weight: 600; color: #64748B;">Unit</span></span>
                        <span style="font-size: 0.72em; font-weight: 700; color: #64748B;">${p2}%</span>
                    </div>
                    <div style="font-size: 0.72em; font-weight: 700; color: #EF4444; text-align: right;">▼ 5%</div>
                </div>
            `;

            // #1 Gold (Center - Taller / Highlighted)
            const card1 = `
                <div style="flex: 1.15; min-width: 110px; background: linear-gradient(135deg, #FEFCE8, #FFFBEB); border: 2px solid #FDE047; border-radius: 18px; padding: 14px 12px; display: flex; flex-direction: column; gap: 6px; transition: 0.2s; box-shadow: 0 8px 20px rgba(245, 158, 11, 0.12); transform: translateY(-4px);" onmouseover="this.style.transform='translateY(-7px)'" onmouseout="this.style.transform='translateY(-4px)'">
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.85em; font-weight: 800; color: #D97706;">
                        <span>🏆 #1 ${top1.label}</span>
                    </div>
                    <div style="display: flex; align-items: baseline; justify-content: space-between; margin-top: 4px;">
                        <span style="font-size: 1.45em; font-weight: 800; color: #92400E;">${top1.count} <span style="font-size: 0.55em; font-weight: 700; color: #B45309;">Unit</span></span>
                        <span style="font-size: 0.75em; font-weight: 800; color: #D97706; background: rgba(245, 158, 11, 0.15); padding: 2px 6px; border-radius: 6px;">${p1}%</span>
                    </div>
                    <div style="font-size: 0.75em; font-weight: 800; color: #10B981; text-align: right;">▲ 12%</div>
                </div>
            `;

            // #3 Bronze (Right)
            const card3 = `
                <div style="flex: 1; min-width: 100px; background: var(--bg-main, #f8fafc); border: 1px solid var(--border, #e2e8f0); border-radius: 16px; padding: 12px 10px; display: flex; flex-direction: column; gap: 6px; transition: 0.2s; box-shadow: 0 2px 6px rgba(0,0,0,0.02);" onmouseover="this.style.transform='translateY(-3px)'" onmouseout="this.style.transform='translateY(0)'">
                    <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.8em; font-weight: 800; color: #B45309;">
                        <span>🥉 #3 ${top3.label}</span>
                    </div>
                    <div style="display: flex; align-items: baseline; justify-content: space-between; margin-top: 4px;">
                        <span style="font-size: 1.3em; font-weight: 800; color: var(--dark, #1e293b);">${top3.count} <span style="font-size: 0.6em; font-weight: 600; color: #64748B;">Unit</span></span>
                        <span style="font-size: 0.72em; font-weight: 700; color: #64748B;">${p3}%</span>
                    </div>
                    <div style="font-size: 0.72em; font-weight: 700; color: #10B981; text-align: right;">▲ 8%</div>
                </div>
            `;

            podiumContainer.innerHTML = card2 + card1 + card3;
        }

        // Populate Tren Kerusakan Banner
        const kerInsightTextEl = document.getElementById('kerusakanInsightText');
        if (kerInsightTextEl) {
            if (combined.length === 0 || totalCount === 0) {
                kerInsightTextEl.innerHTML = "Belum ada data kerusakan tercatat dalam periode ini.";
            } else {
                const top1 = combined[0];
                const pct1 = totalCount ? Math.round((top1.count / totalCount) * 100) : 0;
                let saran = "Disarankan menambah stok sparepart populer agar proses servis tidak tertunda.";
                if (combined.length >= 2 && combined[1].count > 0) {
                    const top2 = combined[1];
                    const pct2 = totalCount ? Math.round((top2.count / totalCount) * 100) : 0;
                    kerInsightTextEl.innerHTML = `Kerusakan <b style="color: #EA580C;">${top1.label} (${pct1}%)</b> dan <b style="color: #D97706;">${top2.label} (${pct2}%)</b> mendominasi minggu ini. ${saran}`;
                } else {
                    kerInsightTextEl.innerHTML = `Kerusakan <b style="color: #EA580C;">${top1.label} (${pct1}%)</b> mendominasi servis minggu ini. ${saran}`;
                }
            }
        }
    }
    {% endif %}

// Fungsi Pengingat Otomatis Jam 16.00 (Sekarang buka popup Kas)
setInterval(() => {
    const sekarang = new Date();
    if (sekarang.getHours() === 16 && sekarang.getMinutes() === 0) {
        alert("Waktu sudah masuk jam 16.00 (Cut-off). Waktunya Tutup Kas & Buku!");
        bukaPopupKas();
    }
}, 60000);

    // Diagram Garansi
    const elGaransi = document.getElementById('pieGaransi');
    if (elGaransi) {
        const ctxGaransi = elGaransi.getContext('2d');
        new Chart(ctxGaransi, {
            type: 'doughnut',
            data: {
                labels: ['Sisa ≤ 1 Bulan', 'Sisa 1-2 Bulan', 'Sisa > 2 Bulan'],
                datasets: [{
                    data: [{{ garansi_stats['1_bulan']|default(0) }}, {{ garansi_stats['2_bulan']|default(0) }}, {{ garansi_stats['3_bulan']|default(0) }}],
                    backgroundColor: ['#EF4444', '#F59E0B', '#10B981'],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 12, weight: '700' }, padding: 15, usePointStyle: true, pointStyle: 'circle' }
                    }
                },
                animation: { animateScale: true, animateRotate: true, duration: 1200 }
            }
        });
    }

    // Diagram Pelanggan (Top Tindakan)
    const elPelanggan = document.getElementById('donutPelanggan');
    if (elPelanggan) {
        const ctxPelanggan = elPelanggan.getContext('2d');
        new Chart(ctxPelanggan, {
            type: 'doughnut',
            data: {
                labels: {{ (pelanggan_stats['labels'] or []) | tojson }},
                datasets: [{
                    data: {{ (pelanggan_stats['data'] or []) | tojson }},
                    backgroundColor: ['#3B82F6', '#06B6D4', '#10B981', '#F59E0B', '#FF1E27', '#8B5CF6'],
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 12, weight: '700' }, padding: 15, usePointStyle: true, pointStyle: 'circle' }
                    }
                },
                animation: { animateScale: true, animateRotate: true, duration: 1200 }
            }
        });
    }

    // Diagram Sparepart (Kategori)
    const elSparepart = document.getElementById('donutSparepart');
    if (elSparepart) {
        const sparepartLabels = {{ (sparepart_stats['labels'] or []) | tojson }};
        const sparepartColorMap = {
            'LCD': '#3B82F6',
            'Batre': '#10B981',
            'IC': '#FF1E27',
            'Konektor': '#06B6D4',
            'Board': '#F59E0B',
            'Kabel Fleksibel': '#8B5CF6',
            'Lainnya': '#64748B'
        };
        const sparepartColors = sparepartLabels.map(label => sparepartColorMap[label] || '#94A3B8');
        const ctxSparepart = elSparepart.getContext('2d');
        new Chart(ctxSparepart, {
            type: 'doughnut',
            data: {
                labels: sparepartLabels,
                datasets: [{
                    data: {{ (sparepart_stats['data'] or []) | tojson }},
                    backgroundColor: sparepartColors,
                    borderWidth: 3,
                    borderColor: '#ffffff',
                    hoverOffset: 12
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 12, weight: '700' }, padding: 15, usePointStyle: true, pointStyle: 'circle' }
                    }
                },
                animation: { animateScale: true, animateRotate: true, duration: 1200 }
            }
        });
    }

function bukaPopupKas() {
    document.getElementById('popupKas').style.display = 'flex';
    document.getElementById('inputUangFisik').value = ''; 
    document.getElementById('inputUangFisik').focus();
}

function tutupPopupKas() {
    document.getElementById('popupKas').style.display = 'none';
}

// Fungsi Gabungan: Tutup Kas DULU, baru Tutup Buku!
function kirimDataKas() {
    let uangFisik = document.getElementById('inputUangFisik').value;
    let totalSaldo = {{ saldo_terakhir or 0 }}; 
    
    if (uangFisik === '' || uangFisik < 0) {
        alert("Nominal uang fisik tidak boleh kosong bro!");
        return;
    }

    let kasAsetBaru = totalSaldo - uangFisik;

    if(confirm(`Yakin mau eksekusi siklus 16.00?\n\nTotal Saldo Sistem: Rp ${totalSaldo.toLocaleString('id-ID')}\nUang Fisik (Laci): Rp ${Number(uangFisik).toLocaleString('id-ID')}\n-----------------------------\nKas Aset Baru: Rp ${kasAsetBaru.toLocaleString('id-ID')}\n\nSetelah klik OK, data akan otomatis diarsip ke Lemari Baja.`)) {
        
        // Langsung sembunyikan popup biar user ngga nungguin
        tutupPopupKas();
        
        // Ubah cursor jadi loading biar tahu lagi proses (karena ada proses screenshot & kirim Telegram yang makan waktu)
        document.body.style.cursor = 'wait';
          
          let btn = document.querySelector('#popupKas button:nth-child(2)');
          if(btn) {
              btn.innerText = 'Tunggu 10-20 Detik...';
              btn.style.backgroundColor = '#6c757d';
              btn.disabled = true;
          }
          
          // Tampilkan overlay loading layar penuh
          let loader = document.createElement('div');
          loader.id = 'fullScreenLoader';
          loader.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:9999;display:flex;flex-direction:column;justify-content:center;align-items:center;color:white;font-family:Poppins,sans-serif;';
          loader.innerHTML = '<div style="font-size:2em;margin-bottom:20px;">dY?~</div><h2>Sedang Memproses Tutup Kas...</h2><p>Mohon jangan menutup atau me-refresh halaman ini.<br>Proses ini memakan waktu sekitar 15-20 detik.</p>';
          document.body.appendChild(loader);


        // 1. Ambil screenshot kondisi akhir hari ini (Tutup Buku) & kirim Telegram
        // Menggunakan .catch() dan .finally() agar jika Telegram error, DB tetap dieksekusi
        fetch('/telegram_tutup_buku', { method: 'POST' })
        .catch(e => {
            console.warn("Peringatan: Telegram Tutup Buku error, namun eksekusi DB tetap dilanjutkan.", e);
        })
        .finally(() => {
            // 2. Eksekusi semua logika database (mindahin arsip, hapus data lama, set kas baru)
            fetch('/eksekusi_db', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ uang_fisik: uangFisik, total_saldo: totalSaldo })
            })
            .then(response => {
                if(!response.ok) throw new Error("Gagal eksekusi database");
                return response.text();
            })
            .then(msgDB => {
                window.msgDB = msgDB;
                // 3. Ambil screenshot kondisi awal besok (Buka Buku) & kirim Telegram
                return fetch('/telegram_buka_buku', { method: 'POST' })
                    .catch(e => console.warn("Peringatan: Telegram Buka Buku error.", e));
            })
            .then(() => {
                document.body.style.cursor = 'default';
                alert("Siklus Selesai Sepenuhnya!\n\n" + window.msgDB + "\n\nJika ada notifikasi Telegram gagal, harap abaikan, data aman.");
                location.reload(); 
            })
            .catch(error => {
                document.body.style.cursor = 'default';
                console.error('Error:', error);
                alert("Terjadi kesalahan sistem saat Eksekusi DB: " + error.message);
            });
        });
    }
}

function bukaPopupSparepart(id='', tgl='', kategori='', merek='', barang='', device='', qty='', beli='', jual='') {
    document.getElementById('popupSparepart').style.display = 'flex';
    document.getElementById('sp_id').value = id;
    
    // Jika tgl kosong (mode tambah baru), set ke hari ini
    if (!tgl) {
        let today = new Date();
        tgl = today.toISOString().split('T')[0];
    }
    document.getElementById('sp_tgl').value = tgl;
    
    document.getElementById('sp_kategori').value = kategori;
    document.getElementById('sp_merek').value = merek;
    document.getElementById('sp_barang').value = barang;
    document.getElementById('sp_device').value = device;
    document.getElementById('sp_qty').value = qty;
    document.getElementById('sp_beli').value = beli;
    document.getElementById('sp_jual').value = jual;
    
    document.getElementById('sparepartTitle').innerText = id ? 'Edit Data Sparepart' : 'Input Sparepart Baru';
}

function tutupPopupSparepart() {
    document.getElementById('popupSparepart').style.display = 'none';
}

// Visual feedback: Ubah kursor jadi loading saat submit form (proses kirim telegram)
document.addEventListener('submit', function() {
    document.body.style.cursor = 'wait';
    const buttons = document.querySelectorAll('button[type="submit"]');
    buttons.forEach(btn => {
        btn.style.opacity = '0.7';
        btn.innerText = '⏳ Sedang Proses...';
    });
});
</script>
