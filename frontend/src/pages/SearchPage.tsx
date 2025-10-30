import { useState } from 'react'
import { Search, Loader2, AlertCircle } from 'lucide-react'
import { useAppSelector, useAppDispatch } from '../hooks'
import { fetchGene, clearError } from '../store/searchSlice'
import { validateGeneName } from '../services/api'
import GeneResults from '../components/GeneResults'
import logo from '../assets/gene-lens-logo.png'

export default function SearchPage() {
  const dispatch = useAppDispatch()
  const { currentGene, loading, error, searchHistory } =
    useAppSelector(state => state.search)
  const [searchTerm, setSearchTerm] = useState('')
  const [validationError, setValidationError] = useState('')

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!searchTerm.trim()) {
      setValidationError('Please enter a gene name')
      return
    }

    if (!validateGeneName(searchTerm)) {
      setValidationError('Invalid gene name format. Use letters, numbers, and hyphens only.')
      return
    }

    setValidationError('')
    dispatch(clearError())
    dispatch(fetchGene(searchTerm.trim().toUpperCase()))
  }

  const handleHistoryClick = (gene: string) => {
    setSearchTerm(gene)
    dispatch(fetchGene(gene))
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-center justify-center mt-6 sm:mt-10 mb-8 sm:mb-12
                      text-center sm:text-left space-y-3 sm:space-y-0 sm:space-x-4">
        <img
          src={logo}
          alt="GeneLens logo"
          className="w-14 h-14 sm:w-16 sm:h-16 object-contain rounded"
        />
        <h1 className="text-3xl sm:text-4xl font-bold text-gray-900">
          Gene<span className="text-primary-600">Lens</span>
        </h1>
      </div>

      {/* Description */}
      <div className="text-center mb-8 sm:mb-12">
        <p className="text-gray-600 text-sm sm:text-base max-w-2xl mx-auto px-2">
          Search for genes and proteins to explore their sequence-to-function relationships in longevity research.
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border p-4 sm:p-6 mb-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div>
            <label htmlFor="gene-search" className="block text-sm font-medium text-gray-700 mb-2">
              Gene Name or Symbol
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="gene-search"
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value)
                  setValidationError('')
                }}
                placeholder="Enter gene name (e.g., NFE2L2, APOE, SOX2)"
                className="block w-full pl-10 pr-3 py-2.5 sm:py-3 border border-gray-300 rounded-md shadow-sm
                           focus:ring-primary-500 focus:border-primary-500 text-sm sm:text-base"
                disabled={loading}
              />
            </div>
            {validationError && (
              <p className="mt-2 text-sm text-red-600">{validationError}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading || !searchTerm.trim()}
            className="w-full flex justify-center items-center px-4 py-2.5 sm:py-3 border border-transparent
                       rounded-md shadow-sm text-sm sm:text-base font-medium text-gray-700 bg-primary-600
                       hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2
                       focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer
                       transition-colors duration-200"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
                Searching...
              </>
            ) : (
              'Search Gene'
            )}
          </button>
        </form>

        {/* Error */}
        {error && (
          <div className="mt-4 p-3 sm:p-4 bg-red-50 border border-red-200 rounded-md text-sm sm:text-base">
            <div className="flex flex-col sm:flex-row sm:items-start">
              <AlertCircle className="h-5 w-5 text-red-400 flex-shrink-0" />
              <div className="sm:ml-3 mt-2 sm:mt-0">
                <h3 className="font-medium text-red-800">Search Error</h3>
                <p className="text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Search History */}
        {searchHistory.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm sm:text-base font-medium text-gray-700 mb-3">Recent Searches</h3>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((gene) => (
                <button
                  key={gene}
                  onClick={() => handleHistoryClick(gene)}
                  className="inline-flex items-center px-3 py-1.5 rounded-full text-xs sm:text-sm
                             font-medium bg-gray-100 text-gray-800 hover:bg-gray-200 transition-colors"
                >
                  {gene}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {currentGene && <GeneResults gene={currentGene} />}

      {/* Example Genes */}
      {!currentGene && !loading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 sm:p-6 mb-8">
          <h3 className="text-base sm:text-lg font-medium text-blue-900 mb-3">Try these example genes:</h3>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {['NFE2L2', 'APOE', 'SOX2', 'OCT4'].map((gene) => (
              <button
                key={gene}
                onClick={() => {
                  setSearchTerm(gene)
                  dispatch(fetchGene(gene))
                }}
                className="p-3 text-center bg-white rounded-lg border
                           border-blue-300 hover:border-blue-400 hover:bg-blue-50
                           transition-colors text-sm sm:text-base"
              >
                <div className="font-medium text-blue-900">{gene}</div>
                <div className="text-xs text-blue-600 mt-1">Click to search</div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
