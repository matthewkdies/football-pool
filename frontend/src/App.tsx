import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { SeasonProvider } from './context/SeasonContext';
import { ChatProvider } from './context/ChatContext';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { ClaimProfileModal } from './components/auth/ClaimProfileModal';
import { ChatDrawer } from './components/chat/ChatDrawer';
import { ScoreboardPage } from './pages/ScoreboardPage';
import { ResultsPage } from './pages/ResultsPage';
import { AssignmentsPage } from './pages/AssignmentsPage';
import { AboutPage } from './pages/AboutPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <SeasonProvider>
          <ChatProvider>
            <div className="flex flex-col min-h-screen bg-base-100 text-base-content antialiased">
              {/* Global Navigation Bar */}
              <Navbar />

              {/* Main Content View */}
              <main className="flex-1">
                <Routes>
                  <Route path="/" element={<ScoreboardPage />} />
                  <Route path="/results" element={<ResultsPage />} />
                  <Route path="/assignments" element={<AssignmentsPage />} />
                  <Route path="/about" element={<AboutPage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </main>

              {/* Global Footer */}
              <Footer />

              {/* Modals & Slide-out Drawers */}
              <ChatDrawer />
              <ClaimProfileModal />
            </div>
          </ChatProvider>
        </SeasonProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}
