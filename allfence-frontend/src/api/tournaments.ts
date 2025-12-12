import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { Tournament, TournamentFilters } from '../types';

const API_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:5001/api';

export const tournamentsApi = createApi({
  reducerPath: 'tournamentsApi',
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
  tagTypes: ['Tournament'],
  endpoints: (builder) => ({
    getTournaments: builder.query<Tournament[], TournamentFilters | void>({
      query: (filters) => {
        const params = new URLSearchParams();
        if (filters) {
          if (filters.status) params.append('status', filters.status);
          if (filters.weapon) params.append('weapon', filters.weapon);
          if (filters.bracket) params.append('bracket', filters.bracket);
          if (filters.search) params.append('search', filters.search);
        }
        return `/tournaments${params.toString() ? '?' + params.toString() : ''}`;
      },
      providesTags: ['Tournament'],
    }),

    getTournamentById: builder.query<Tournament, number>({
      query: (id) => `/tournaments/${id}`,
      providesTags: (_, __, id) => [{ type: 'Tournament', id }],
    }),

    createTournament: builder.mutation<Tournament, Partial<Tournament>>({
      query: (tournament) => ({
        url: '/tournaments',
        method: 'POST',
        body: tournament,
      }),
      invalidatesTags: ['Tournament'],
    }),

    updateTournament: builder.mutation<Tournament, { id: number; data: Partial<Tournament> }>({
      query: ({ id, data }) => ({
        url: `/tournaments/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'Tournament', id }],
    }),

    deleteTournament: builder.mutation<void, number>({
      query: (id) => ({
        url: `/tournaments/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Tournament'],
    }),

    registerFencer: builder.mutation<{ message: string }, { tournament_id: number; fencer_id: number }>({
      query: ({ tournament_id, fencer_id }) => ({
        url: `/tournaments/${tournament_id}/register`,
        method: 'POST',
        body: { fencer_id },
      }),
      invalidatesTags: (_, __, { tournament_id }) => [{ type: 'Tournament', id: tournament_id }],
    }),

    getTournamentParticipants: builder.query<any[], number>({
      query: (tournament_id) => `/tournaments/${tournament_id}/participants`,
      providesTags: (_, __, tournament_id) => [{ type: 'Tournament', id: tournament_id }],
    }),

    unregisterFencer: builder.mutation<{ message: string }, { tournament_id: number; fencer_id: number }>({
      query: ({ tournament_id, fencer_id }) => ({
        url: `/tournaments/${tournament_id}/participants/${fencer_id}`,
        method: 'DELETE',
      }),
      invalidatesTags: (_, __, { tournament_id }) => [{ type: 'Tournament', id: tournament_id }],
    }),

    recordResults: builder.mutation<
      { message: string; updated_count: number; errors?: string[] },
      { tournament_id: number; results: { fencer_id: number; placement: number }[] }
    >({
      query: ({ tournament_id, results }) => ({
        url: `/tournaments/${tournament_id}/results`,
        method: 'POST',
        body: { results },
      }),
      invalidatesTags: (_, __, { tournament_id }) => [{ type: 'Tournament', id: tournament_id }],
    }),
  }),
});

export const {
  useGetTournamentsQuery,
  useGetTournamentByIdQuery,
  useCreateTournamentMutation,
  useUpdateTournamentMutation,
  useDeleteTournamentMutation,
  useRegisterFencerMutation,
  useGetTournamentParticipantsQuery,
  useUnregisterFencerMutation,
  useRecordResultsMutation,
} = tournamentsApi;
