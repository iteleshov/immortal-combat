import { useState } from 'react'
import { ChevronDown, ChevronRight, ExternalLink, FileText, Loader2 } from 'lucide-react'
import { GeneResponse } from '../types'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import logo from '../assets/gene-lens-logo.png'

interface GeneResultsProps {
  gene: GeneResponse
}

export default function GeneResults({ gene }: GeneResultsProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['basic', 'function']))

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newExpanded = new Set(prev)
      newExpanded.has(section) ? newExpanded.delete(section) : newExpanded.add(section)
      return newExpanded
    })
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
        className="w-full flex items-center justify-between p-3 sm:p-4 bg-gray-50 hover:bg-gray-100
                   border-b border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        <h3 className="text-base sm:text-lg font-semibold text-gray-700">{title}</h3>
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

  const SequenceDisplay = ({
                             sequence,
                             title
                           }: {
    sequence?: string
    title: string
  }) => {
    if (!sequence) return null

    return (
      <div className="mt-4">
        <div className="flex items-center justify-between mb-2 flex-wrap gap-1">
          <h4 className="text-sm font-medium text-gray-700">{title}</h4>
          <span className="text-xs text-gray-500">{sequence.length} characters</span>
        </div>
        <div className="rounded-md overflow-hidden border bg-gray-50">
          <pre className="p-3 sm:p-4 text-[11px] sm:text-xs font-mono text-gray-800 overflow-auto
                          max-h-[250px] sm:max-h-[300px] whitespace-pre-wrap break-all">
            {sequence}
          </pre>
        </div>
      </div>
    )
  }

  // ——— Processing state (Loader)
  if (gene.status === 'processing') {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
        <div className="flex flex-col items-center space-y-3">
          <Loader2 className="h-8 w-8 text-primary-600 animate-spin" />
          <h2 className="text-lg sm:text-xl font-semibold text-gray-900">
            Processing your request
          </h2>
          <p className="text-gray-600 text-sm sm:text-base">
            Your query for <strong>{gene.gene}</strong> is being processed.
          </p>
          <p className="text-gray-600 text-sm sm:text-base">
            Average processing time: <strong>up to 1 hour</strong>.
          </p>

          {gene.queue_size && gene.queue_size > 1 && (
            <p className="text-xs sm:text-sm text-gray-500 mt-2">
              There are currently <strong>{gene.queue_size - 1}</strong> other
              gene(s) in the queue ahead of yours.
            </p>
          )}
        </div>
      </div>
    )
  }

  return (
    <div
      id="gene-results"
      className="bg-white rounded-lg shadow-sm border overflow-hidden w-full"
    >
      {/* Header */}
      <div className="p-4 sm:p-6 border-b border-gray-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3 sm:space-x-4">
          <img src={logo} alt="GeneLens logo" className="w-8 h-8 sm:w-10 sm:h-10 object-contain rounded" />
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900">{gene.gene}</h2>
            {gene.synonyms?.length > 0 && (
              <p className="text-xs sm:text-sm text-gray-600 mt-1">
                Also known as: {gene.synonyms.join(', ')}
              </p>
            )}
          </div>
        </div>

        <button
          onClick={() => {
            const blob = new Blob([gene.article ?? ''], { type: 'text/plain;charset=utf-8' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = `${gene.gene}.md`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)
          }}
          className="inline-flex items-center justify-center w-full sm:w-auto px-3 py-2 border border-gray-300
                     shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700
                     bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2
                     focus:ring-primary-500 cursor-pointer"
          disabled={gene.status !== 'ready'}
          hidden={gene.status !== 'ready'}
        >
          <FileText className="h-4 w-4 mr-2" />
          Download
        </button>
      </div>

      {/* Article content */}
      <div className="p-4 sm:p-6">
        <div className="prose prose-gray max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
            className="text-sm sm:text-base leading-relaxed text-gray-900"
          >
            {gene.article}
          </ReactMarkdown>
        </div>
      </div>

      {/* Additional Data */}
      {gene.status === 'ready' && (
        <>
          <div className="px-4 sm:px-6 py-3 border-t border-b border-gray-300 bg-transparent">
            <h3 className="text-sm sm:text-md font-semibold text-gray-900 uppercase tracking-wide">
              Additional Data
            </h3>
          </div>

          {/* Basic Info */}
          <div>
            <SectionHeader title="Basic Information" section="basic" />
            {expandedSections.has('basic') && (
              <div className="p-4 sm:p-6 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Gene Symbol</label>
                    <p className="mt-1 text-sm text-gray-900 break-words">{gene.gene}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Synonyms</label>
                    <p className="mt-1 text-sm text-gray-900 break-words">{gene.synonyms?.join(', ') || 'None'}</p>
                  </div>
                </div>
                {gene.interval_in_dna_sequence && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">DNA Sequence Interval</label>
                    <p className="mt-1 text-sm text-gray-900">
                      Positions {gene.interval_in_dna_sequence[0]} - {gene.interval_in_dna_sequence[1]}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Function */}
          <div>
            <SectionHeader title="Function" section="function" />
            {expandedSections.has('function') && (
              <div className="p-4 sm:p-6">
                <p className="text-sm sm:text-base text-gray-900 leading-relaxed">
                  {gene.function || 'No function information available.'}
                </p>
              </div>
            )}
          </div>

          {/* Other sections (same pattern)... */}
          <div>
            <SectionHeader title="Sequences" section="sequences" />
            {expandedSections.has('sequences') && (
              <div className="p-4 sm:p-6 space-y-6">
                <SequenceDisplay sequence={gene.protein_sequence} title="Protein Sequence" />
                <SequenceDisplay sequence={gene.dna_sequence} title="DNA Sequence" />
              </div>
            )}
          </div>

          {gene.externalLink && gene.externalLink.trim() !== '' && (
            <div>
              <SectionHeader title="Source" section="source" />
              {expandedSections.has('source') && (
                <div className="p-4 sm:p-6">
                  <a
                    href={gene.externalLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-sm sm:text-base text-primary-600 hover:text-primary-800 break-all"
                  >
                    View source article
                    <ExternalLink className="ml-1 h-4 w-4" />
                  </a>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
