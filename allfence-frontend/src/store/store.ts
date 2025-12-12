import { configureStore } from '@reduxjs/toolkit';
import { tournamentsApi } from '../api/tournaments';
import { fencersApi } from '../api/fencers';
import { rankingsApi } from '../api/rankings';
import { clubsApi } from '../api/clubs';
import { authApi } from '../api/auth';
import { seasonsApi } from '../api/seasons';
import uiReducer from './slices/uiSlice';
import notificationReducer from './slices/notificationSlice';
import authReducer from './slices/authSlice';

export const store = configureStore({
  reducer: {
    [tournamentsApi.reducerPath]: tournamentsApi.reducer,
    [fencersApi.reducerPath]: fencersApi.reducer,
    [rankingsApi.reducerPath]: rankingsApi.reducer,
    [clubsApi.reducerPath]: clubsApi.reducer,
    [authApi.reducerPath]: authApi.reducer,
    [seasonsApi.reducerPath]: seasonsApi.reducer,
    ui: uiReducer,
    notifications: notificationReducer,
    auth: authReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(tournamentsApi.middleware)
      .concat(fencersApi.middleware)
      .concat(rankingsApi.middleware)
      .concat(clubsApi.middleware)
      .concat(authApi.middleware)
      .concat(seasonsApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
