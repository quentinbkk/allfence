import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { Ranking, ClubRanking } from '../types';

const API_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:5001/api';

interface ClubCumulativePoint {
  date: string;
  cumulative_points: number;
}

interface ClubCumulativeData {
  club_id: string;
  club_name: string;
  data: ClubCumulativePoint[];
}

interface FencerCumulativePoint {
  date: string;
  tournament_name: string;
  points_awarded: number;
  cumulative_points: number;
}

export interface FencerCumulativeData {
  fencer_id: number;
  fencer_name: string;
  current_points: number;
  data: FencerCumulativePoint[];
}

export const rankingsApi = createApi({
  reducerPath: 'rankingsApi',
  baseQuery: fetchBaseQuery({
    baseUrl: API_URL,
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        headers.set('Authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['Ranking'],
  endpoints: (builder) => ({
    getRankings: builder.query<Ranking[], { bracket?: string; weapon?: string }>({
      query: ({ bracket, weapon }) => {
        const params = new URLSearchParams();
        if (bracket) params.append('bracket', bracket);
        if (weapon) params.append('weapon', weapon);
        return `/rankings?${params.toString()}`;
      },
      providesTags: ['Ranking'],
    }),

    getFencerRankings: builder.query<Ranking[], number>({
      query: (fencer_id) => `/fencers/${fencer_id}/rankings`,
      providesTags: ['Ranking'],
    }),

    getClubRankings: builder.query<ClubRanking[], { weapon?: string }>({
      query: ({ weapon }) => {
        const params = new URLSearchParams();
        if (weapon) params.append('weapon', weapon);
        return `/rankings/clubs?${params.toString()}`;
      },
      providesTags: ['Ranking'],
    }),

    getAllClubsCumulativePoints: builder.query<ClubCumulativeData[], { weapon: string }>({
      query: ({ weapon }) => {
        const params = new URLSearchParams();
        params.append('weapon', weapon);
        return `/rankings/clubs/cumulative-points?${params.toString()}`;
      },
      providesTags: ['Ranking'],
    }),

    getTopFencersCumulativePoints: builder.query<FencerCumulativeData[], { bracket: string; weapon?: string; gender?: string; limit?: number }>({
      query: ({ bracket, weapon, gender, limit = 10 }) => {
        const params = new URLSearchParams();
        params.append('bracket', bracket);
        if (weapon) params.append('weapon', weapon);
        if (gender) params.append('gender', gender);
        params.append('limit', limit.toString());
        return `/rankings/cumulative-points?${params.toString()}`;
      },
      providesTags: ['Ranking'],
    }),

    resetAllRankings: builder.mutation<
      { message: string; rankings_reset: number },
      void
    >({
      query: () => ({
        url: '/rankings/reset',
        method: 'POST',
      }),
      invalidatesTags: ['Ranking'],
    }),
  }),
});

export const {
  useGetRankingsQuery,
  useGetFencerRankingsQuery,
  useGetClubRankingsQuery,
  useGetAllClubsCumulativePointsQuery,
  useGetTopFencersCumulativePointsQuery,
  useResetAllRankingsMutation,
} = rankingsApi;
