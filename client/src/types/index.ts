export interface GeneResponse {
  gene: string;
  function?: string;
  synonyms: string[];
  longevity_association?: string;
  modification_effects?: string;
  dna_sequence?: string;
  interval_in_dna_sequence?: [number, number];
  protein_sequence?: string;
  interval_in_protein_sequence?: [number, number];
  interval_in_sequence?: [number, number];
  contribution_of_evolution?: string;
  article?: string;
}

export interface ComparisonResponse {
  comparison_id: string;
  genes_compared: string[];
  comparison_article: string;
  common_pathways: {
    pathway_name: string;
    genes_involved: string[];
    description: string;
  }[];
  key_differences: {
    category: string;
    differences: string[];
  }[];
  evolutionary_relationships: {
    conservation_levels: Record<string, string>;
  };
  modification_patterns: {
    common_modifications: string[];
    gene_specific_modifications: Record<string, string[]>;
  };
}

export interface SearchState {
  currentGene: GeneResponse | null;
  loading: boolean;
  error: string | null;
  searchHistory: string[];
}

export interface ComparisonState {
  selectedGenes: string[];
  comparisonResult: ComparisonResponse | null;
  loading: boolean;
  error: string | null;
}

export interface UIState {
  sidebarOpen: boolean;
  activeTab: 'search' | 'comparison';
  theme: 'light';
}

