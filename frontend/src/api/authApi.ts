import { request } from './client';
import { AuthMeResponse, MemberResponse } from '../types';

export const authApi = {
  /** Check current claim status */
  getMe: () => request<AuthMeResponse>('/api/auth/me'),

  /** List all pool members for claiming */
  getMembers: () => request<MemberResponse[]>('/api/members'),

  /** Claim identity for a member */
  claim: (memberId: number) =>
    request<MemberResponse>('/api/auth/claim', {
      method: 'POST',
      body: JSON.stringify({ member_id: memberId }),
    }),

  /** Unclaim identity and clear session cookie */
  unclaim: () =>
    request<{ status: string }>('/api/auth/unclaim', {
      method: 'POST',
    }),
};
