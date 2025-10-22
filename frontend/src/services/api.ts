import { GeneResponse } from '../types'
import { mockGenes } from '../data/mockGenes'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true'

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const searchGene = async (geneName: string): Promise<GeneResponse> => {
  await delay(800) // Simulate network delay

  if (USE_MOCK_DATA) {
    const gene = mockGenes[geneName.toUpperCase()]
    if (!gene) {
      throw new Error(`Gene "${geneName}" not found. Try NRF2, APOE, SOX2, or OCT4`)
    }
    return gene
  }

  // Real API call
  const response = await fetch(`${API_BASE_URL}/api/search?gene_name=${encodeURIComponent(geneName)}`)
  if (!response.ok) {
    throw new Error('Failed to fetch gene data')
  }
  return response.json()
}

// Validate gene name format
export const validateGeneName = (name: string): boolean => {
  // Allow alphanumeric and common gene name characters
  const geneNameRegex = /^[A-Z0-9-]+$/i
  return geneNameRegex.test(name) && name.length >= 2 && name.length <= 20
}


