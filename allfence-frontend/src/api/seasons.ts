import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:5001/api';

export interface Season {
  season_id: number;
  name: string;
  start_date: string;
  end_date: string;
  status: 'Active' | 'Completed' | 'Upcoming';
  description?: string;
  tournament_count: number;
}

export interface CreateSeasonRequest {
  name: string;
  start_date: string;
  end_date: string;
  status?: 'Active' | 'Completed' | 'Upcoming';
  description?: string;
}

export interface SimulateSeasonRequest {
  num_tournaments?: number;
  reset_rankings?: boolean;
}

export interface SimulationStats {
  season_id: number;
  season_name: string;
  tournaments_created: number;
  total_results: number;
  avg_participants: number;
  start_date: string;
  end_date: string;
}

export const seasonsApi = createApi({
  reducerPath: 'seasonsApi',
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
  tagTypes: ['Season'],
  endpoints: (builder) => ({
    getSeasons: builder.query<Season[], void>({
      query: () => '/seasons',
      providesTags: ['Season'],
    }),

    getSeasonById: builder.query<Season, number>({
      query: (id) => `/seasons/${id}`,
      providesTags: (_, __, id) => [{ type: 'Season', id }],
    }),

    createSeason: builder.mutation<Season, CreateSeasonRequest>({
      query: (body) => ({
        url: '/seasons',
        method: 'POST',
        body,
      }),
      invalidatesTags: ['Season'],
    }),

    simulateSeason: builder.mutation<
      { message: string; statistics: SimulationStats },
      { season_id: number; options?: SimulateSeasonRequest }
    >({
      query: ({ season_id, options }) => ({
        url: `/seasons/${season_id}/simulate`,
        method: 'POST',
        body: options || {},
      }),
      // Invalidate Season tags - Ranking invalidation is handled in the component
      invalidatesTags: ['Season'],
    }),

    deleteSeason: builder.mutation<
      { message: string; tournaments_unlinked: number },
      number
    >({
      query: (season_id) => ({
        url: `/seasons/${season_id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Season'],
    }),
  }),
});

export const {
  useGetSeasonsQuery,
  useGetSeasonByIdQuery,
  useCreateSeasonMutation,
  useSimulateSeasonMutation,
  useDeleteSeasonMutation,
} = seasonsApi;
