import os

file_path = 'templates/index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace ls
content = content.replace(
"""    const ls = {
      get: (k, d) => { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch { return d; } },
      set: (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
    };""",
"""    const api = {
      get: async (url) => { const r = await fetch(url); return r.json(); },
      post: async (url, data) => { const r = await fetch(url, { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) }); return r.json(); },
      put: async (url, data) => { const r = await fetch(url, { method: 'PUT', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data) }); return r.json(); },
      del: async (url) => { const r = await fetch(url, { method: 'DELETE' }); return r.json(); },
    };"""
)

# TradeTabContent signature and handlers
content = content.replace(
"""    const TradeTabContent = ({ trades, setTrades, settings, initialBalance, month, isDemo, prefill, clearPrefill }) => {""",
"""    const TradeTabContent = ({ trades, onAddTrade, onUpdateTrade, onDeleteTrade, settings, initialBalance, month, isDemo, prefill, clearPrefill }) => {"""
)

content = content.replace(
"""      const handleAdd = useCallback((trade) => {
        if (editTrade) setTrades(ts=>ts.map(t=>t.id===trade.id?trade:t));
        else           setTrades(ts=>[...ts,trade]);
        setEditTrade(null); setShowForm(false); clearPrefill?.();
      }, [editTrade, setTrades, clearPrefill]);

      const handleEdit   = useCallback((trade) => { setEditTrade(trade); setShowForm(true); window.scrollTo({top:0,behavior:'smooth'}); }, []);
      const handleDelete = useCallback((id) => { if(window.confirm('削除しますか？')) setTrades(ts=>ts.filter(t=>t.id!==id)); }, [setTrades]);""",
"""      const handleAdd = useCallback(async (trade) => {
        if (editTrade) await onUpdateTrade(trade);
        else           await onAddTrade(trade);
        setEditTrade(null); setShowForm(false); clearPrefill?.();
      }, [editTrade, onAddTrade, onUpdateTrade, clearPrefill]);

      const handleEdit   = useCallback((trade) => { setEditTrade(trade); setShowForm(true); window.scrollTo({top:0,behavior:'smooth'}); }, []);
      const handleDelete = useCallback(async (id) => { if(window.confirm('削除しますか？')) await onDeleteTrade(id); }, [onDeleteTrade]);"""
)

# SettingsForm update
content = content.replace(
"""    const SettingsForm = ({ settings, onSave }) => {""",
"""    const SettingsForm = ({ settings, onSave }) => {"""
) # unchanged

content = content.replace(
"""      const handleSubmit = (e) => {
        e.preventDefault();
        const p = (k,d) => Math.max(0.01, parseFloat(form[k])||d);
        onSave({
          initialBalance:     Math.max(1, parseFloat(form.initialBalance)||1000),
          monthlyTargetPct:   p('monthlyTargetPct',20),
          dailyLossLimitPct:  p('dailyLossLimitPct',6),
          monthlyDDLimitPct:  p('monthlyDDLimitPct',10),
          minWinRate:         p('minWinRate',50),
          minRR:              p('minRR',2.0),
          minComplianceRate:  p('minComplianceRate',90),
          maxRiskPerTradePct: p('maxRiskPerTradePct',2),
          demoInitialBalance: Math.max(1, parseFloat(form.demoInitialBalance)||10000),
        });
        setSaved(true); setTimeout(()=>setSaved(false),2500);
      };""",
"""      const handleSubmit = async (e) => {
        e.preventDefault();
        const p = (k,d) => Math.max(0.01, parseFloat(form[k])||d);
        await onSave({
          initialBalance:     Math.max(1, parseFloat(form.initialBalance)||1000),
          monthlyTargetPct:   p('monthlyTargetPct',20),
          dailyLossLimitPct:  p('dailyLossLimitPct',6),
          monthlyDDLimitPct:  p('monthlyDDLimitPct',10),
          minWinRate:         p('minWinRate',50),
          minRR:              p('minRR',2.0),
          minComplianceRate:  p('minComplianceRate',90),
          maxRiskPerTradePct: p('maxRiskPerTradePct',2),
          demoInitialBalance: Math.max(1, parseFloat(form.demoInitialBalance)||10000),
        });
        setSaved(true); setTimeout(()=>setSaved(false),2500);
      };"""
)

# App update
content = content.replace(
"""    const App = () => {
      const [trades,     setTrades]     = useState(()=>ls.get(TRADES_KEY,[]));
      const [demoTrades, setDemoTrades] = useState(()=>ls.get(DEMO_TRADES_KEY,[]));
      const [settings,   setSettings]   = useState(()=>({...DEFAULT_SETTINGS,...ls.get(SETTINGS_KEY,{})}));
      const [tab,        setTab]        = useState('dashboard');
      const [month,      setMonth]      = useState(thisMonth);
      const [prefill,    setPrefill]    = useState(null);

      useEffect(()=>{ ls.set(TRADES_KEY,    trades);    },[trades]);
      useEffect(()=>{ ls.set(DEMO_TRADES_KEY,demoTrades);},[demoTrades]);
      useEffect(()=>{ ls.set(SETTINGS_KEY,  settings);  },[settings]);""",
"""    const App = () => {
      const [trades,     setTrades]     = useState([]);
      const [demoTrades, setDemoTrades] = useState([]);
      const [settings,   setSettings]   = useState(DEFAULT_SETTINGS);
      const [tab,        setTab]        = useState('dashboard');
      const [month,      setMonth]      = useState(thisMonth);
      const [prefill,    setPrefill]    = useState(null);
      const [loading,    setLoading]    = useState(true);

      useEffect(() => {
        Promise.all([
          api.get('/api/trades?demo=false'),
          api.get('/api/trades?demo=true'),
          api.get('/api/settings')
        ]).then(([t, dt, s]) => {
          setTrades(t);
          setDemoTrades(dt);
          setSettings({...DEFAULT_SETTINGS, ...s});
          setLoading(false);
        });
      }, []);

      const addTrade = async (trade, isDemo) => {
        const newTrade = await api.post(`/api/trades?demo=${isDemo}`, trade);
        if (isDemo) setDemoTrades(ts => [...ts, newTrade]);
        else setTrades(ts => [...ts, newTrade]);
      };

      const updateTrade = async (trade, isDemo) => {
        const updatedTrade = await api.put(`/api/trades/${trade.id}`, trade);
        if (isDemo) setDemoTrades(ts => ts.map(t => t.id === trade.id ? updatedTrade : t));
        else setTrades(ts => ts.map(t => t.id === trade.id ? updatedTrade : t));
      };

      const deleteTrade = async (id, isDemo) => {
        await api.del(`/api/trades/${id}`);
        if (isDemo) setDemoTrades(ts => ts.filter(t => t.id !== id));
        else setTrades(ts => ts.filter(t => t.id !== id));
      };

      const saveSettings = async (newSettings) => {
        const updatedSettings = await api.post('/api/settings', newSettings);
        setSettings({...DEFAULT_SETTINGS, ...updatedSettings});
      };
      
      if (loading) return <div className="min-h-screen bg-gray-950 flex items-center justify-center text-white">Loading...</div>;"""
)

# App usage update
content = content.replace(
"""            {tab==='real'    &&<TradeTabContent trades={trades}     setTrades={setTrades}     settings={settings} initialBalance={settings.initialBalance}     month={month} isDemo={false} prefill={prefill?.isReal?prefill:null}    clearPrefill={()=>setPrefill(null)} />}
            {tab==='demo'    &&<TradeTabContent trades={demoTrades} setTrades={setDemoTrades} settings={settings} initialBalance={settings.demoInitialBalance} month={month} isDemo={true}  prefill={prefill&&!prefill.isReal?prefill:null} clearPrefill={()=>setPrefill(null)} />}
            {tab==='settings'&&<SettingsForm settings={settings} onSave={setSettings} />}""",
"""            {tab==='real'    &&<TradeTabContent trades={trades}     onAddTrade={(t)=>addTrade(t, false)} onUpdateTrade={(t)=>updateTrade(t, false)} onDeleteTrade={(id)=>deleteTrade(id, false)} settings={settings} initialBalance={settings.initialBalance}     month={month} isDemo={false} prefill={prefill?.isReal?prefill:null}    clearPrefill={()=>setPrefill(null)} />}
            {tab==='demo'    &&<TradeTabContent trades={demoTrades} onAddTrade={(t)=>addTrade(t, true)} onUpdateTrade={(t)=>updateTrade(t, true)} onDeleteTrade={(id)=>deleteTrade(id, true)} settings={settings} initialBalance={settings.demoInitialBalance} month={month} isDemo={true}  prefill={prefill&&!prefill.isReal?prefill:null} clearPrefill={()=>setPrefill(null)} />}
            {tab==='settings'&&<SettingsForm settings={settings} onSave={saveSettings} />}"""
)

# Footer text
content = content.replace(
"""データはブラウザの localStorage に保存されます""",
"""データはサーバーのデータベースに保存されます"""
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied.")
