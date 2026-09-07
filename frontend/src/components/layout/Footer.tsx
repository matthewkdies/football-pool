import { Heart } from 'lucide-react';

export function Footer() {
  return (
    <footer className="footer footer-center p-6 bg-base-200/50 text-base-content/70 border-t border-base-content/10 mt-auto text-xs">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 w-full px-4">
        <div>
          <span className="font-bold text-base-content">UCMFPTDCYAMBCMYR</span> — Uncle Charles Memorial Football Pool
        </div>
        <div className="flex items-center gap-1">
          Made with <Heart className="h-3.5 w-3.5 text-error fill-error" /> for the Dies family
        </div>
        <div className="opacity-60">
          Remember: <em>"Show me the money!!"</em>
        </div>
      </div>
    </footer>
  );
}
