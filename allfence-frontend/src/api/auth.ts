import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_URL = (import.meta.env.VITE_API_URL as string) || 'http://localhost:5001/api';

interface LoginRequest {
  username: string;
  password: string;
}

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

interface AuthResponse {
  token: string;
  user: {
    user_id: number;
    username: string;
    email: string;
    is_admin: boolean;
  };
}

export const authApi = createApi({
  reducerPath: 'authApi',
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
  tagTypes: ['Auth'],
  endpoints: (builder) => ({
    login: builder.mutation<AuthResponse, LoginRequest>({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    register: builder.mutation<AuthResponse, RegisterRequest>({
      query: (userData) => ({
        url: '/auth/register',
        method: 'POST',
        body: userData,
      }),
    }),
    getCurrentUser: builder.query<AuthResponse['user'], void>({
      query: () => '/auth/me',
      providesTags: ['Auth'],
    }),
  }),
});

export const { useLoginMutation, useRegisterMutation, useGetCurrentUserQuery } = authApi;
