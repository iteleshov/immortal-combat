import { useState } from 'react'
import { ChevronDown, ChevronRight, Download, FileText } from 'lucide-react'
import { ComparisonResponse } from '../types'
import { exportToJSON, exportToPDF } from '../services/export'

interface ComparisonResultsProps {
  comparison: ComparisonResponse
}

export default function ComparisonResults({ comparison }: ComparisonResultsProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview', 'common-pathways']))

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const handleExportJSON = () => {
    exportToJSON(comparison, `comparison_${comparison.genes_compared.join('_')}`)
  }

  const handleExportPDF = () => {
    exportToPDF('comparison-results', `comparison_${comparison.genes_compared.join('_')}`)
  }

  const SectionHeader = ({ 
    title, 
    section, 
    children 
  }: { 
    title: string
    section: string
    children?: React.ReactNode 
  }) => {
    const isExpanded = expandedSections.has(section)
    
    return (
      <button
        onClick={() => toggleSection(section)}
        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 border-b border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center space-x-2">
          {children}
          {isExpanded ? (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-500" />
          )}
        </div>
      </button>
    )
  }

  return (
    <div id="comparison-results" className="bg-white rounded-lg shadow-sm border">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Gene Comparison Analysis</h2>
            <p className="text-sm text-gray-600 mt-1">
              Comparing: {comparison.genes_compared.join(', ')}
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleExportJSON}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <FileText className="h-4 w-4 mr-2" />
              JSON
            </button>
            <button
              onClick={handleExportPDF}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <Download className="h-4 w-4 mr-2" />
              PDF
            </button>
          </div>
        </div>
      </div>

      {/* Overview */}
      <div>
        <SectionHeader title="Analysis Overview" section="overview" />
        {expandedSections.has('overview') && (
          <div className="p-6">
            <div className="prose prose-sm max-w-none">
              <div 
                className="whitespace-pre-wrap text-gray-900 leading-relaxed"
                dangerouslySetInnerHTML={{ 
                  __html: comparison.comparison_article.replace(/\n/g, '<br>') 
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Common Pathways */}
      <div>
        <SectionHeader title="Common Pathways" section="common-pathways" />
        {expandedSections.has('common-pathways') && (
          <div className="p-6 space-y-4">
            {comparison.common_pathways.map((pathway, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <h4 className="text-lg font-semibold text-gray-900 mb-2">{pathway.pathway_name}</h4>
                <div className="mb-3">
                  <span className="inline-block bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                    Genes: {pathway.genes_involved.join(', ')}
                  </span>
                </div>
                <p className="text-sm text-gray-700 leading-relaxed">{pathway.description}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Key Differences */}
      <div>
        <SectionHeader title="Key Differences" section="key-differences" />
        {expandedSections.has('key-differences') && (
          <div className="p-6 space-y-6">
            {comparison.key_differences.map((category, index) => (
              <div key={index}>
                <h4 className="text-lg font-semibold text-gray-900 mb-3">{category.category}</h4>
                <ul className="space-y-2">
                  {category.differences.map((difference, diffIndex) => (
                    <li key={diffIndex} className="flex items-start">
                      <span className="flex-shrink-0 w-2 h-2 bg-gray-400 rounded-full mt-2 mr-3"></span>
                      <span className="text-sm text-gray-700">{difference}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Evolutionary Relationships */}
      <div>
        <SectionHeader title="Evolutionary Relationships" section="evolutionary" />
        {expandedSections.has('evolutionary') && (
          <div className="p-6">
            <h4 className="text-lg font-semibold text-gray-900 mb-4">Conservation Levels</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(comparison.evolutionary_relationships.conservation_levels).map(([gene, conservation]) => (
                <div key={gene} className="border border-gray-200 rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-2">{gene}</h5>
                  <p className="text-sm text-gray-700">{conservation}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modification Patterns */}
      <div>
        <SectionHeader title="Modification Patterns" section="modifications" />
        {expandedSections.has('modifications') && (
          <div className="p-6 space-y-6">
            {/* Common Modifications */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Common Modifications</h4>
              <div className="flex flex-wrap gap-2">
                {comparison.modification_patterns.common_modifications.map((modification, index) => (
                  <span key={index} className="inline-block bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">
                    {modification}
                  </span>
                ))}
              </div>
            </div>

            {/* Gene-Specific Modifications */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 mb-3">Gene-Specific Modifications</h4>
              <div className="space-y-4">
                {Object.entries(comparison.modification_patterns.gene_specific_modifications).map(([gene, modifications]) => (
                  <div key={gene} className="border border-gray-200 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2">{gene}</h5>
                    <ul className="space-y-1">
                      {modifications.map((modification, index) => (
                        <li key={index} className="text-sm text-gray-700 flex items-start">
                          <span className="flex-shrink-0 w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 mr-2"></span>
                          {modification}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

