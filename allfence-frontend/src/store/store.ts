import { configureStore } from '@reduxjs/toolkit';
import { tournamentsApi } from '../api/tournaments';
import { fencersApi } from '../api/fencers';
import { rankingsApi } from '../api/rankings';
import { clubsApi } from '../api/clubs';
import { seasonsApi } from '../api/seasons';
import uiReducer from './slices/uiSlice';
import notificationReducer from './slices/notificationSlice';

export const store = configureStore({
  reducer: {
    [tournamentsApi.reducerPath]: tournamentsApi.reducer,
    [fencersApi.reducerPath]: fencersApi.reducer,
    [rankingsApi.reducerPath]: rankingsApi.reducer,
    [clubsApi.reducerPath]: clubsApi.reducer,
    [seasonsApi.reducerPath]: seasonsApi.reducer,
    ui: uiReducer,
    notifications: notificationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware()
      .concat(tournamentsApi.middleware)
      .concat(fencersApi.middleware)
      .concat(rankingsApi.middleware)
      .concat(clubsApi.middleware)
      .concat(seasonsApi.middleware),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
