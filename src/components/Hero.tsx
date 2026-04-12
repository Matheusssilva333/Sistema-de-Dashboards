import React from "react";
import { motion } from "motion/react";
import { ArrowRight, Zap, BarChart3 } from "lucide-react";

export default function Hero() {
  return (
    <section className="mb-16 py-12">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        {/* Left Content */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          <div className="space-y-4">
            <motion.h1 
              className="text-5xl lg:text-6xl font-mono font-bold tracking-tighter uppercase leading-tight"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              Gestão Premium
            </motion.h1>
            <motion.p 
              className="text-lg font-serif italic opacity-70 leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              Transforme seus dados de anúncios em inteligência acionável. Com AI avançada e análises em tempo real, você toma decisões mais rápidas e lucrativas.
            </motion.p>
          </div>

          <motion.div 
            className="flex flex-wrap gap-4 pt-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="flex items-center gap-2 px-4 py-2 border border-[#141414] bg-white/40 hover:bg-[#141414] hover:text-[#E4E3E0] transition-all group cursor-pointer">
              <Zap className="w-4 h-4" />
              <span className="font-mono text-xs font-bold uppercase">IA Avançada</span>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 border border-[#141414] bg-white/40 hover:bg-[#141414] hover:text-[#E4E3E0] transition-all group cursor-pointer">
              <BarChart3 className="w-4 h-4" />
              <span className="font-mono text-xs font-bold uppercase">Análises Reais</span>
            </div>
          </motion.div>

          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-8 px-8 py-4 bg-[#141414] text-[#E4E3E0] font-mono font-bold uppercase text-sm tracking-widest hover:scale-105 transition-transform flex items-center gap-2 group"
          >
            Começar Agora
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </motion.button>
        </motion.div>

        {/* Right Visual */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="relative h-[400px] lg:h-[500px]"
        >
          <div className="absolute inset-0 border border-[#141414] bg-gradient-to-br from-white/60 to-white/20 flex items-center justify-center overflow-hidden group">
            <motion.div
              animate={{ 
                y: [0, -20, 0],
                rotate: [0, 2, -2, 0]
              }}
              transition={{ 
                duration: 4, 
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="text-center space-y-4"
            >
              <div className="text-6xl font-mono font-bold text-[#141414]">📊</div>
              <p className="font-mono text-xs uppercase tracking-widest opacity-60">Dashboard em Tempo Real</p>
              <div className="space-y-2 text-left text-xs font-mono">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                  <span>ROAS: 4.2x</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                  <span>Conversões: +45%</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-600 rounded-full animate-pulse" />
                  <span>CTR: 3.8%</span>
                </div>
              </div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
