import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { GeneResponse, SearchState } from '../types'
import { searchGene } from '../services/api'

const initialState: SearchState = {
  currentGene: null,
  loading: false,
  error: null,
  searchHistory: [],
}

export const fetchGene = createAsyncThunk(
  'search/fetchGene',
  async (geneName: string) => {
    const response = await searchGene(geneName)
    return response
  }
)

const searchSlice = createSlice({
  name: 'search',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearCurrentGene: (state) => {
      state.currentGene = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchGene.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchGene.fulfilled, (state, action: PayloadAction<GeneResponse>) => {
        state.loading = false
        state.currentGene = action.payload
        if (!state.searchHistory.includes(action.payload.gene)) {
          state.searchHistory.unshift(action.payload.gene)
          if (state.searchHistory.length > 10) {
            state.searchHistory.pop()
          }
        }
      })
      .addCase(fetchGene.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to fetch gene data'
      })
  },
})

export const { clearError, clearCurrentGene } = searchSlice.actions
export default searchSlice.reducer


