import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { TournamentFilters, FencerFilters } from '../../types';

interface UiState {
  isLoading: boolean;
  tournamentFilters: TournamentFilters;
  fencerFilters: FencerFilters;
  selectedTournamentId?: number;
  selectedFencerId?: number;
  modalOpen: {
    createTournament: boolean;
    registerFencer: boolean;
    recordResults: boolean;
  };
}

const initialState: UiState = {
  isLoading: false,
  tournamentFilters: {},
  fencerFilters: {},
  modalOpen: {
    createTournament: false,
    registerFencer: false,
    recordResults: false,
  },
};

export const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setTournamentFilters: (state, action: PayloadAction<TournamentFilters>) => {
      state.tournamentFilters = action.payload;
    },
    setFencerFilters: (state, action: PayloadAction<FencerFilters>) => {
      state.fencerFilters = action.payload;
    },
    setSelectedTournament: (state, action: PayloadAction<number | undefined>) => {
      state.selectedTournamentId = action.payload;
    },
    setSelectedFencer: (state, action: PayloadAction<number | undefined>) => {
      state.selectedFencerId = action.payload;
    },
    toggleModal: (state, action: PayloadAction<{ modal: keyof typeof state.modalOpen; open: boolean }>) => {
      state.modalOpen[action.payload.modal] = action.payload.open;
    },
  },
});

export const {
  setLoading,
  setTournamentFilters,
  setFencerFilters,
  setSelectedTournament,
  setSelectedFencer,
  toggleModal,
} = uiSlice.actions;
export default uiSlice.reducer;
