import { Award, BookOpen, PhoneCall, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export function AboutPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      {/* Page Title */}
      <div className="text-center max-w-2xl mx-auto mb-10">
        <h1 className="text-3xl sm:text-4xl font-black text-base-content tracking-tight">
          About the Pool & Rules
        </h1>
        <p className="text-xs sm:text-sm text-base-content/70 mt-2 font-medium">
          The storied history and official guidelines of the <strong>UCMFPTDCYAMBCMYR</strong>.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-stretch">
        {/* Card 1: Storied History */}
        <div className="card bg-base-100 border border-base-content/10 shadow-sm flex flex-col">
          <div className="p-6 sm:p-8 flex-1">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-primary/10 text-primary rounded-xl">
                <BookOpen className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Storied History</h2>
                <span className="text-xs text-base-content/60">From the 1980s to Today</span>
              </div>
            </div>

            <div className="prose prose-sm max-w-none text-base-content/85 space-y-4 leading-relaxed">
              <p className="font-semibold text-base text-base-content">
                The UCMFPTDCYAMBCMYR has a storied history ranging from CPA-certified blind drawings to lobster and steak dinners.
              </p>

              <p>
                The football pool originally began in the &apos;80s, started by <strong>Uncle Charles</strong>. Original rules were very similar, with the notable exception of the playoffs; originally most and least weeks continued into the playoffs! At its peak, the original league had about 30 members.
              </p>

              <p>
                Fast-forward a few years, and <strong>Grandma and Grandpa</strong> brought the pool back! To honor Uncle Charles, they renamed the pool to commemorate his great contributions to football enjoyment and familial bonding:
              </p>

              <div className="p-4 bg-base-200/80 rounded-xl border border-base-content/10 font-bold text-center text-primary text-sm sm:text-base">
                &ldquo;Uncle Charles Memorial Football Pool That Doesn&apos;t Cost You Any Money But Can Make You Rich&rdquo;
              </div>

              <p>
                Verbose? Definitely. Accurate? Also definitely! Traditionally, each season begins with an extravagant lobster and steak dinner at which the drawing occurs. Unfortunately, the invites always arrive <em>after</em> the drawing and dinner. I guess they must have a lot of leftovers.
              </p>

              <div className="divider my-4"></div>

              <h3 className="font-bold text-base text-base-content flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-warning" />
                League Folklore & Tidbits
              </h3>

              <ul className="list-disc list-inside space-y-1.5 text-xs text-base-content/80">
                <li><strong>Aunt Katherine</strong> made shirts after the league&apos;s return!</li>
                <li>The drawings are CPA-certified blind drawings. According to Grandma, at least.</li>
                <li>During one selection party, the teams and names were in bowls out on the deck. A sudden gust of wind sent both bowls and their contents flying!</li>
              </ul>
            </div>
          </div>

          <div className="p-4 bg-base-200/40 border-t border-base-content/10 text-center">
            <Link to="/assignments" className="btn btn-sm btn-ghost text-primary font-semibold">
              View Current Team Assignments →
            </Link>
          </div>
        </div>

        {/* Card 2: Official Rules */}
        <div className="card bg-base-100 border border-base-content/10 shadow-sm flex flex-col">
          <div className="p-6 sm:p-8 flex-1">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 bg-secondary/10 text-secondary rounded-xl">
                <Award className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Official Rules</h2>
                <span className="text-xs text-base-content/60">How to Win (and Claim) the Cash</span>
              </div>
            </div>

            <div className="prose prose-sm max-w-none text-base-content/85 space-y-4 leading-relaxed">
              <p>
                The first week of the regular season is a <strong>&ldquo;Most&rdquo;</strong> week, and the following week is a <strong>&ldquo;Least&rdquo;</strong> week. This pattern alternates weekly until the playoffs begin.
              </p>

              {/* Rules List */}
              <div className="space-y-3 mt-4">
                <div className="flex items-start gap-3 p-3 bg-base-200/60 rounded-xl">
                  <span className="badge badge-primary font-bold shrink-0 mt-0.5">1</span>
                  <div className="text-xs sm:text-sm">
                    <strong>Most Points Week:</strong> If your team scores the most points of all 32 teams, you win <strong>$10</strong>.
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-base-200/60 rounded-xl">
                  <span className="badge badge-primary font-bold shrink-0 mt-0.5">2</span>
                  <div className="text-xs sm:text-sm">
                    <strong>Least Points Week:</strong> If your team scores the least points of all 32 teams, you win <strong>$10</strong>.
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-base-200/60 rounded-xl">
                  <span className="badge badge-accent font-bold shrink-0 mt-0.5">3</span>
                  <div className="text-xs sm:text-sm">
                    <strong>The 50-Point Bonus:</strong> If your team scores exactly 50 or more points, you win <strong>$50</strong>!
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-base-200/60 rounded-xl">
                  <span className="badge badge-neutral font-bold shrink-0 mt-0.5">4</span>
                  <div className="text-xs sm:text-sm">
                    <strong>Rolling Pot:</strong> If no pool member owns the winning team, the pot rolls over into the next week!
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-base-200/60 rounded-xl">
                  <span className="badge badge-primary font-bold shrink-0 mt-0.5">5</span>
                  <div className="text-xs sm:text-sm">
                    <strong>Playoffs:</strong> Every playoff game won by your team earns you <strong>$15</strong>.
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-base-200/60 rounded-xl">
                  <span className="badge badge-warning font-bold shrink-0 mt-0.5">6</span>
                  <div className="text-xs sm:text-sm">
                    <strong>Super Bowl:</strong> The Super Bowl champion owner wins <strong>$25</strong>!
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-base-200/60 rounded-xl opacity-75">
                  <span className="badge badge-ghost font-bold shrink-0 mt-0.5">7</span>
                  <div className="text-xs sm:text-sm">
                    <strong>Developer Bounty:</strong> For rebuilding this website, Matt gets <strong>$10,000</strong>! (Pending grandparents&apos; approval.)
                  </div>
                </div>
              </div>

              {/* The Grandma Rule Alert */}
              <div className="mt-6 p-4 bg-warning/15 border border-warning/40 rounded-2xl flex items-start gap-3">
                <PhoneCall className="h-6 w-6 text-warning shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-sm text-base-content">
                    The Golden Grandma Rule:
                  </h4>
                  <p className="text-xs text-base-content/85 mt-1 font-semibold">
                    &ldquo;If you win, you have to call Grandma and tell her: SHOW ME THE MONEY!!&rdquo;
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="p-4 bg-base-200/40 border-t border-base-content/10 text-center">
            <Link to="/results" className="btn btn-sm btn-ghost text-primary font-semibold">
              Check Season Standings & Winners →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
