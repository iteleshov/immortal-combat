import { configureStore } from '@reduxjs/toolkit'
import searchReducer from './searchSlice'
import uiReducer from './uiSlice'

export const store = configureStore({
  reducer: {
    search: searchReducer,
    ui: uiReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch


