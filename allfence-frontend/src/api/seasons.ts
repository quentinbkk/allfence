import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_URL = (import.meta.env.VITE_API_URL as string) || '/api';

export interface Season {
  season_id: number;
  name: string;
  start_date: string;
  end_date: string;
  status: 'Active' | 'Completed' | 'Upcoming';
  description?: string;
  tournament_count: number;
}

export const seasonsApi = createApi({
  reducerPath: 'seasonsApi',
  baseQuery: fetchBaseQuery({ baseUrl: API_URL }),
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
  }),
});

export const {
  useGetSeasonsQuery,
  useGetSeasonByIdQuery,
} = seasonsApi;
