import { DollarSign } from 'lucide-react';

interface PotCardProps {
  amount: number;
  seasonYear: number;
}

export function PotCard({ amount, seasonYear }: PotCardProps) {
  return (
    <div className="bg-gradient-to-r from-success/15 via-base-200 to-base-200 border border-success/30 rounded-2xl p-5 mb-6 shadow-sm flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="p-3 bg-success/20 text-success rounded-xl">
          <DollarSign className="h-8 w-8" />
        </div>
        <div>
          <div className="text-xs uppercase font-bold tracking-wider text-base-content/60">
            {seasonYear}-{seasonYear + 1} Rolling Pot
          </div>
          <div className="text-3xl sm:text-4xl font-black font-mono text-success">
            ${amount}
          </div>
        </div>
      </div>
      <div className="text-xs text-base-content/60 max-w-xs text-right hidden sm:block">
        Unclaimed weekly pots roll over into the next week, raising the stakes!
      </div>
    </div>
  );
}
