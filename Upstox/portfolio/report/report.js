// Initialize the report with the holdings data
document.addEventListener('DOMContentLoaded', function() {
    // Check if holdings data is available
    if (typeof holdingsData === 'undefined') {
        alert('Holdings data not found. Please run the generate_report.py script first.');
        return;
    }

    // Populate summary section
    populateSummary();
    
    // Populate holdings table
    populateHoldingsTable();
    
    // Create charts
    createAllocationChart();
    createPerformanceChart();
});

// Format currency values
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2
    }).format(value);
}

// Format percentage values
function formatPercentage(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'percent',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value / 100);
}

// Populate the summary section
function populateSummary() {
    const summary = holdingsData.summary;
    
    // Set the report date
    document.getElementById('date-value').textContent = summary.report_date;
    
    // Set the summary values
    document.getElementById('total-investment').textContent = formatCurrency(summary.total_investment);
    document.getElementById('current-value').textContent = formatCurrency(summary.total_current_value);
    document.getElementById('overall-pnl').textContent = formatCurrency(summary.total_pnl);
    
    const pnlPercentElement = document.getElementById('overall-pnl-percent');
    pnlPercentElement.textContent = `${summary.total_pnl_percent.toFixed(2)}%`;
    
    // Add positive/negative class based on P&L
    if (summary.total_pnl >= 0) {
        document.getElementById('overall-pnl').classList.add('positive');
        pnlPercentElement.classList.add('positive');
    } else {
        document.getElementById('overall-pnl').classList.add('negative');
        pnlPercentElement.classList.add('negative');
    }
    
    // Set holdings count
    document.getElementById('holdings-count').textContent = summary.holdings_count;
}

// Populate the holdings table
function populateHoldingsTable() {
    const tableBody = document.querySelector('#holdings-table tbody');
    const holdings = holdingsData.holdings;
    
    // Sort holdings by current value (descending)
    holdings.sort((a, b) => b.current_value - a.current_value);
    
    // Clear existing rows
    tableBody.innerHTML = '';
    
    // Add rows for each holding
    holdings.forEach(holding => {
        const row = document.createElement('tr');
        
        // Create cells
        row.innerHTML = `
            <td>${holding.symbol}</td>
            <td>${holding.company_name}</td>
            <td>${holding.quantity}</td>
            <td>${holding.avg_price.toFixed(2)}</td>
            <td>${holding.ltp.toFixed(2)}</td>
            <td>${holding.investment_value.toFixed(2)}</td>
            <td>${holding.current_value.toFixed(2)}</td>
            <td class="${holding.pnl >= 0 ? 'positive' : 'negative'}">${holding.pnl.toFixed(2)}</td>
            <td class="${holding.pnl_percent >= 0 ? 'positive' : 'negative'}">${holding.pnl_percent.toFixed(2)}%</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Create the portfolio allocation chart
function createAllocationChart() {
    const holdings = holdingsData.holdings;
    
    // Prepare data for the chart
    const labels = holdings.map(holding => holding.symbol);
    const data = holdings.map(holding => holding.current_value);
    
    // Get background colors based on P&L
    const backgroundColors = holdings.map(holding => {
        // Generate colors based on P&L percentage
        const pnlPercent = holding.pnl_percent;
        if (pnlPercent > 20) return '#4caf50';  // Strong positive
        if (pnlPercent > 0) return '#81c784';   // Positive
        if (pnlPercent > -10) return '#ffb74d'; // Small negative
        return '#e57373';                       // Strong negative
    });
    
    // Create the chart
    const ctx = document.getElementById('allocation-chart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: backgroundColors,
                borderColor: 'white',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 20,
                        boxWidth: 12
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                            const percentage = ((value / total) * 100).toFixed(2);
                            return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create the performance chart
function createPerformanceChart() {
    const holdings = holdingsData.holdings;
    
    // Sort holdings by P&L percentage
    const sortedHoldings = [...holdings].sort((a, b) => b.pnl_percent - a.pnl_percent);
    
    // Prepare data for the chart
    const labels = sortedHoldings.map(holding => holding.symbol);
    const investmentData = sortedHoldings.map(holding => holding.investment_value);
    const pnlData = sortedHoldings.map(holding => holding.pnl);
    
    // Create the chart
    const ctx = document.getElementById('performance-chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Investment Value',
                    data: investmentData,
                    backgroundColor: 'rgba(30, 136, 229, 0.7)',
                    borderColor: 'rgba(30, 136, 229, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Profit/Loss',
                    data: pnlData,
                    backgroundColor: sortedHoldings.map(holding => 
                        holding.pnl >= 0 ? 'rgba(76, 175, 80, 0.7)' : 'rgba(244, 67, 54, 0.7)'
                    ),
                    borderColor: sortedHoldings.map(holding => 
                        holding.pnl >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)'
                    ),
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        borderDash: [2, 4]
                    },
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value).replace('.00', '');
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.raw || 0;
                            return `${label}: ${formatCurrency(value)}`;
                        }
                    }
                }
            }
        }
    });
}