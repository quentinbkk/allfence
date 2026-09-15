import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { Club } from '../types';

const API_URL = (import.meta.env.VITE_API_URL as string) || '/api';

interface CumulativePointsData {
  date: string;
  tournament_name: string;
  points_earned: number;
  cumulative_points: number;
}

export const clubsApi = createApi({
  reducerPath: 'clubsApi',
  baseQuery: fetchBaseQuery({ baseUrl: API_URL }),
  tagTypes: ['Club'],
  endpoints: (builder) => ({
    getClubs: builder.query<Club[], void>({
      query: () => '/clubs',
      providesTags: ['Club'],
    }),

    getClubById: builder.query<Club, string>({
      query: (id) => `/clubs/${id}`,
      providesTags: (_, __, id) => [{ type: 'Club', id }],
    }),

    getClubCumulativePoints: builder.query<CumulativePointsData[], string>({
      query: (clubId) => `/clubs/${clubId}/cumulative-points`,
      providesTags: (_, __, clubId) => [{ type: 'Club', id: clubId }],
    }),
  }),
});

export const { useGetClubsQuery, useGetClubByIdQuery, useGetClubCumulativePointsQuery } = clubsApi;
