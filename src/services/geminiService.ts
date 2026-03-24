import { GoogleGenAI } from "@google/genai";
import { DashboardData } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

export async function getTrafficInsights(data: DashboardData) {
  const model = "gemini-3-flash-preview";
  
  const prompt = `
    Você é um especialista sênior em tráfego pago (Facebook Ads, Google Ads).
    Analise os seguintes dados de performance de uma conta de anúncios e forneça 3 insights estratégicos acionáveis para o gestor de tráfego.
    
    Resumo Geral:
    - Gasto Total: R$ ${data.summary.spend}
    - ROAS Médio: ${data.summary.roas}
    - Conversões: ${data.summary.conversions}
    - CPA: R$ ${data.summary.cpa}
    - CTR: ${data.summary.ctr}%
    
    Campanhas:
    ${data.campaigns.map(c => `- ${c.name}: Gasto R$ ${c.spend}, ROAS ${c.roas}, Conversões ${c.conversions}`).join('\n')}
    
    Formate a resposta em JSON com o seguinte esquema:
    {
      "insights": [
        { "title": "Título do Insight", "description": "Descrição detalhada e ação recomendada" }
      ]
    }
  `;

  try {
    const response = await ai.models.generateContent({
      model,
      contents: prompt,
      config: {
        responseMimeType: "application/json"
      }
    });
    
    const text = response.text;
    if (!text) return { insights: [] };
    return JSON.parse(text);
  } catch (error) {
    console.error("Error fetching AI insights:", error);
    return { insights: [{ title: "Erro na IA", description: "Não foi possível gerar insights no momento." }] };
  }
}
