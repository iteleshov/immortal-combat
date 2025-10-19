import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { UIState } from '../types'

const initialState: UIState = {
  sidebarOpen: false,
  activeTab: 'search',
  theme: 'light',
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen
    },
    setActiveTab: (state, action: PayloadAction<'search' | 'comparison'>) => {
      state.activeTab = action.payload
    },
    closeSidebar: (state) => {
      state.sidebarOpen = false
    },
  },
})

export const { toggleSidebar, setActiveTab, closeSidebar } = uiSlice.actions
export default uiSlice.reducer


