import { ComparisonResponse } from '../types'

export const mockComparison: ComparisonResponse = {
  comparison_id: 'comp_2024_001',
  genes_compared: ['NRF2', 'APOE', 'SOX2', 'OCT4'],
  comparison_article: `# Comprehensive Comparison of NRF2, APOE, SOX2, and OCT4

## Overview
This analysis compares four genes with distinct but interconnected roles in longevity and cellular function: NRF2 (antioxidant defense), APOE (lipid metabolism), SOX2 (pluripotency), and OCT4 (stem cell maintenance).

## Common Longevity Mechanisms
All four genes contribute to longevity through distinct yet complementary pathways. NRF2 provides cellular protection through oxidative stress response, while APOE modulates systemic metabolism and neuroprotection. SOX2 and OCT4 maintain regenerative capacity through stem cell regulation and cellular reprogramming.

## Key Functional Differences
- **NRF2**: Operates primarily in stress response and cytoprotection
- **APOE**: Functions in lipid transport and cholesterol homeostasis  
- **SOX2**: Master regulator of pluripotency and neural development
- **OCT4**: Core transcription factor for embryonic stem cell identity

## Evolutionary Conservation
NRF2 and SOX2 show high conservation across vertebrates, while APOE is mammal-specific and OCT4 is vertebrate-specific. The differential conservation patterns reflect their distinct evolutionary origins and functional constraints.

## Therapeutic Implications
Understanding these genes collectively provides insights into comprehensive anti-aging strategies targeting multiple longevity pathways: oxidative stress (NRF2), metabolic health (APOE), and regenerative capacity (SOX2/OCT4).`,
  
  common_pathways: [
    {
      pathway_name: 'Oxidative Stress Response',
      genes_involved: ['NRF2', 'APOE'],
      description: 'Both NRF2 and APOE play crucial roles in cellular antioxidant defense. NRF2 directly regulates antioxidant gene expression, while APOE modulates oxidative stress through lipid metabolism and membrane protection.'
    },
    {
      pathway_name: 'Cellular Reprogramming',
      genes_involved: ['SOX2', 'OCT4'],
      description: 'SOX2 and OCT4 are core transcription factors in the Yamanaka factor set, working synergistically to maintain pluripotency and enable cellular reprogramming for regenerative medicine applications.'
    },
    {
      pathway_name: 'Neuroprotection',
      genes_involved: ['APOE', 'NRF2', 'SOX2'],
      description: 'All three genes contribute to neural health: APOE through lipid transport, NRF2 via oxidative stress protection, and SOX2 through neural stem cell maintenance.'
    }
  ],
  
  key_differences: [
    {
      category: 'Longevity Mechanism',
      differences: [
        'NRF2: Primarily antioxidant defense and stress response, directly activates protective gene programs',
        'APOE: Lipid metabolism and neural protection, with variant-specific longevity effects (APOE2 protective, APOE4 detrimental)',
        'SOX2: Cellular reprogramming and stem cell maintenance, enables tissue regeneration',
        'OCT4: Pluripotency and developmental regulation, critical for iPSC generation'
      ]
    },
    {
      category: 'Tissue Specificity',
      differences: [
        'NRF2: Ubiquitously expressed with highest activity in liver, kidney, and digestive tract',
        'APOE: Predominantly expressed in liver, brain, and macrophages',
        'SOX2: Restricted to neural tissues and embryonic stem cells',
        'OCT4: Highly restricted to embryonic stem cells and germline'
      ]
    },
    {
      category: 'Regulation Mechanism',
      differences: [
        'NRF2: Regulated by KEAP1-mediated ubiquitination and degradation',
        'APOE: Transcriptionally regulated with genetic variants affecting protein function',
        'SOX2: Regulated through phosphorylation and protein-protein interactions',
        'OCT4: Strictly controlled through developmental signaling pathways'
      ]
    }
  ],
  
  evolutionary_relationships: {
    conservation_levels: {
      NRF2: 'Highly conserved across vertebrates (>95% in mammals). Orthologs: SKN-1 (C. elegans), CncC (Drosophila)',
      APOE: 'Mammalian-specific with human variants. Emerged ~300 million years ago',
      SOX2: 'Highly conserved in vertebrates (>90% in mammals). Critical HMG-box domain universally conserved',
      OCT4: 'Vertebrate-specific transcription factor. POU domain shows high conservation within vertebrates'
    }
  },
  
  modification_patterns: {
    common_modifications: ['Phosphorylation', 'Ubiquitination', 'Acetylation'],
    gene_specific_modifications: {
      NRF2: [
        'Phosphorylation at Ser40 (KEAP1 dissociation)',
        'Ubiquitination by KEAP1-Cul3 (degradation)',
        'Acetylation (enhanced DNA binding)'
      ],
      APOE: [
        'Genetic variants (Cys/Arg at positions 112, 158)',
        'Phosphorylation (protein stability)',
        'Glycosylation (receptor binding)'
      ],
      SOX2: [
        'Phosphorylation (multiple sites, stability regulation)',
        'SUMOylation (DNA binding modulation)',
        'Acetylation (protein-protein interactions)',
        'SuperSOX modifications (enhanced reprogramming)'
      ],
      OCT4: [
        'Phosphorylation (transcriptional activity)',
        'Ubiquitination (degradation control)',
        'SUMOylation (subcellular localization)',
        'OCT6-to-OCT4 conversion mutations'
      ]
    }
  }
}


