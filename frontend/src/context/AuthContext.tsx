import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { AuthMeResponse, MemberResponse } from '../types';
import { authApi } from '../api/authApi';

interface AuthContextType {
  auth: AuthMeResponse | null;
  isLoading: boolean;
  members: MemberResponse[];
  isClaimModalOpen: boolean;
  openClaimModal: () => void;
  closeClaimModal: () => void;
  claim: (memberId: number) => Promise<void>;
  unclaim: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthMeResponse | null>(null);
  const [members, setMembers] = useState<MemberResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isClaimModalOpen, setIsClaimModalOpen] = useState<boolean>(false);

  const refreshAuth = useCallback(async () => {
    try {
      const data = await authApi.getMe();
      setAuth(data);
    } catch {
      setAuth({ claimed: false, member: null, current_team: null });
    }
  }, []);

  const loadMembers = useCallback(async () => {
    try {
      const list = await authApi.getMembers();
      setMembers(list);
    } catch {
      setMembers([]);
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      await Promise.all([refreshAuth(), loadMembers()]);
      setIsLoading(false);
    };
    init();
  }, [refreshAuth, loadMembers]);

  const claim = async (memberId: number) => {
    await authApi.claim(memberId);
    await refreshAuth();
    setIsClaimModalOpen(false);
  };

  const unclaim = async () => {
    await authApi.unclaim();
    await refreshAuth();
  };

  return (
    <AuthContext.Provider
      value={{
        auth,
        isLoading,
        members,
        isClaimModalOpen,
        openClaimModal: () => setIsClaimModalOpen(true),
        closeClaimModal: () => setIsClaimModalOpen(false),
        claim,
        unclaim,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
