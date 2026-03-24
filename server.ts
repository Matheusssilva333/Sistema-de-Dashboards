import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";
import { MercadoPagoConfig, Preference } from 'mercadopago';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// --- Mercado Pago Setup ---
const client = new MercadoPagoConfig({ 
  accessToken: process.env.MERCADO_PAGO_ACCESS_TOKEN || '' 
});

// --- Mock SaaS State (In-memory for demo, use DB in production) ---
let metaAccessToken: string | null = null;
let userSubscription = {
  plan: "free", // free, gold, black, premium
  status: "active",
  expiresAt: null as string | null
};

const PLANS = {
  free: { name: "Free", price: 0, aiInsightsLimit: 1 },
  gold: { name: "Gold", price: 50, aiInsightsLimit: 5 },
  black: { name: "Black", price: 150, aiInsightsLimit: 20 },
  premium: { name: "Premium", price: 200, aiInsightsLimit: 100 }
};

async function startServer() {
  const app = express();
  const PORT = Number(process.env.PORT) || 3000;

  app.use(express.json());

  // --- Subscription & Payment Endpoints ---

  // 1. Get current subscription status
  app.get("/api/subscription", (req, res) => {
    res.json(userSubscription);
  });

  // 2. Create Mercado Pago Preference for Checkout
  app.post("/api/checkout/create-preference", async (req, res) => {
    const { planId } = req.body;
    const plan = (PLANS as any)[planId];

    if (!plan || planId === 'free') {
      return res.status(400).json({ error: "Plano inválido" });
    }

    try {
      const preference = new Preference(client);
      const result = await preference.create({
        body: {
          items: [
            {
              id: planId,
              title: `Assinatura Gestão Premium - Plano ${plan.name}`,
              unit_price: plan.price,
              quantity: 1,
              currency_id: 'BRL'
            }
          ],
          back_urls: {
            success: `${process.env.APP_URL}/dashboard?payment=success`,
            failure: `${process.env.APP_URL}/dashboard?payment=failure`,
            pending: `${process.env.APP_URL}/dashboard?payment=pending`
          },
          auto_return: 'approved',
          notification_url: `${process.env.APP_URL}/api/webhooks/mercadopago`,
          external_reference: "user_123" // In a real app, use the actual user ID
        }
      });

      res.json({ id: result.id, init_point: result.init_point });
    } catch (error) {
      console.error("Mercado Pago Error:", error);
      res.status(500).json({ error: "Erro ao criar preferência de pagamento" });
    }
  });

  // 3. Webhook for Payment Notifications
  app.post("/api/webhooks/mercadopago", async (req, res) => {
    const { type, data } = req.body;
    
    if (type === 'payment') {
      // In a real app, fetch payment details from MP and update DB
      console.log("Payment received:", data.id);
      // For demo: update the mock user state
      // userSubscription.plan = "gold"; // Example
    }
    
    res.sendStatus(200);
  });

  // --- Meta Ads API Integration ---
  // (Keep existing Meta endpoints but add subscription check)

  // 1. Get Meta Login URL
  app.get("/api/auth/meta/url", (req, res) => {
    const appId = process.env.META_APP_ID;
    const redirectUri = `${process.env.APP_URL}/api/auth/meta/callback`;
    
    if (!appId) {
      return res.status(400).json({ error: "META_APP_ID not configured" });
    }

    const params = new URLSearchParams({
      client_id: appId,
      redirect_uri: redirectUri,
      scope: "ads_read,ads_management,read_insights",
      response_type: "code",
    });

    res.json({ url: `https://www.facebook.com/v18.0/dialog/oauth?${params}` });
  });

  // 2. Meta Auth Callback
  app.get("/api/auth/meta/callback", async (req, res) => {
    const { code } = req.query;
    const appId = process.env.META_APP_ID;
    const appSecret = process.env.META_APP_SECRET;
    const redirectUri = `${process.env.APP_URL}/api/auth/meta/callback`;

    if (!code || !appId || !appSecret) {
      return res.status(400).send("Missing code or credentials");
    }

    try {
      const response = await fetch(
        `https://graph.facebook.com/v18.0/oauth/access_token?client_id=${appId}&redirect_uri=${redirectUri}&client_secret=${appSecret}&code=${code}`
      );
      const data = await response.json() as any;
      
      if (data.access_token) {
        metaAccessToken = data.access_token;
        res.send(`
          <html>
            <body>
              <script>
                if (window.opener) {
                  window.opener.postMessage({ type: 'META_AUTH_SUCCESS' }, '*');
                  window.close();
                } else {
                  window.location.href = '/';
                }
              </script>
              <p>Conectado com sucesso! Esta janela fechará automaticamente.</p>
            </body>
          </html>
        `);
      } else {
        res.status(400).send("Failed to get access token: " + JSON.stringify(data));
      }
    } catch (error) {
      res.status(500).send("Error during Meta authentication");
    }
  });

  // 3. Fetch Real Meta Metrics
  app.get("/api/metrics", async (req, res) => {
    const adAccountId = process.env.META_AD_ACCOUNT_ID;
    
    if (!metaAccessToken || !adAccountId) {
      // Return empty state if not connected, ensuring only real data is used
      return res.json({ 
        summary: { spend: 0, roas: 0, conversions: 0, cpa: 0, ctr: 0, clicks: 0 },
        daily: [],
        campaigns: [],
        isRealData: false,
        isConnected: false
      });
    }

    try {
      // Fetch Insights (Summary & Daily)
      const insightsResponse = await fetch(
        `https://graph.facebook.com/v18.0/${adAccountId}/insights?fields=spend,conversions,reach,impressions,clicks,cpc,ctr,cpp&date_preset=last_7d&time_increment=1&access_token=${metaAccessToken}`
      );
      const insightsData = await insightsResponse.json() as any;

      // Fetch Campaigns
      const campaignsResponse = await fetch(
        `https://graph.facebook.com/v18.0/${adAccountId}/campaigns?fields=name,status,insights.date_preset(last_7d){spend,conversions,roas}&access_token=${metaAccessToken}`
      );
      const campaignsData = await campaignsResponse.json() as any;

      if (insightsData.error || campaignsData.error) {
        throw new Error(insightsData.error?.message || campaignsData.error?.message);
      }

      // Transform Meta data to our Dashboard format
      const daily = insightsData.data.map((day: any) => ({
        date: day.date_start,
        spend: parseFloat(day.spend || 0),
        conversions: parseInt(day.conversions?.[0]?.value || 0),
        roas: parseFloat(day.purchase_roas?.[0]?.value || 0)
      }));

      const summary = daily.reduce((acc: any, day: any) => ({
        spend: acc.spend + day.spend,
        conversions: acc.conversions + day.conversions,
        roas: acc.roas + day.roas,
        clicks: acc.clicks + parseInt(insightsData.data[0].clicks || 0), // Simplification
      }), { spend: 0, conversions: 0, roas: 0, clicks: 0 });
      
      summary.roas = summary.roas / daily.length;
      summary.cpa = summary.spend / (summary.conversions || 1);
      summary.ctr = parseFloat(insightsData.data[0]?.ctr || 0);

      const campaigns = campaignsData.data.map((c: any) => ({
        id: c.id,
        name: c.name,
        status: c.status.toLowerCase(),
        spend: parseFloat(c.insights?.data?.[0]?.spend || 0),
        roas: parseFloat(c.insights?.data?.[0]?.purchase_roas?.[0]?.value || 0),
        conversions: parseInt(c.insights?.data?.[0]?.conversions?.[0]?.value || 0)
      }));

      res.json({ summary, daily, campaigns, isRealData: true });
    } catch (error: any) {
      console.error("Meta API Error:", error);
      res.status(500).json({ error: "Erro ao buscar dados da Meta: " + error.message });
    }
  });

  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", message: "Gestão Premium API is running" });
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Gestão Premium Server running on http://localhost:${PORT}`);
  });
}

function getMockData(isDemo: boolean) {
  return {
    isDemo,
    summary: { spend: 12500.50, roas: 4.2, conversions: 850, cpa: 14.70, ctr: 2.1, clicks: 40500 },
    daily: [
      { date: "2026-03-17", spend: 1500, conversions: 100, roas: 3.8 },
      { date: "2026-03-18", spend: 1800, conversions: 120, roas: 4.1 },
      { date: "2026-03-19", spend: 1600, conversions: 110, roas: 4.0 },
      { date: "2026-03-20", spend: 2000, conversions: 150, roas: 4.5 },
      { date: "2026-03-21", spend: 1900, conversions: 140, roas: 4.3 },
      { date: "2026-03-22", spend: 1700, conversions: 115, roas: 4.2 },
      { date: "2026-03-23", spend: 2000, conversions: 115, roas: 4.4 }
    ],
    campaigns: [
      { id: 1, name: "Venda Direta - Coleção Verão", status: "active", spend: 4500, roas: 5.1, conversions: 320 },
      { id: 2, name: "Remarketing - Carrinho Abandonado", status: "active", spend: 1200, roas: 8.4, conversions: 150 },
      { id: 3, name: "Lookalike - Compradores 1%", status: "active", spend: 3800, roas: 3.2, conversions: 210 },
      { id: 4, name: "Topo de Funil - Vídeo View", status: "paused", spend: 3000, roas: 1.5, conversions: 170 }
    ]
  };
}

startServer();
