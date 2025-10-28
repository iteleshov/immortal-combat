import { useState } from 'react'
import { ChevronDown, ChevronRight, ExternalLink, FileText } from 'lucide-react'
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
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
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
        <h3 className="text-lg font-semibold text-gray-700">{title}</h3>
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
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-medium text-gray-700">{title}</h4>
          <span className="text-xs text-gray-500">{sequence.length} characters</span>
        </div>
        <div className="rounded-md overflow-hidden border bg-gray-50">
          <pre className="p-4 text-xs font-mono text-gray-800 overflow-auto max-h-[300px] whitespace-pre-wrap break-all">
            {sequence}
          </pre>
        </div>
      </div>
    )
  }

  if (gene.status === 'processing') {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Processing your request
        </h2>
        <p className="text-gray-600">
          Your query for <strong>{gene.gene}</strong> is being processed.
          This may take up to one hour. Please check back later.
        </p>
      </div>
    )
  } else if (gene.status === 'ready') {
    return (
      <div id="gene-results" className="bg-white rounded-lg shadow-sm border">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <img src={logo} alt="GeneLens logo" className="w-10 h-10 object-contain rounded" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{gene.gene}</h2>
              {gene.synonyms?.length > 0 && (
                <p>Also known as: {gene.synonyms.join(', ')}</p>
              )}
            </div>
          </div>

          <button
            onClick={() => {
              const blob = new Blob([gene.article!!], { type: 'text/plain;charset=utf-8' })
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `${gene.gene}.md`
              document.body.appendChild(a)
              a.click()
              document.body.removeChild(a)
              URL.revokeObjectURL(url)
            }}
            className="inline-flex items-center px-3 py-2 border border-gray-300
                     shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700
                     bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2
                     focus:ring-primary-500 cursor-pointer"
          >
            <FileText className="h-4 w-4 mr-2" />
            Download
          </button>
        </div>

        {/* Analysis result */}
        <div>
          <div className="prose prose-gray max-w-none p-6">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeRaw]}
              className="text-sm leading-relaxed text-gray-900"
            >
              {gene.article}
            </ReactMarkdown>
          </div>
        </div>

        {/* Divider: Additional Data */}
        <div className="px-6 py-3 border-t border-b border-gray-300 bg-transparent">
          <h3 className="text-md font-semibold text-gray-900 uppercase tracking-wide">
            Additional Data
          </h3>
        </div>

        {/* Basic Information */}
        <div>
          <SectionHeader title="Basic Information" section="basic" />
          {expandedSections.has('basic') && (
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Gene Symbol</label>
                  <p className="mt-1 text-sm text-gray-900">{gene.gene}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Synonyms</label>
                  <p className="mt-1 text-sm text-gray-900">{gene.synonyms.join(', ') || 'None'}</p>
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
            <div className="p-6">
              <p className="text-sm text-gray-900 leading-relaxed">
                {gene.function || 'No function information available.'}
              </p>
            </div>
          )}
        </div>

        {/* Longevity Association */}
        <div>
          <SectionHeader title="Longevity Association" section="longevity" />
          {expandedSections.has('longevity') && (
            <div className="p-6">
              <p className="text-sm text-gray-900 leading-relaxed">
                {gene.longevity_association || 'No longevity association information available.'}
              </p>
            </div>
          )}
        </div>

        {/* Modification Effects */}
        <div>
          <SectionHeader title="Modification Effects" section="modifications" />
          {expandedSections.has('modifications') && (
            <div className="p-6">
              <p className="text-sm text-gray-900 leading-relaxed">
                {gene.modification_effects || 'No modification effects information available.'}
              </p>
            </div>
          )}
        </div>

        {/* Evolutionary Conservation */}
        <div>
          <SectionHeader title="Evolutionary Conservation" section="evolution" />
          {expandedSections.has('evolution') && (
            <div className="p-6">
              <p className="text-sm text-gray-900 leading-relaxed">
                {gene.contribution_of_evolution || 'No evolutionary conservation information available.'}
              </p>
            </div>
          )}
        </div>

        {/* Sequences */}
        <div>
          <SectionHeader title="Sequences" section="sequences" />
          {expandedSections.has('sequences') && (
            <div className="p-6 space-y-6">
              <SequenceDisplay sequence={gene.protein_sequence} title="Protein Sequence" />
              <SequenceDisplay sequence={gene.dna_sequence} title="DNA Sequence" />
            </div>
          )}
        </div>

        {/* Source */}
        {gene.externalLink && gene.externalLink.trim() !== '' && (
          <div>
            <SectionHeader title="Source" section="source" />
            {expandedSections.has('source') && (
              <div className="p-6">
                <a
                  href={gene.externalLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-sm text-primary-600 hover:text-primary-800"
                >
                  View source article
                  <ExternalLink className="ml-1 h-4 w-4" />
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }
}
