import { motion } from 'framer-motion';
import { Search, MapPin } from 'lucide-react';
import { useState } from 'react';

export default function AnimatedSearchBar({ onSearch }: { onSearch: (q: string) => void }) {
  const [isFocused, setIsFocused] = useState(false);
  const [query, setQuery] = useState('');

  return (
    <div className="w-full max-w-2xl mx-auto relative z-20">
      <motion.div 
        animate={{ 
          y: isFocused ? -4 : 0,
          boxShadow: isFocused ? '0 20px 40px -10px rgba(0,0,0,0.3)' : '0 4px 12px rgba(0,0,0,0.1)'
        }}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        className={`flex items-center p-2 rounded-full backdrop-blur-xl border transition-colors duration-300 ${isFocused ? 'border-primary bg-background' : 'border-border bg-card'}`}
      >
        <div className="pl-4 pr-2 text-zinc-400">
          <Search size={20} />
        </div>
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          onKeyDown={(e) => e.key === 'Enter' && onSearch(query)}
          placeholder="Search for hospitals, police, schools..."
          className="flex-1 bg-transparent border-none outline-none text-foreground placeholder-zinc-500 py-3 text-lg font-sans w-full"
        />
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => onSearch(query)}
          className="bg-foreground text-background px-6 py-3 rounded-full font-semibold hover:bg-primary hover:text-white transition-colors"
        >
          Search
        </motion.button>
      </motion.div>
      
      <button className="mt-6 mx-auto flex items-center gap-2 text-zinc-400 hover:text-foreground transition-colors font-medium text-sm">
        <MapPin size={16} /> Use My Current Location
      </button>
    </div>
  );
}
