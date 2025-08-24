/**
 * Chart utilities for glucoAudio
 */

class GlucoCharts {
    /**
     * Initialize charts
     */
    constructor() {
        this.charts = {};
    }
    
    /**
     * Create gauge chart for glucose level
     * @param {string} elementId - Canvas element ID
     * @param {object} data - Glucose data
     */
    createGaugeChart(elementId, data) {
        const canvas = document.getElementById(elementId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Clear any existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        // Determine color based on glucose level
        let color = '#00FF00'; // green for normal
        
        if (data.primary_estimate === 'elevated') {
            color = '#FFFF00'; // yellow for elevated
        } else if (data.primary_estimate === 'low') {
            color = '#FF9900'; // orange for low
        } else if (data.primary_estimate === 'critical') {
            color = '#FF0000'; // red for critical
        }
        
        // Create chart
        this.charts[elementId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [data.confidence_score * 100, 100 - (data.confidence_score * 100)],
                    backgroundColor: [color, '#333333'],
                    borderWidth: 0
                }]
            },
            options: {
                cutout: '70%',
                rotation: -90,
                circumference: 180,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                }
            }
        });
        
        return this.charts[elementId];
    }
    
    /**
     * Create history chart for glucose trends
     * @param {string} elementId - Canvas element ID
     * @param {array} data - Historical glucose data
     */
    createHistoryChart(elementId, data) {
        const canvas = document.getElementById(elementId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Clear any existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        // Prepare data
        const labels = data.map(item => {
            const date = new Date(item.timestamp);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        });
        
        const values = data.map(item => {
            // Convert string estimates to numeric values for visualization
            switch (item.prediction.primary_estimate) {
                case 'low': return 60;
                case 'normal': return 100;
                case 'elevated': return 140;
                case 'critical': return 180;
                default: return 100;
            }
        });
        
        const confidences = data.map(item => item.prediction.confidence_score);
        
        // Create chart
        this.charts[elementId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Glucose Estimate',
                    data: values,
                    borderColor: '#FFFFFF',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: function(context) {
                        const value = context.dataset.data[context.dataIndex];
                        if (value <= 70) return '#FF9900'; // low
                        if (value <= 120) return '#00FF00'; // normal
                        if (value <= 160) return '#FFFF00'; // elevated
                        return '#FF0000'; // critical
                    },
                    pointRadius: function(context) {
                        const confidence = confidences[context.dataIndex];
                        return 4 + (confidence * 4); // Size based on confidence
                    },
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 40,
                        max: 200,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#CCCCCC'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#CCCCCC'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#FFFFFF',
                        bodyColor: '#CCCCCC',
                        callbacks: {
                            label: function(context) {
                                const dataIndex = context.dataIndex;
                                const confidence = confidences[dataIndex] * 100;
                                return [
                                    `Estimate: ${data[dataIndex].prediction.primary_estimate}`,
                                    `Confidence: ${confidence.toFixed(0)}%`
                                ];
                            }
                        }
                    }
                }
            }
        });
        
        return this.charts[elementId];
    }
    
    /**
     * Animate counter
     * @param {string} elementId - Element ID
     * @param {number} targetValue - Target value
     * @param {number} duration - Animation duration in ms
     * @param {string} prefix - Prefix to add before the number
     * @param {string} suffix - Suffix to add after the number
     */
    animateCounter(elementId, targetValue, duration = 2000, prefix = '', suffix = '') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const startTime = performance.now();
        const startValue = 0;
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            
            const current = startValue + (targetValue - startValue) * easeOutCubic;
            element.textContent = `${prefix}${Math.round(current)}${suffix}`;
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
    
    /**
     * Create biomarker radar chart
     * @param {string} elementId - Canvas element ID
     * @param {object} data - Biomarker data
     */
    createBiomarkerChart(elementId, data) {
        const canvas = document.getElementById(elementId);
        if (!canvas) return null;
        
        const ctx = canvas.getContext('2d');
        
        // Clear any existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        // Create chart
        this.charts[elementId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(data),
                datasets: [{
                    label: 'Voice Biomarkers',
                    data: Object.values(data),
                    backgroundColor: 'rgba(0, 255, 0, 0.2)',
                    borderColor: '#00FF00',
                    pointBackgroundColor: '#00FF00',
                    pointBorderColor: '#000000',
                    pointHoverBackgroundColor: '#FFFFFF',
                    pointHoverBorderColor: '#00FF00'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            display: false
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.2)'
                        },
                        pointLabels: {
                            color: '#CCCCCC',
                            font: {
                                size: 10
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
        
        return this.charts[elementId];
    }
}
