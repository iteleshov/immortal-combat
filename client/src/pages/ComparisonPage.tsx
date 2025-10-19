import { useState } from 'react'
import { Plus, X, Loader2, AlertCircle, BarChart3 } from 'lucide-react'
import { useAppSelector, useAppDispatch } from '../hooks'
import { addGene, removeGene, fetchComparison, clearSelectedGenes } from '../store/comparisonSlice'
import { validateGeneName } from '../services/api'
import ComparisonResults from '../components/ComparisonResults'

const AVAILABLE_GENES = ['NRF2', 'APOE', 'SOX2', 'OCT4']

export default function ComparisonPage() {
  const dispatch = useAppDispatch()
  const { selectedGenes, comparisonResult, loading, error } = useAppSelector(state => state.comparison)
  const [newGene, setNewGene] = useState('')
  const [validationError, setValidationError] = useState('')

  const handleAddGene = () => {
    if (!newGene.trim()) {
      setValidationError('Please enter a gene name')
      return
    }

    if (!validateGeneName(newGene)) {
      setValidationError('Invalid gene name format. Use letters, numbers, and hyphens only.')
      return
    }

    if (selectedGenes.includes(newGene.toUpperCase())) {
      setValidationError('Gene already selected')
      return
    }

    if (selectedGenes.length >= 4) {
      setValidationError('Maximum 4 genes can be compared')
      return
    }

    setValidationError('')
    dispatch(addGene(newGene.trim().toUpperCase()))
    setNewGene('')
  }

  const handleCompare = () => {
    if (selectedGenes.length < 2) {
      setValidationError('Select at least 2 genes to compare')
      return
    }
    
    setValidationError('')
    dispatch(fetchComparison(selectedGenes))
  }

  const handleRemoveGene = (gene: string) => {
    dispatch(removeGene(gene))
  }

  const handleClearAll = () => {
    dispatch(clearSelectedGenes())
    setValidationError('')
  }

  const handleQuickAdd = (gene: string) => {
    if (!selectedGenes.includes(gene) && selectedGenes.length < 4) {
      dispatch(addGene(gene))
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Gene Comparison</h1>
        <p className="text-gray-600">
          Compare up to 4 genes to analyze their relationships, common pathways, and differences in longevity mechanisms.
        </p>
      </div>

      {/* Gene Selection */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Genes to Compare</h2>
        
        {/* Add Gene Form */}
        <div className="mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              value={newGene}
              onChange={(e) => {
                setNewGene(e.target.value)
                setValidationError('')
              }}
              placeholder="Enter gene name"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              disabled={loading || selectedGenes.length >= 4}
            />
            <button
              onClick={handleAddGene}
              disabled={loading || selectedGenes.length >= 4}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Plus className="h-4 w-4 mr-1" />
              Add
            </button>
          </div>
          {validationError && (
            <p className="mt-2 text-sm text-red-600">{validationError}</p>
          )}
        </div>

        {/* Quick Add Buttons */}
        <div className="mb-6">
          <p className="text-sm font-medium text-gray-700 mb-2">Quick Add:</p>
          <div className="flex flex-wrap gap-2">
            {AVAILABLE_GENES.map((gene) => (
              <button
                key={gene}
                onClick={() => handleQuickAdd(gene)}
                disabled={selectedGenes.includes(gene) || selectedGenes.length >= 4}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {gene}
              </button>
            ))}
          </div>
        </div>

        {/* Selected Genes */}
        {selectedGenes.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm font-medium text-gray-700">
                Selected Genes ({selectedGenes.length}/4)
              </p>
              <button
                onClick={handleClearAll}
                className="text-sm text-red-600 hover:text-red-800"
              >
                Clear All
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {selectedGenes.map((gene) => (
                <div
                  key={gene}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800"
                >
                  {gene}
                  <button
                    onClick={() => handleRemoveGene(gene)}
                    className="ml-2 text-primary-600 hover:text-primary-800"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Compare Button */}
        <button
          onClick={handleCompare}
          disabled={loading || selectedGenes.length < 2}
          className="w-full flex justify-center items-center px-4 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="animate-spin -ml-1 mr-3 h-5 w-5" />
              Analyzing...
            </>
          ) : (
            <>
              <BarChart3 className="h-5 w-5 mr-2" />
              Compare Genes
            </>
          )}
        </button>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Comparison Error</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      {comparisonResult && <ComparisonResults comparison={comparisonResult} />}

      {/* Instructions */}
      {selectedGenes.length === 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-3">How to Compare Genes</h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
            <li>Add 2-4 genes using the input field above or quick-add buttons</li>
            <li>Click "Compare Genes" to analyze their relationships</li>
            <li>View AI-generated insights about common pathways and differences</li>
            <li>Export results as PDF or JSON for further analysis</li>
          </ol>
        </div>
      )}
    </div>
  )
}

