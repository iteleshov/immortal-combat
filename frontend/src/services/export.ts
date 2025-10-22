import { jsPDF } from 'jspdf'
import html2canvas from 'html2canvas'
import { GeneResponse } from '../types'

export const exportToPDF = async (elementId: string, filename: string) => {
  const element = document.getElementById(elementId)
  if (!element) {
    throw new Error('Element not found for PDF export')
  }

  // Capture the element as canvas
  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
  })

  const imgData = canvas.toDataURL('image/png')
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'px',
    format: [canvas.width, canvas.height],
  })

  pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height)
  pdf.save(`${filename}.pdf`)
}

export const formatGeneForExport = (gene: GeneResponse): string => {
  return `Gene: ${gene.gene}
Synonyms: ${gene.synonyms.join(', ')}

Function:
${gene.function || 'N/A'}

Longevity Association:
${gene.longevity_association || 'N/A'}

Modification Effects:
${gene.modification_effects || 'N/A'}

Protein Sequence Length: ${gene.protein_sequence?.length || 0}
DNA Sequence Length: ${gene.dna_sequence?.length || 0}

Evolutionary Conservation:
${gene.contribution_of_evolution || 'N/A'}

Source: ${gene.article || 'N/A'}
`
}


