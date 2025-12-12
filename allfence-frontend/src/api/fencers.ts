import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { Fencer, FencerFilters } from '../types';

const API_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:5001/api';

export const fencersApi = createApi({
  reducerPath: 'fencersApi',
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
  tagTypes: ['Fencer'],
  endpoints: (builder) => ({
    getFencers: builder.query<Fencer[], FencerFilters | void>({
      query: (filters) => {
        const params = new URLSearchParams();
        if (filters) {
          if (filters.weapon) params.append('weapon', filters.weapon);
          if (filters.bracket) params.append('bracket', filters.bracket);
          if (filters.gender) params.append('gender', filters.gender);
          if (filters.club_id) params.append('club_id', filters.club_id);
          if (filters.search) params.append('search', filters.search);
        }
        return `/fencers${params.toString() ? '?' + params.toString() : ''}`;
      },
      providesTags: ['Fencer'],
    }),

    getFencerById: builder.query<Fencer, number>({
      query: (id) => `/fencers/${id}`,
      providesTags: (_, __, id) => [{ type: 'Fencer', id }],
    }),

    updateFencer: builder.mutation<Fencer, { id: number; data: Partial<Fencer> }>({
      query: ({ id, data }) => ({
        url: `/fencers/${id}`,
        method: 'PUT',
        body: data,
      }),
      invalidatesTags: (_, __, { id }) => [{ type: 'Fencer', id }],
    }),

    getFencerResults: builder.query<any[], number>({
      query: (id) => `/fencers/${id}/results`,
      providesTags: (_, __, id) => [{ type: 'Fencer', id }],
    }),

    getFencerUpcomingTournaments: builder.query<any[], number>({
      query: (id) => `/fencers/${id}/upcoming-tournaments`,
      providesTags: (_, __, id) => [{ type: 'Fencer', id }],
    }),
  }),
});

export const {
  useGetFencersQuery,
  useGetFencerByIdQuery,
  useUpdateFencerMutation,
  useGetFencerResultsQuery,
  useGetFencerUpcomingTournamentsQuery,
} = fencersApi;
