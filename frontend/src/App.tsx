import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import SearchPage from './pages/SearchPage'
import ComparisonPage from './pages/ComparisonPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/comparison" element={<ComparisonPage />} />
      </Routes>
    </Layout>
  )
}

export default App


