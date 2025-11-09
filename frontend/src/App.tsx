import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import SearchPage from './pages/SearchPage'
import RAGPage from './pages/RAGPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/gene/:geneName" element={<SearchPage />} />
        <Route path="/rag" element={<RAGPage />} />
      </Routes>
    </Layout>
  )
}

export default App


