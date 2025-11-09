import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Dna, Bot } from 'lucide-react'
import { useAppSelector, useAppDispatch } from '../hooks'
import { toggleSidebar, setActiveTab, closeSidebar } from '../store/uiSlice'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const dispatch = useAppDispatch()
  const { sidebarOpen } = useAppSelector(state => state.ui)
  const location = useLocation()

  const navigation = [
    { name: 'Search', href: '/', icon: Dna, tab: 'search' as const },
    {name: 'RAG Assistant', href: '/rag', icon: Bot, tab: 'rag' as const},
  ]

  // Enhance hover and focus states for navigation links
  const enhancedNavigation = navigation.map((item) => ({
    ...item,
    hoverClass: 'transition duration-200 ease-in-out transform hover:scale-105 hover:shadow-md',
  }))

  return (
    <div className="min-h-screen bg-background-default text-text-primary">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-background-card bg-opacity-75" onClick={() => dispatch(closeSidebar())} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-background-card shadow-xl">
          <div className="flex h-16 items-center justify-between px-4">
            <h1 className="text-xl font-bold text-text-primary">Gene Knowledge Base</h1>
            <button
              onClick={() => dispatch(closeSidebar())}
              className="rounded-md p-2 text-text-secondary hover:text-text-primary"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          <nav className="flex-1 px-4 py-4">
            {enhancedNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => {
                  dispatch(setActiveTab(item.tab))
                  dispatch(closeSidebar())
                }}
                className={`mb-2 flex items-center rounded-md px-3 py-2 text-sm font-medium ${
                  location.pathname === item.href
                    ? 'bg-primary-500 text-text-primary'
                    : `text-text-secondary hover:bg-background-card hover:text-text-primary ${item.hoverClass}`
                }`}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-background-card shadow-lg">
          <div className="flex h-16 items-center px-4">
            <h1 className="text-xl font-bold text-text-primary">Gene Knowledge Base</h1>
          </div>
          <nav className="flex-1 px-4 py-4">
            {enhancedNavigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => dispatch(setActiveTab(item.tab))}
                className={`mb-2 flex items-center rounded-md px-3 py-2 text-sm font-medium ${
                  location.pathname === item.href
                    ? 'bg-primary-500 text-text-primary'
                    : `text-text-secondary hover:bg-background-card hover:text-text-primary ${item.hoverClass}`
                }`}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Mobile header */}
        <div className="flex h-16 items-center justify-between bg-background-card px-4 shadow-sm lg:hidden">
          <button
            onClick={() => dispatch(toggleSidebar())}
            className="rounded-md p-2 text-text-secondary hover:text-text-primary"
          >
            <Menu className="h-6 w-6" />
          </button>
          <h1 className="text-lg font-semibold text-text-primary">Gene Knowledge Base</h1>
          <div className="w-10" /> {/* Spacer for centering */}
        </div>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}

