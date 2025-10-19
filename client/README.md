# Longevity Gene Knowledge Base - Frontend

A React frontend for the Longevity Gene & Protein Sequence-to-Function Knowledge Base. This application allows users to search for genes, view comprehensive information about their sequence-to-function relationships, and compare multiple genes using AI-powered analysis.

## Features

- **Gene Search**: Search for genes and view detailed information including:
  - Protein/DNA sequences with syntax highlighting
  - Longevity associations
  - Modification effects
  - Evolutionary conservation data
  - Foldable sections for better organization

- **Gene Comparison**: Compare up to 4 genes with AI-powered analysis:
  - Common pathways identification
  - Key differences analysis
  - Evolutionary relationships
  - Modification patterns

- **Export Functionality**: Export results as PDF or JSON

- **Mobile-First Design**: Responsive design optimized for mobile devices

## Technology Stack

- **React 18** with TypeScript
- **Redux Toolkit** for state management
- **Tailwind CSS** for styling
- **Vite** for build tooling
- **React Syntax Highlighter** for sequence display
- **jsPDF** and **html2canvas** for PDF export

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Running with Backend

To run both frontend and backend together:

```bash
npm run dev:full
```

This will start:
- Frontend at `http://localhost:3000`
- Backend at `http://localhost:8000`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run dev:full` - Run frontend and backend together
- `npm run lint` - Run ESLint

## Mock Data

The application includes comprehensive mock data for testing with these genes:
- **NRF2**: Antioxidant response and stress defense
- **APOE**: Lipid metabolism and neural protection  
- **SOX2**: Pluripotency and cellular reprogramming
- **OCT4**: Stem cell maintenance and development

## Environment Variables

Create a `.env` file in the client directory:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=true
```

- `VITE_API_BASE_URL`: Backend API URL
- `VITE_USE_MOCK_DATA`: Use mock data instead of real API calls

## Project Structure

```
client/
├── src/
│   ├── components/          # React components
│   ├── pages/              # Page components
│   ├── store/              # Redux store and slices
│   ├── services/           # API and utility services
│   ├── data/               # Mock data
│   ├── types/              # TypeScript type definitions
│   └── hooks/              # Custom React hooks
├── public/                 # Static assets
└── package.json
```

## API Integration

The frontend integrates with the FastAPI backend through these endpoints:

- `GET /search?gene_name={name}` - Search for a gene
- `POST /compare` - Compare multiple genes

When `VITE_USE_MOCK_DATA=true`, the frontend uses mock data instead of making real API calls.

## Contributing

1. Follow the existing code style
2. Use TypeScript for all new code
3. Add proper error handling
4. Test on mobile devices
5. Update documentation as needed

## License

This project is part of the Immortal Combat longevity research initiative.

## Notes

- The PostCSS plugin for Tailwind has moved to a separate package. If you run into an error mentioning using `tailwindcss` directly as a PostCSS plugin, make sure `@tailwindcss/postcss` is installed and the `postcss.config.js` uses it. The project already includes `@tailwindcss/postcss` in `package.json` and the config file has been updated.

