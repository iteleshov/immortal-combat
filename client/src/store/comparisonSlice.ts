import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { ComparisonResponse, ComparisonState } from '../types'
import { compareGenes } from '../services/api'

const initialState: ComparisonState = {
  selectedGenes: [],
  comparisonResult: null,
  loading: false,
  error: null,
}

export const fetchComparison = createAsyncThunk(
  'comparison/fetchComparison',
  async (genes: string[]) => {
    const response = await compareGenes(genes)
    return response
  }
)

const comparisonSlice = createSlice({
  name: 'comparison',
  initialState,
  reducers: {
    addGene: (state, action: PayloadAction<string>) => {
      if (!state.selectedGenes.includes(action.payload) && state.selectedGenes.length < 4) {
        state.selectedGenes.push(action.payload)
      }
    },
    removeGene: (state, action: PayloadAction<string>) => {
      state.selectedGenes = state.selectedGenes.filter(g => g !== action.payload)
    },
    clearSelectedGenes: (state) => {
      state.selectedGenes = []
      state.comparisonResult = null
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchComparison.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchComparison.fulfilled, (state, action: PayloadAction<ComparisonResponse>) => {
        state.loading = false
        state.comparisonResult = action.payload
      })
      .addCase(fetchComparison.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || 'Failed to compare genes'
      })
  },
})

export const { addGene, removeGene, clearSelectedGenes, clearError } = comparisonSlice.actions
export default comparisonSlice.reducer


