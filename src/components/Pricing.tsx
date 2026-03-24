import React from 'react';
import { Check, Zap, Shield, Crown } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '../lib/utils';

interface Plan {
  id: string;
  name: string;
  price: number;
  description: string;
  features: string[];
  icon: React.ReactNode;
  color: string;
}

const plans: Plan[] = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    description: 'Para gestores que estão começando.',
    features: [
      '1 Insight de IA por dia',
      'Dashboard Básico',
      'Conexão com 1 conta Meta',
      'Suporte via Comunidade'
    ],
    icon: <Zap className="w-6 h-6" />,
    color: 'border-[#141414]/20'
  },
  {
    id: 'gold',
    name: 'Gold',
    price: 50,
    description: 'Ideal para freelancers em crescimento.',
    features: [
      '5 Insights de IA por dia',
      'Dashboard Avançado',
      'Conexão com 3 contas Meta',
      'Suporte Prioritário',
      'Relatórios em PDF'
    ],
    icon: <Shield className="w-6 h-6" />,
    color: 'border-yellow-500'
  },
  {
    id: 'black',
    name: 'Black',
    price: 150,
    description: 'Para agências que buscam escala.',
    features: [
      '20 Insights de IA por dia',
      'Dashboard Customizável',
      'Contas Meta Ilimitadas',
      'Gerente de Conta Dedicado',
      'Alertas de Performance'
    ],
    icon: <Crown className="w-6 h-6" />,
    color: 'border-purple-600'
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 200,
    description: 'O nível máximo de inteligência.',
    features: [
      'Insights de IA Ilimitados',
      'White-label (Sua marca)',
      'API de Exportação',
      'Consultoria Mensal de Tráfego',
      'Acesso Antecipado a Novas IAs'
    ],
    icon: <Crown className="w-6 h-6" />,
    color: 'border-blue-600'
  }
];

interface PricingProps {
  onSelectPlan: (planId: string) => void;
  currentPlan?: string;
}

export default function Pricing({ onSelectPlan, currentPlan }: PricingProps) {
  return (
    <div className="py-12">
      <div className="text-center mb-16">
        <h2 className="text-4xl font-mono font-bold uppercase tracking-tighter mb-4">Escolha seu Plano</h2>
        <p className="font-serif italic opacity-60">Escalabilidade e inteligência para sua gestão de tráfego.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        {plans.map((plan, idx) => (
          <motion.div
            key={plan.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={cn(
              "bg-white/50 border-2 p-8 flex flex-col h-full transition-all group hover:bg-[#141414] hover:text-[#E4E3E0]",
              plan.color,
              currentPlan === plan.id && "bg-[#141414] text-[#E4E3E0] scale-105 shadow-2xl z-10"
            )}
          >
            <div className="flex justify-between items-start mb-6">
              <div className="p-2 border border-current">
                {plan.icon}
              </div>
              {currentPlan === plan.id && (
                <span className="text-[10px] font-mono uppercase font-bold px-2 py-1 border border-current">Plano Atual</span>
              )}
            </div>

            <h3 className="text-2xl font-mono font-bold uppercase mb-2">{plan.name}</h3>
            <div className="flex items-baseline gap-1 mb-4">
              <span className="text-3xl font-mono font-bold">R$ {plan.price}</span>
              <span className="text-xs font-mono opacity-50">/mês</span>
            </div>
            <p className="text-sm font-serif italic opacity-60 mb-8 group-hover:opacity-80">{plan.description}</p>

            <ul className="space-y-4 mb-12 flex-1">
              {plan.features.map((feature, fIdx) => (
                <li key={fIdx} className="flex items-start gap-3 text-xs font-mono uppercase tracking-tight">
                  <Check className="w-4 h-4 text-green-600 group-hover:text-green-400 shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => onSelectPlan(plan.id)}
              disabled={currentPlan === plan.id || plan.id === 'free'}
              className={cn(
                "w-full py-4 font-mono text-xs font-bold uppercase border-2 transition-all",
                currentPlan === plan.id 
                  ? "border-green-600 text-green-600 cursor-default" 
                  : "border-[#141414] hover:bg-[#E4E3E0] hover:text-[#141414] group-hover:border-[#E4E3E0]",
                plan.id === 'free' && "opacity-50 cursor-not-allowed"
              )}
            >
              {currentPlan === plan.id ? "Plano Ativo" : plan.id === 'free' ? "Plano Inicial" : "Assinar Agora"}
            </button>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
