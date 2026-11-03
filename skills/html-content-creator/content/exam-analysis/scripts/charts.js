const examLabels = {exam_labels_json};
const examAxisLabels = {exam_axis_labels_json};
const chartGroups = {chart_groups_json};
const examNames = {exam_names_json};
const examFileNames = {exam_file_names_json};
const allStats = {all_stats_json};
let totalGroups = {total_groups};

let charts = [];
let currentView = 'chart';
let currentExamIndex = -1;
let searchTerm = '';

const allChartData = JSON.parse(JSON.stringify(chartGroups));
const COLORS = ['#5B8DEF', '#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181',
    '#AA96DA', '#FCBAD3', '#A8D8EA', '#FF9F43', '#6C5CE7',
    '#00CEC9', '#FD79A8', '#74B9FF', '#55EFC4', '#FDCB6E',
    '#E17055', '#00B894', '#636E72', '#B2BEC3', '#DFE6E9',
    '#74B9FF', '#A29BFE', '#FD79A8', '#FAB1A0', '#81ECEC'];

document.addEventListener('DOMContentLoaded', function() {
    initExamList();
    initCharts();
    initSearch();
});

function initExamList() {
    const container = document.getElementById('examList');
    examNames.forEach((name, index) => {
        const item = document.createElement('div');
        item.className = 'exam-item';
        item.textContent = examFileNames[index];
        item.title = name;
        item.onclick = () => switchToExam(index);
        container.appendChild(item);
    });
}

function showChartView() {
    currentView = 'chart';
    document.getElementById('chartView').classList.add('active');
    document.getElementById('tableView').classList.remove('active');
    document.getElementById('chartTab').classList.add('active');
    document.querySelectorAll('.exam-item').forEach(item => item.classList.remove('active'));
}

function switchToExam(index) {
    currentView = 'table';
    currentExamIndex = index;
    document.getElementById('chartView').classList.remove('active');
    document.getElementById('tableView').classList.add('active');
    document.getElementById('chartTab').classList.remove('active');
    document.querySelectorAll('.exam-item').forEach((item, i) => {
        item.classList.toggle('active', i === index);
    });
    document.getElementById('currentExamTitle').innerHTML = examNames[index] + '（' + examFileNames[index] + '）统计表格';
    renderTables(index);
}

function initCharts() {
    renderChartGroups(chartGroups);
}

function renderChartGroups(groupsData) {
    // 销毁旧图表
    charts.forEach(c => {
        try { if (c.scoreChart) c.scoreChart.destroy(); } catch(e) {}
        try { if (c.rankChart) c.rankChart.destroy(); } catch(e) {}
    });
    charts = [];

    const container = document.getElementById('chartsContainer');
    container.innerHTML = '';

    groupsData.forEach((group, groupIdx) => {
        const groupDiv = document.createElement('div');
        groupDiv.className = 'chart-group';
        groupDiv.innerHTML = `<div class="chart-group-title">第${groupIdx + 1}组（共${groupsData.length}组）</div>`;

        const chartsDiv = document.createElement('div');
        chartsDiv.className = 'charts-container';

        // 总分图
        const scoreWrapper = document.createElement('div');
        scoreWrapper.className = 'chart-wrapper';
        scoreWrapper.innerHTML = '<h4 class="chart-title">总分变化折线图</h4><canvas id="scoreChart' + groupIdx + '"></canvas>';
        chartsDiv.appendChild(scoreWrapper);

        // 名次图
        const rankWrapper = document.createElement('div');
        rankWrapper.className = 'chart-wrapper';
        rankWrapper.innerHTML = '<h4 class="chart-title">总分名次变化折线图（向上=进步）</h4><canvas id="rankChart' + groupIdx + '"></canvas>';
        chartsDiv.appendChild(rankWrapper);

        groupDiv.appendChild(chartsDiv);
        container.appendChild(groupDiv);

        // 初始化图表
        setTimeout(() => {
            initGroupCharts(groupIdx, group.datasets);
        }, 100);
    });
}

function initGroupCharts(groupIdx, datasets) {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: 'rgba(0,0,0,0.8)',
                titleFont: { size: 13 },
                bodyFont: { size: 12 },
                padding: 12,
                cornerRadius: 8,
                itemSort: function(a, b) {
                    var isScore = a.chart.canvas.id.startsWith('scoreChart');
                    if (isScore) {
                        return b.parsed.y - a.parsed.y;
                    } else {
                        return a.parsed.y - b.parsed.y;
                    }
                },
                callbacks: {
                    title: function(items) {
                        if (items.length > 0) {
                            return examAxisLabels[items[0].dataIndex].split('\n');
                        }
                        return '';
                    },
                    label: function(context) {
                        var name = context.dataset.label;
                        var value = context.parsed.y;
                        if (value === null) return null;
                        if (context.chart.canvas.id.startsWith('scoreChart')) {
                            return name + ': ' + value + '分';
                        } else {
                            return name + ': ' + value + '名';
                        }
                    }
                }
            },
        },
        scales: {
            x: {
                grid: { color: '#f0f0f0' },
                ticks: {
                    font: { size: 11 },
                    callback: function(value, index) {
                        return examAxisLabels[index].split('\n');
                    }
                }
            },
            y: { grid: { color: '#f0f0f0' }, ticks: { font: { size: 11 } } }
        }
    };

    // 总分图表
    const scoreCtx = document.getElementById('scoreChart' + groupIdx).getContext('2d');
    const scoreChart = new Chart(scoreCtx, {
        type: 'line',
        data: {
            labels: examAxisLabels,
            datasets: datasets.map(d => ({
                label: d.name,
                data: d.total_scores,
                borderColor: d.color,
                backgroundColor: d.color + '20',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: d.color,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }))
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    min: 450,
                    max: 700,
                    title: { display: true, text: '总分' }
                }
            }
        }
    });

    // 名次图表(反转)
    const rankCtx = document.getElementById('rankChart' + groupIdx).getContext('2d');
    const rankChart = new Chart(rankCtx, {
        type: 'line',
        data: {
            labels: examAxisLabels,
            datasets: datasets.map(d => ({
                label: d.name,
                data: d.total_ranks,
                borderColor: d.color,
                backgroundColor: d.color + '20',
                borderWidth: 2,
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: d.color,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }))
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    reverse: true,
                    title: { display: true, text: '名次（向上=进步）' }
                }
            }
        }
    });

    charts.push({ scoreChart, rankChart, datasets });

    // 添加图例
    const wrappers = document.querySelectorAll('.chart-wrapper');
    const scoreWrapper = wrappers[groupIdx * 2];
    const rankWrapper = wrappers[groupIdx * 2 + 1];
    addLegend(scoreWrapper, scoreChart);
    addLegend(rankWrapper, rankChart);
}

function addLegend(container, chart) {
    const legendDiv = document.createElement('div');
    legendDiv.className = 'chart-legend';
    chart.data.datasets.forEach((ds, i) => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        item.innerHTML = '<span class="legend-color" style="background:' + ds.borderColor + '"></span>' + ds.label;
        item.onclick = () => toggleDataset(chart, i, legendDiv);
        legendDiv.appendChild(item);
    });
    container.appendChild(legendDiv);
}

function toggleDataset(chart, index, legendDiv) {
    const meta = chart.getDatasetMeta(index);
    meta.hidden = !meta.hidden;
    chart.update();
    const items = legendDiv.querySelectorAll('.legend-item');
    items[index].style.opacity = meta.hidden ? '0.3' : '1';
}

function initSearch() {
    document.getElementById('searchBtn').addEventListener('click', function() {
        var term = document.getElementById('studentSearch').value.trim();
        if (!term) return;
        searchTerm = term.toLowerCase();
        searchCharts();
        document.getElementById('studentSearch').value = '';
    });

    document.getElementById('clearBtn').addEventListener('click', function() {
        document.getElementById('studentSearch').value = '';
        searchTerm = '';
        renderChartGroups(chartGroups);
    });
}

function searchCharts() {
    var matched = [];
    allChartData.forEach(function(group) {
        group.datasets.forEach(function(ds) {
            if (ds.name.toLowerCase().indexOf(searchTerm) !== -1) {
                matched.push(JSON.parse(JSON.stringify(ds)));
            }
        });
    });

    if (matched.length === 0) {
        renderChartGroups([]);
        return;
    }

    var filteredGroups = [];
    for (var i = 0; i < matched.length; i += 10) {
        var groupDatasets = matched.slice(i, i + 10);
        var datasets = groupDatasets.map(function(ds, j) {
            ds.color = COLORS[j % COLORS.length];
            return ds;
        });
        filteredGroups.push({
            group_index: Math.floor(i / 10),
            datasets: datasets
        });
    }
    renderChartGroups(filteredGroups);
}

function renderTables(examIndex) {
    const container = document.getElementById('tablesContainer');
    container.innerHTML = '';

    const examData = allStats.find(s => s.exam_index === examIndex);
    if (!examData) return;

    container.innerHTML = generateTablesHtml(examData.stats);
    initTableSort();
}

function generateTablesHtml(tables) {
    if (!tables || tables.length === 0) {
        return '<p style="text-align:center;color:#999;padding:40px;">暂无数据</p>';
    }
    return tables.map(table => {
        const tableId = 'table_' + table.id;
        const rows = table.rows || [];
        return '<div class="table-container" id="' + tableId + '"><h3 class="table-title">' + table.name + '</h3><div class="table-wrapper"><table class="data-table" data-table-id="' + tableId + '"><thead><tr><th data-sort-col="0">序号 <span class="sort-icon">&#9660;</span></th>' + (table.headers || []).map((h, i) => '<th data-sort-col="' + (i+1) + '">' + h + ' <span class="sort-icon">&#9660;</span></th>').join('') + '</tr></thead><tbody>' + generateAllRows(rows) + '</tbody></table></div></div>';
    }).join('');
}

function generateAllRows(rows) {
    return rows.map((row, idx) => {
        const cells = ['<td>' + (idx + 1) + '</td>'];
        row.forEach(cell => cells.push('<td>' + (cell !== null && cell !== undefined ? cell : '-') + '</td>'));
        return '<tr>' + cells.join('') + '</tr>';
    }).join('');
}

function initTableSort() {
    document.querySelectorAll('.data-table th[data-sort-col]').forEach(th => {
        th.addEventListener('click', function() {
            const table = th.closest('table');
            const colIndex = parseInt(th.dataset.sortCol);
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const isAsc = th.classList.contains('sorted-asc');
            document.querySelectorAll('#' + table.dataset.tableId + ' th').forEach(h => {
                h.classList.remove('sorted', 'sorted-asc', 'sorted-desc');
            });
            rows.sort((a, b) => {
                let aVal = a.cells[colIndex]?.textContent.trim() || '';
                let bVal = b.cells[colIndex]?.textContent.trim() || '';
                const aNum = parseFloat(aVal);
                const bNum = parseFloat(bVal);
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return isAsc ? aNum - bNum : bNum - aNum;
                }
                return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
            });
            th.classList.add('sorted', isAsc ? 'sorted-desc' : 'sorted-asc');
            th.querySelector('.sort-icon').textContent = isAsc ? '▲' : '▼';
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}


   