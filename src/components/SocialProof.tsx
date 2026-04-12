import React from "react";
import { motion } from "motion/react";
import { Quote } from "lucide-react";

const testimonials = [
  {
    name: "Willian W.G.B.O.",
    role: "Instrutor de Práticas Profissionais | Engenharia de Produção",
    content: "Profissional atencioso e dedicado.",
    image: "/social-proof/willian.png",
    date: "10 de abril de 2026"
  },
  {
    name: "Arthur Henrique",
    role: "Staff Software Engineer",
    content: "Matheus é um programador e um resolvedor de problemas nato. Em constante aprendizado, busca aprender e aplicar seus conhecimentos em produtos reais.",
    image: "/social-proof/arthur.png",
    date: "21 de janeiro de 2026"
  }
];

export default function SocialProof() {
  return (
    <section className="mt-16 mb-12">
      <div className="flex items-center gap-3 mb-8">
        <Quote className="w-6 h-6 text-[#141414]" />
        <h2 className="text-2xl font-mono font-bold tracking-tighter uppercase">
          Prova Social & Depoimentos
        </h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {testimonials.map((t, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: idx * 0.2 }}
            className="bg-white/40 border border-[#141414] p-6 flex flex-col gap-4 hover:bg-white/60 transition-all group"
          >
            <div className="flex flex-col gap-4">
              <div className="overflow-hidden border border-[#141414]/20">
                <img 
                  src={t.image} 
                  alt={`Depoimento de ${t.name}`}
                  className="w-full h-auto grayscale hover:grayscale-0 transition-all duration-500"
                />
              </div>
              <div className="space-y-2">
                <p className="font-serif italic text-lg text-[#141414] leading-relaxed">
                  "{t.content}"
                </p>
                <div className="pt-4 border-t border-[#141414]/10">
                  <h4 className="font-mono font-bold text-sm uppercase tracking-tight">{t.name}</h4>
                  <p className="font-mono text-[10px] uppercase opacity-60 leading-tight mt-1">{t.role}</p>
                  <p className="font-mono text-[9px] uppercase opacity-40 mt-2">{t.date}</p>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
