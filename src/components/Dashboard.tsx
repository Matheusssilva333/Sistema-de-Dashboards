import React, { useState, useEffect } from "react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  LineChart, Line, AreaChart, Area 
} from "recharts";
import { 
  TrendingUp, Users, DollarSign, Target, MousePointer2, 
  Brain, AlertCircle, CheckCircle2, PauseCircle, ChevronRight,
  LayoutDashboard, Settings, LogOut, Menu, X, Crown
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";
import { cn, formatCurrency, formatNumber, formatPercent } from "../lib/utils";
import { DashboardData } from "../types";
import { getTrafficInsights } from "../services/geminiService";

import Pricing from "./Pricing";

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"dashboard" | "pricing">("dashboard");

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/metrics");
      const json = await response.json();
      
      // Fetch subscription separately
      const subResponse = await fetch("/api/subscription");
      const subJson = await subResponse.json();
      
      if (json.error) {
        setError(json.error);
      } else {
        setData({ ...json, subscription: subJson });
        // Fetch AI insights
        const aiResponse = await getTrafficInsights(json);
        setInsights(aiResponse.insights);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setError("Falha ao carregar dados do servidor.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();

    // Listen for OAuth success message
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === 'META_AUTH_SUCCESS') {
        fetchData();
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const handleConnectMeta = async () => {
    try {
      const response = await fetch("/api/auth/meta/url");
      const { url, error } = await response.json();
      if (error) {
        alert(error + ". Configure as variáveis de ambiente no painel Secrets.");
        return;
      }
      window.open(url, 'meta_auth_popup', 'width=600,height=700');
    } catch (err) {
      alert("Erro ao iniciar conexão com a Meta.");
    }
  };

  const handleSelectPlan = async (planId: string) => {
    try {
      const response = await fetch("/api/checkout/create-preference", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ planId })
      });
      const { init_point, error } = await response.json();
      if (error) {
        alert(error);
        return;
      }
      // Redirect to Mercado Pago Checkout
      window.location.href = init_point;
    } catch (err) {
      alert("Erro ao processar pagamento.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#E4E3E0]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-[#141414] border-t-transparent rounded-full animate-spin" />
          <p className="font-mono text-xs uppercase tracking-widest text-[#141414]/60">Carregando Gestão Premium...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#E4E3E0] text-[#141414] font-sans selection:bg-[#141414] selection:text-[#E4E3E0]">
      {/* Sidebar */}
      <aside 
        className={cn(
          "bg-[#141414] text-[#E4E3E0] transition-all duration-300 flex flex-col",
          isSidebarOpen ? "w-64" : "w-20"
        )}
      >
        <div className="p-6 flex items-center gap-3">
          <div className="w-8 h-8 bg-[#E4E3E0] rounded flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-[#141414]" />
          </div>
          {isSidebarOpen && <span className="font-mono font-bold text-lg tracking-tighter uppercase">Gestão Premium</span>}
        </div>

        <nav className="flex-1 px-4 mt-8 space-y-2">
          <SidebarItem 
            icon={<LayoutDashboard />} 
            label="Dashboard" 
            active={activeTab === "dashboard"} 
            isOpen={isSidebarOpen} 
            onClick={() => setActiveTab("dashboard")}
          />
          <SidebarItem 
            icon={<Crown />} 
            label="Assinatura" 
            active={activeTab === "pricing"} 
            isOpen={isSidebarOpen} 
            onClick={() => setActiveTab("pricing")}
          />
          <SidebarItem icon={<Target />} label="Campanhas" isOpen={isSidebarOpen} />
          <SidebarItem icon={<Users />} label="Clientes" isOpen={isSidebarOpen} />
          <SidebarItem icon={<Settings />} label="Configurações" isOpen={isSidebarOpen} />
        </nav>

        <div className="p-4 border-t border-[#E4E3E0]/10">
          <div className={cn("px-4 py-3 mb-4 border border-[#E4E3E0]/20 bg-[#E4E3E0]/5", !isSidebarOpen && "hidden")}>
            <p className="text-[10px] font-mono uppercase opacity-40 mb-1">Seu Plano</p>
            <p className="text-xs font-mono font-bold uppercase tracking-widest text-green-400">{data?.subscription?.plan || 'Free'}</p>
          </div>
          <SidebarItem icon={<LogOut />} label="Sair" isOpen={isSidebarOpen} />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        <header className="flex justify-between items-center mb-12">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-mono font-bold tracking-tighter uppercase">
                {activeTab === "dashboard" ? "Visão Geral" : "Planos & Assinatura"}
              </h1>
              {activeTab === "dashboard" && !data?.isConnected && (
                <span className="px-2 py-0.5 border border-[#141414] text-[10px] font-mono uppercase font-bold bg-orange-100">Aguardando Conexão</span>
              )}
              {activeTab === "dashboard" && data?.isConnected && (
                <span className="px-2 py-0.5 border border-green-600 text-[10px] font-mono uppercase font-bold text-green-600 bg-green-50">Dados Reais</span>
              )}
            </div>
            <p className="font-serif italic text-sm opacity-60">
              {activeTab === "dashboard" 
                ? "Performance consolidada da conta de anúncios Meta" 
                : "Gerencie sua assinatura e acesse recursos exclusivos."}
            </p>
          </div>
          <div className="flex gap-4">
            {activeTab === "dashboard" && !data?.isConnected && (
              <button 
                onClick={handleConnectMeta}
                className="px-4 py-2 bg-[#141414] text-[#E4E3E0] font-mono text-xs uppercase font-bold hover:bg-opacity-90 transition-all flex items-center gap-2"
              >
                Conectar Meta Ads
              </button>
            )}
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 border border-[#141414] hover:bg-[#141414] hover:text-[#E4E3E0] transition-colors"
            >
              {isSidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </header>

        <AnimatePresence mode="wait">
          {activeTab === "dashboard" ? (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              {error && (
                <div className="mb-8 p-4 border border-red-600 bg-red-50 text-red-600 font-mono text-xs flex items-center gap-3">
                  <AlertCircle className="w-4 h-4" />
                  {error}
                </div>
              )}

              {!data && !error && (
                <div className="flex flex-col items-center justify-center h-64 border border-dashed border-[#141414]/30">
                  <p className="font-serif italic opacity-60 mb-4">Nenhum dado disponível. Conecte sua conta da Meta.</p>
                  <button 
                    onClick={handleConnectMeta}
                    className="px-6 py-3 border border-[#141414] font-mono text-xs uppercase font-bold hover:bg-[#141414] hover:text-[#E4E3E0] transition-all"
                  >
                    Configurar Conexão
                  </button>
                </div>
              )}

              {data && (
                <>
                  {/* Stats Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                    <StatCard 
                      label="Gasto Total" 
                      value={formatCurrency(data.summary.spend)} 
                      icon={<DollarSign className="w-4 h-4" />}
                      trend="+12.5%"
                    />
                    <StatCard 
                      label="ROAS Médio" 
                      value={data.summary.roas.toFixed(2)} 
                      icon={<TrendingUp className="w-4 h-4" />}
                      trend="+0.4"
                    />
                    <StatCard 
                      label="Conversões" 
                      value={formatNumber(data.summary.conversions)} 
                      icon={<Target className="w-4 h-4" />}
                      trend="+85"
                    />
                    <StatCard 
                      label="CTR Médio" 
                      value={formatPercent(data.summary.ctr)} 
                      icon={<MousePointer2 className="w-4 h-4" />}
                      trend="-0.2%"
                    />
                  </div>

                  {/* Charts Section */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
                    {/* Main Chart */}
                    <div className="lg:col-span-2 bg-white/50 border border-[#141414] p-6">
                      <div className="flex justify-between items-center mb-8">
                        <h3 className="font-mono font-bold uppercase text-xs tracking-widest">Gasto vs Conversões (7 dias)</h3>
                        <div className="flex gap-4 text-[10px] font-mono uppercase opacity-60">
                          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#141414]" /> Gasto</div>
                          <div className="flex items-center gap-1"><div className="w-2 h-2 bg-[#141414]/30" /> Conversões</div>
                        </div>
                      </div>
                      <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={data.daily}>
                            <defs>
                              <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#141414" stopOpacity={0.1}/>
                                <stop offset="95%" stopColor="#141414" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#141414/10" />
                            <XAxis 
                              dataKey="date" 
                              axisLine={false} 
                              tickLine={false} 
                              tick={{ fontSize: 10, fontFamily: 'monospace' }}
                              tickFormatter={(val) => val.split('-').slice(1).join('/')}
                            />
                            <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 10, fontFamily: 'monospace' }} />
                            <Tooltip 
                              contentStyle={{ backgroundColor: '#141414', color: '#E4E3E0', border: 'none', fontFamily: 'monospace', fontSize: '10px' }}
                              itemStyle={{ color: '#E4E3E0' }}
                            />
                            <Area type="monotone" dataKey="spend" stroke="#141414" fillOpacity={1} fill="url(#colorSpend)" strokeWidth={2} />
                            <Area type="monotone" dataKey="conversions" stroke="#141414" strokeDasharray="5 5" fill="transparent" strokeWidth={1} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>

                    {/* AI Insights */}
                    <div className="bg-[#141414] text-[#E4E3E0] p-6 flex flex-col">
                      <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-2">
                          <Brain className="w-5 h-5" />
                          <h3 className="font-mono font-bold uppercase text-xs tracking-widest">AI Insights</h3>
                        </div>
                        {data?.subscription?.plan === 'free' && (
                          <span className="text-[9px] font-mono uppercase bg-yellow-500 text-[#141414] px-1.5 py-0.5 font-bold">Limitado</span>
                        )}
                      </div>
                      <div className="space-y-6 flex-1">
                        {insights.length > 0 ? insights.map((insight, idx) => (
                          <motion.div 
                            key={idx}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="space-y-2"
                          >
                            <h4 className="font-mono text-[11px] font-bold uppercase text-[#E4E3E0]/80 flex items-center gap-2">
                              <ChevronRight className="w-3 h-3" /> {insight.title}
                            </h4>
                            <p className="font-serif italic text-sm text-[#E4E3E0]/60 leading-relaxed">
                              {insight.description}
                            </p>
                          </motion.div>
                        )) : (
                          <p className="font-serif italic text-sm opacity-40">Analisando dados para gerar insights...</p>
                        )}
                      </div>
                      <div className="mt-8 pt-6 border-t border-[#E4E3E0]/10 flex items-center justify-between">
                        <span className="text-[10px] font-mono opacity-40 uppercase">Powered by Gemini 3.1</span>
                        <div className="flex gap-1">
                          {[1, 2, 3].map(i => <div key={i} className="w-1 h-1 bg-[#E4E3E0]/20 rounded-full" />)}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Campaign Table */}
                  <div className="bg-white/50 border border-[#141414]">
                    <div className="p-6 border-bottom border-[#141414] flex justify-between items-center">
                      <h3 className="font-mono font-bold uppercase text-xs tracking-widest">Performance por Campanha</h3>
                      <button className="text-[10px] font-mono uppercase underline underline-offset-4 hover:opacity-60 transition-opacity">Ver Todas</button>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="border-y border-[#141414]">
                            <th className="p-4 font-serif italic text-[11px] uppercase opacity-50 font-normal">Status</th>
                            <th className="p-4 font-serif italic text-[11px] uppercase opacity-50 font-normal">Campanha</th>
                            <th className="p-4 font-serif italic text-[11px] uppercase opacity-50 font-normal text-right">Gasto</th>
                            <th className="p-4 font-serif italic text-[11px] uppercase opacity-50 font-normal text-right">ROAS</th>
                            <th className="p-4 font-serif italic text-[11px] uppercase opacity-50 font-normal text-right">Conversões</th>
                            <th className="p-4 font-serif italic text-[11px] uppercase opacity-50 font-normal text-right">Ação</th>
                          </tr>
                        </thead>
                        <tbody>
                          {data.campaigns.map((campaign) => (
                            <tr key={campaign.id} className="border-b border-[#141414]/10 hover:bg-[#141414] hover:text-[#E4E3E0] transition-colors group cursor-pointer">
                              <td className="p-4">
                                {campaign.status === 'active' ? (
                                  <CheckCircle2 className="w-4 h-4 text-green-600 group-hover:text-green-400" />
                                ) : (
                                  <PauseCircle className="w-4 h-4 text-orange-600 group-hover:text-orange-400" />
                                )}
                              </td>
                              <td className="p-4 font-mono text-xs font-bold uppercase">{campaign.name}</td>
                              <td className="p-4 font-mono text-xs text-right">{formatCurrency(campaign.spend)}</td>
                              <td className="p-4 font-mono text-xs text-right">{campaign.roas.toFixed(2)}</td>
                              <td className="p-4 font-mono text-xs text-right">{formatNumber(campaign.conversions)}</td>
                              <td className="p-4 text-right">
                                <button className="p-1 border border-current opacity-40 group-hover:opacity-100">
                                  <ChevronRight className="w-3 h-3" />
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="pricing"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <Pricing 
                onSelectPlan={handleSelectPlan} 
                currentPlan={data?.subscription?.plan || 'free'} 
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

function SidebarItem({ 
  icon, 
  label, 
  active = false, 
  isOpen = true,
  onClick
}: { 
  icon: React.ReactNode, 
  label: string, 
  active?: boolean, 
  isOpen?: boolean,
  onClick?: () => void
}) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-4 px-4 py-3 transition-all group",
        active ? "bg-[#E4E3E0] text-[#141414]" : "hover:bg-[#E4E3E0]/10 text-[#E4E3E0]/60 hover:text-[#E4E3E0]"
      )}
    >
      <div className={cn("w-5 h-5", active ? "text-[#141414]" : "text-current")}>
        {icon}
      </div>
      {isOpen && <span className="font-mono text-xs font-bold uppercase tracking-widest">{label}</span>}
      {active && isOpen && <div className="ml-auto w-1 h-1 bg-[#141414] rounded-full" />}
    </button>
  );
}

function StatCard({ label, value, icon, trend }: { label: string, value: string, icon: React.ReactNode, trend: string }) {
  return (
    <div className="bg-white/50 border border-[#141414] p-6 flex flex-col gap-4 hover:bg-[#141414] hover:text-[#E4E3E0] transition-all group cursor-default">
      <div className="flex justify-between items-start">
        <span className="font-serif italic text-[11px] uppercase opacity-50 group-hover:opacity-70">{label}</span>
        <div className="p-1.5 border border-[#141414] group-hover:border-[#E4E3E0]">
          {icon}
        </div>
      </div>
      <div className="flex items-baseline justify-between gap-2">
        <span className="text-3xl font-mono font-bold tracking-tighter">{value}</span>
        <span className={cn(
          "text-[10px] font-mono font-bold px-1.5 py-0.5 border",
          trend.startsWith('+') ? "border-green-600 text-green-600 group-hover:border-green-400 group-hover:text-green-400" : "border-red-600 text-red-600 group-hover:border-red-400 group-hover:text-red-400"
        )}>
          {trend}
        </span>
      </div>
    </div>
  );
}
