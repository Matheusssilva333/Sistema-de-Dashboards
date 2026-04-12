import React from "react";
import { motion } from "motion/react";
import { Brain, TrendingUp, Shield, Zap, BarChart3, Users } from "lucide-react";

const features = [
  {
    icon: <Brain className="w-8 h-8" />,
    title: "IA Avançada",
    description: "Insights automáticos gerados por Gemini 3.1 para otimizar suas campanhas."
  },
  {
    icon: <TrendingUp className="w-8 h-8" />,
    title: "Análises em Tempo Real",
    description: "Monitore performance consolidada de múltiplas contas Meta Ads."
  },
  {
    icon: <Shield className="w-8 h-8" />,
    title: "Segurança de Dados",
    description: "Autenticação segura via OAuth e proteção total de seus dados."
  },
  {
    icon: <Zap className="w-8 h-8" />,
    title: "Performance Rápida",
    description: "Dashboard otimizado com carregamento instantâneo e responsivo."
  },
  {
    icon: <BarChart3 className="w-8 h-8" />,
    title: "Relatórios Customizáveis",
    description: "Gere relatórios em PDF com métricas personalizadas para seus clientes."
  },
  {
    icon: <Users className="w-8 h-8" />,
    title: "Suporte Dedicado",
    description: "Equipe pronta para ajudar no seu crescimento e sucesso."
  }
];

export default function Features() {
  return (
    <section className="mb-16 py-12">
      <div className="text-center mb-12">
        <motion.h2 
          className="text-4xl font-mono font-bold tracking-tighter uppercase mb-4"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          Recursos Poderosos
        </motion.h2>
        <motion.p 
          className="text-lg font-serif italic opacity-60 max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
        >
          Tudo que você precisa para gerenciar e otimizar seus anúncios em um só lugar.
        </motion.p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: idx * 0.1 }}
            className="bg-white/40 border border-[#141414] p-6 hover:bg-[#141414] hover:text-[#E4E3E0] transition-all group cursor-default"
          >
            <div className="mb-4 p-3 border border-[#141414] w-fit bg-white/50 group-hover:bg-[#E4E3E0] group-hover:text-[#141414] transition-all">
              {feature.icon}
            </div>
            <h3 className="text-lg font-mono font-bold uppercase mb-2 tracking-tight">
              {feature.title}
            </h3>
            <p className="text-sm font-serif italic opacity-70 group-hover:opacity-80 leading-relaxed">
              {feature.description}
            </p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
