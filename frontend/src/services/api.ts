import { GeneResponse } from '../types'

const API_BASE_URL = 'https://gene-lens.site'

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

export const searchGene = async (geneName: string): Promise<GeneResponse> => {
  await delay(800) // Simulate network delay

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


