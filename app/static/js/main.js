/**
 * 給与管理アプリのグローバルJavaScript関数
 */

// 通貨フォーマット
function formatCurrency(value) {
    return new Intl.NumberFormat('ja-JP', {
        style: 'currency',
        currency: 'JPY'
    }).format(value);
}

// テーブルの並び替え機能
function setupTableSorting() {
    document.querySelectorAll('th[data-sort]').forEach(header => {
        header.addEventListener('click', () => {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(header.parentNode.children).indexOf(header);
            const direction = header.classList.contains('sort-asc') ? 'desc' : 'asc';
            
            // ソート方向の指定
            document.querySelectorAll('th').forEach(th => {
                th.classList.remove('sort-asc', 'sort-desc');
            });
            
            header.classList.add(`sort-${direction}`);
            
            // データ型に応じたソート関数
            const getValue = (row, index) => {
                const cell = row.querySelectorAll('td')[index];
                const rawValue = cell.textContent.trim();
                
                // 通貨フォーマットされた値（¥123,456）を数値に変換
                if (rawValue.startsWith('¥')) {
                    return parseFloat(rawValue.replace(/[¥,]/g, ''));
                }
                
                // 数値に変換可能であれば数値として比較
                const numValue = parseFloat(rawValue);
                return isNaN(numValue) ? rawValue.toLowerCase() : numValue;
            };
            
            // ソート実行
            rows.sort((a, b) => {
                const aValue = getValue(a, columnIndex);
                const bValue = getValue(b, columnIndex);
                
                if (typeof aValue === 'string' && typeof bValue === 'string') {
                    return direction === 'asc' 
                        ? aValue.localeCompare(bValue, 'ja') 
                        : bValue.localeCompare(aValue, 'ja');
                } else {
                    return direction === 'asc' ? aValue - bValue : bValue - aValue;
                }
            });
            
            // テーブル更新
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

// 年月選択によるフィルタリング
function setupYearMonthFilter() {
    const yearSelect = document.getElementById('year-filter');
    const monthSelect = document.getElementById('month-filter');
    
    if (!yearSelect || !monthSelect) return;
    
    function filterTable() {
        const yearValue = yearSelect.value;
        const monthValue = monthSelect.value;
        const rows = document.querySelectorAll('table tbody tr');
        
        rows.forEach(row => {
            const yearCell = row.querySelector('td[data-year]');
            const monthCell = row.querySelector('td[data-month]');
            
            if (!yearCell || !monthCell) return;
            
            const yearMatch = yearValue === 'all' || yearCell.dataset.year === yearValue;
            const monthMatch = monthValue === 'all' || monthCell.dataset.month === monthValue;
            
            row.style.display = (yearMatch && monthMatch) ? '' : 'none';
        });
    }
    
    yearSelect.addEventListener('change', filterTable);
    monthSelect.addEventListener('change', filterTable);
}

// DOMロード時の初期化
document.addEventListener('DOMContentLoaded', function() {
    // 各種機能の初期化
    setupTableSorting();
    setupYearMonthFilter();
    
    // ツールチップの初期化（Bootstrapのツールチップ）
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 印刷ボタンの機能
    const printButton = document.getElementById('print-button');
    if (printButton) {
        printButton.addEventListener('click', () => {
            window.print();
        });
    }
}); 