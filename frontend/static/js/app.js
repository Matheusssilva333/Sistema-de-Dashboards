/**
 * Traffic Dashboard - Meta Ads
 * Main Application JavaScript
 */

// API Base URL
const API_BASE_URL = '';

// Alpine.js Dashboard App
function dashboardApp() {
    return {
        // State
        sidebarCollapsed: false,
        activeTab: 'overview',
        pageTitle: 'Visão Geral',
        loading: false,
        selectedPeriod: 30,
        selectedAccount: null,
        searchQuery: '',
        statusFilter: '',
        
        // Data
        accounts: [],
        campaigns: [],
        filteredCampaigns: [],
        summary: {
            impressions: 0,
            clicks: 0,
            spend: 0,
            conversions: 0,
            ctr: 0,
            cpc: 0,
            cpm: 0,
            cpa: 0
        },
        
        // Charts
        performanceChart: null,
        roiChart: null,
        
        // Initialize
        async init() {
            console.log('🚀 Initializing Traffic Dashboard...');
            await this.loadAccounts();
            await this.loadData();
            this.initCharts();
        },
        
        // Set Active Tab
        setActiveTab(tab) {
            this.activeTab = tab;
            
            const titles = {
                'overview': 'Visão Geral',
                'campaigns': 'Campanhas',
                'performance': 'Performance',
                'audience': 'Público',
                'reports': 'Relatórios'
            };
            
            this.pageTitle = titles[tab] || 'Dashboard';
            
            // Update active nav item
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
            });
            
            const activeItem = document.querySelector(`[href="#${tab}"]`);
            if (activeItem) {
                activeItem.classList.add('active');
            }
        },
        
        // Load Accounts
        async loadAccounts() {
            try {
                const response = await fetch(`${API_BASE_URL}/api/ad-accounts/`);
                const data = await response.json();
                
                this.accounts = data.accounts || [];
                
                if (this.accounts.length > 0 && !this.selectedAccount) {
                    this.selectedAccount = this.accounts[0];
                }
                
                console.log(`✅ Loaded ${this.accounts.length} ad accounts`);
            } catch (error) {
                console.error('❌ Error loading accounts:', error);
                this.showNotification('Erro ao carregar contas', 'error');
            }
        },
        
        // Load Data
        async loadData() {
            this.loading = true;
            
            try {
                // Load summary
                await this.loadSummary();
                
                // Load campaigns if account selected
                if (this.selectedAccount) {
                    await this.loadCampaigns();
                }
                
                console.log('✅ Data loaded successfully');
            } catch (error) {
                console.error('❌ Error loading data:', error);
                this.showNotification('Erro ao carregar dados', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        // Load Summary
        async loadSummary() {
            try {
                const params = new URLSearchParams({
                    days: this.selectedPeriod
                });
                
                if (this.selectedAccount) {
                    params.append('account_id', this.selectedAccount.account_id);
                }
                
                const response = await fetch(`${API_BASE_URL}/api/insights/summary?${params}`);
                const data = await response.json();
                
                this.summary = data.metrics || this.summary;
                
                console.log('📊 Summary loaded:', this.summary);
            } catch (error) {
                console.error('❌ Error loading summary:', error);
            }
        },
        
        // Load Campaigns
        async loadCampaigns() {
            try {
                const params = new URLSearchParams({
                    account_id: this.selectedAccount.account_id
                });
                
                if (this.statusFilter) {
                    params.append('status', this.statusFilter);
                }
                
                const response = await fetch(`${API_BASE_URL}/api/campaigns/?${params}`);
                const data = await response.json();
                
                this.campaigns = data.campaigns || [];
                this.filterCampaigns();
                
                console.log(`📢 Loaded ${this.campaigns.length} campaigns`);
            } catch (error) {
                console.error('❌ Error loading campaigns:', error);
            }
        },
        
        // Filter Campaigns
        filterCampaigns() {
            this.filteredCampaigns = this.campaigns.filter(campaign => {
                const matchesSearch = !this.searchQuery || 
                    campaign.name.toLowerCase().includes(this.searchQuery.toLowerCase());
                
                const matchesStatus = !this.statusFilter || 
                    campaign.status === this.statusFilter;
                
                return matchesSearch && matchesStatus;
            });
        },
        
        // Sync Data
        async syncData() {
            this.loading = true;
            
            try {
                // Sync accounts
                await fetch(`${API_BASE_URL}/api/ad-accounts/sync`, {
                    method: 'POST'
                });
                
                // Reload data
                await this.loadAccounts();
                await this.loadData();
                
                this.showNotification('Dados sincronizados com sucesso!', 'success');
                console.log('✅ Data synced successfully');
            } catch (error) {
                console.error('❌ Error syncing data:', error);
                this.showNotification('Erro ao sincronizar dados', 'error');
            } finally {
                this.loading = false;
            }
        },
        
        // View Campaign Details
        viewCampaignDetails(campaign) {
            console.log('👁️ Viewing campaign:', campaign);
            // TODO: Implement campaign details modal/page
            alert(`Visualizando campanha: ${campaign.name}`);
        },
        
        // Edit Campaign
        editCampaign(campaign) {
            console.log('✏️ Editing campaign:', campaign);
            // TODO: Implement campaign editing
            alert(`Editando campanha: ${campaign.name}`);
        },
        
        // Format Number
        formatNumber(num) {
            if (!num) return '0';
            return new Intl.NumberFormat('pt-BR').format(num);
        },
        
        // Format Currency
        formatCurrency(value) {
            if (!value) return 'R$ 0,00';
            return new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL'
            }).format(value);
        },
        
        // Show Notification
        showNotification(message, type = 'info') {
            // Simple console notification for now
            // TODO: Implement toast notifications
            console.log(`[${type.toUpperCase()}] ${message}`);
        },
        
        // Initialize Charts
        initCharts() {
            // Wait for DOM to be ready
            this.$nextTick(() => {
                this.createPerformanceChart();
                this.createROIChart();
            });
        },
        
        // Create Performance Chart
        createPerformanceChart() {
            const ctx = document.getElementById('performanceChart');
            if (!ctx) return;
            
            // Sample data (would come from API)
            const labels = this.generateDateLabels(this.selectedPeriod);
            const impressionsData = this.generateSampleData(labels.length, 1000, 5000);
            const clicksData = this.generateSampleData(labels.length, 50, 300);
            const spendData = this.generateSampleData(labels.length, 100, 500);
            
            this.performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            label: 'Impressões',
                            data: impressionsData,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            tension: 0.4,
                            fill: true,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Cliques',
                            data: clicksData,
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            tension: 0.4,
                            fill: true,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Gasto (R$)',
                            data: spendData,
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            tension: 0.4,
                            fill: true,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                color: '#cbd5e1',
                                usePointStyle: true,
                                padding: 20
                            }
                        },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            titleColor: '#f1f5f9',
                            bodyColor: '#cbd5e1',
                            borderColor: '#334155',
                            borderWidth: 1,
                            padding: 12,
                            displayColors: true
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                color: '#334155',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        },
                        y: {
                            type: 'linear',
                            position: 'left',
                            grid: {
                                color: '#334155',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        },
                        y1: {
                            type: 'linear',
                            position: 'right',
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        }
                    }
                }
            });
        },
        
        // Create ROI Chart
        createROIChart() {
            const ctx = document.getElementById('roiChart');
            if (!ctx) return;
            
            // Sample data
            const campaigns = ['Campanha A', 'Campanha B', 'Campanha C', 'Campanha D', 'Campanha E'];
            const roiData = [4.5, 3.2, 5.1, 2.8, 3.9];
            
            this.roiChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: campaigns,
                    datasets: [{
                        label: 'ROAS',
                        data: roiData,
                        backgroundColor: [
                            'rgba(59, 130, 246, 0.8)',
                            'rgba(139, 92, 246, 0.8)',
                            'rgba(16, 185, 129, 0.8)',
                            'rgba(245, 158, 11, 0.8)',
                            'rgba(6, 182, 212, 0.8)'
                        ],
                        borderColor: [
                            '#3b82f6',
                            '#8b5cf6',
                            '#10b981',
                            '#f59e0b',
                            '#06b6d4'
                        ],
                        borderWidth: 2,
                        borderRadius: 8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            backgroundColor: '#1e293b',
                            titleColor: '#f1f5f9',
                            bodyColor: '#cbd5e1',
                            borderColor: '#334155',
                            borderWidth: 1,
                            padding: 12
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#94a3b8'
                            }
                        },
                        y: {
                            grid: {
                                color: '#334155',
                                drawBorder: false
                            },
                            ticks: {
                                color: '#94a3b8',
                                callback: function(value) {
                                    return value.toFixed(1) + 'x';
                                }
                            },
                            beginAtZero: true
                        }
                    }
                }
            });
        },
        
        // Generate Date Labels
        generateDateLabels(days) {
            const labels = [];
            const today = new Date();
            
            for (let i = days - 1; i >= 0; i--) {
                const date = new Date(today);
                date.setDate(date.getDate() - i);
                labels.push(date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }));
            }
            
            return labels;
        },
        
        // Generate Sample Data
        generateSampleData(length, min, max) {
            const data = [];
            for (let i = 0; i < length; i++) {
                data.push(Math.floor(Math.random() * (max - min + 1)) + min);
            }
            return data;
        }
    };
}

// Export for global use
window.dashboardApp = dashboardApp;

console.log('✅ Dashboard App loaded');
