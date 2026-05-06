import { motion } from 'framer-motion';
import { MapPin, Info, Star } from 'lucide-react';
import { useState } from 'react';

export default function ResourceCard({ resource }: { resource: any }) {
  const [isHovered, setIsHovered] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);

  return (
    <motion.div
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{ y: -8, scale: 1.01 }}
      transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      className="relative flex flex-col p-5 bg-card backdrop-blur-2xl border border-border rounded-3xl overflow-hidden cursor-pointer shadow-[0_8px_32px_-8px_rgba(0,0,0,0.3)] h-full"
    >
      <motion.div 
        className="absolute inset-0 rounded-3xl pointer-events-none"
        initial={{ opacity: 0 }}
        animate={{ opacity: isHovered ? 1 : 0 }}
        style={{ boxShadow: 'inset 0 1px 1px rgba(255, 255, 255, 0.15)' }}
      />

      <div className="relative w-full h-48 rounded-2xl overflow-hidden mb-4 shrink-0">
        <motion.img 
          src={resource.image} 
          alt={resource.title}
          animate={{ scale: isHovered ? 1.05 : 1 }}
          transition={{ duration: 0.4, ease: [0.2, 0.8, 0.2, 1] }}
          className="w-full h-full object-cover"
        />
        <motion.button 
          whileTap={{ scale: 0.9 }}
          onClick={(e) => { e.stopPropagation(); setIsFavorited(!isFavorited); }}
          className="absolute top-3 right-3 p-2 bg-black/40 backdrop-blur-md rounded-full text-zinc-400 hover:text-yellow-400 transition-colors z-10"
        >
          <Star className={isFavorited ? "fill-yellow-400 text-yellow-400" : ""} size={18} />
        </motion.button>
      </div>

      <h2 className="text-xl font-semibold text-foreground tracking-tight mb-2 line-clamp-2">{resource.title}</h2>
      
      <div className="flex items-center gap-2 mb-3">
        <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-background border border-border text-xs font-medium">
          <div className={`w-2 h-2 rounded-full ${resource.is_open ? 'bg-green-500' : 'bg-red-500'}`} />
          {resource.is_open ? 'Open Now' : 'Closed'}
        </span>
      </div>

      <p className="text-zinc-400 text-sm mb-6 flex-grow leading-relaxed line-clamp-3">{resource.desc}</p>

      <div className="flex gap-3 mt-auto pt-4 border-t border-border/50">
        <a 
          href={`https://www.google.com/maps/dir/?api=1&destination=${resource.lat},${resource.lon}`}
          target="_blank"
          rel="noreferrer"
          className="flex-1 flex justify-center items-center gap-2 bg-background border border-border py-2.5 rounded-xl text-sm font-medium hover:bg-foreground hover:text-background transition-colors"
          onClick={(e) => e.stopPropagation()}
        >
          <MapPin size={16} /> Directions
        </a>
        <button className="flex-1 flex justify-center items-center gap-2 bg-background border border-border py-2.5 rounded-xl text-sm font-medium text-primary hover:bg-primary hover:text-white transition-colors">
          <Info size={16} /> Details
        </button>
      </div>
    </motion.div>
  );
}
