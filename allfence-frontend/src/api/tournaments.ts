import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { Tournament, TournamentFilters } from '../types';

const API_URL = (import.meta.env.VITE_API_URL as string) || '/api';

export const tournamentsApi = createApi({
  reducerPath: 'tournamentsApi',
  baseQuery: fetchBaseQuery({ baseUrl: API_URL }),
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

    getTournamentParticipants: builder.query<any[], number>({
      query: (tournament_id) => `/tournaments/${tournament_id}/participants`,
      providesTags: (_, __, tournament_id) => [{ type: 'Tournament', id: tournament_id }],
    }),
  }),
});

export const {
  useGetTournamentsQuery,
  useGetTournamentByIdQuery,
  useGetTournamentParticipantsQuery,
} = tournamentsApi;
