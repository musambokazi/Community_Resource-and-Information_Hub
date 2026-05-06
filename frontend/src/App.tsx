import { useState, useEffect } from 'react';
import { motion, LayoutGroup } from 'framer-motion';
import AnimatedSearchBar from './components/AnimatedSearchBar';
import ResourceCard from './components/ResourceCard';

function App() {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchNearby = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:5000/api/nearby');
      const data = await res.json();
      if (data.success) setResources(data.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleSearch = async (query: string) => {
    if (!query) return;
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:5000/api/search?q=${query}`);
      const data = await res.json();
      if (data.success) setResources(data.data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchNearby();
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground font-sans selection:bg-primary/30 relative overflow-hidden">
      {/* Dynamic Background Blobs */}
      <div className="fixed top-[-10%] left-[-10%] w-[600px] h-[600px] bg-[#431407] rounded-full blur-[120px] opacity-40 -z-10 animate-[pulse_8s_ease-in-out_infinite]" />
      <div className="fixed bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-[#1e1b4b] rounded-full blur-[120px] opacity-40 -z-10 animate-[pulse_12s_ease-in-out_infinite_alternate]" />

      <nav className="flex justify-between items-center px-8 py-6 max-w-7xl mx-auto backdrop-blur-md sticky top-0 z-50 bg-background/50 border-b border-border">
        <div className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <span className="text-primary text-3xl">✦</span>
          Community Hub
        </div>
        <div className="flex gap-4">
          <button className="px-5 py-2 rounded-full border border-border bg-card hover:bg-white hover:text-black transition-colors font-medium text-sm">
            Log In
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 pt-24 pb-32">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-gradient-to-br from-white to-zinc-500 bg-clip-text text-transparent">
            Find What You Need,<br/>Right Now.
          </h1>
          <p className="text-lg md:text-xl text-zinc-400 max-w-2xl mx-auto font-medium">
            Discover essential services, verify live operating hours, and navigate your neighborhood with confidence.
          </p>
        </motion.div>

        <AnimatedSearchBar onSearch={handleSearch} />

        <div className="mt-24">
          <h3 className="text-2xl font-bold tracking-tight mb-8 pl-2 border-l-4 border-primary">Nearby Resources</h3>
          
          {loading ? (
            <div className="flex justify-center items-center h-40">
              <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <LayoutGroup>
              <motion.div 
                layout
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
              >
                {resources.map((res: any, idx: number) => (
                  <motion.div
                    layout
                    key={res.place_id || idx}
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ 
                      delay: idx * 0.05,
                      type: 'spring',
                      stiffness: 260,
                      damping: 20
                    }}
                  >
                    <ResourceCard resource={res} />
                  </motion.div>
                ))}
              </motion.div>
            </LayoutGroup>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
