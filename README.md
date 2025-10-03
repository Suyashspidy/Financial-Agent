# Claims Triage Agent

A modern React web application for intelligent insurance claims triage using AI-powered analysis and routing.

## Features

- **Intelligent File Upload**: Drag and drop PDF upload with validation
- **AI-Powered Analysis**: Automatic claim scoring and complexity assessment
- **Smart Routing**: AI suggests the appropriate team for each claim
- **Real-time Dashboard**: View and manage processed claims
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **Frontend**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Components**: react-bits component library
- **Icons**: Lucide React
- **Build Tool**: Vite

## Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Usage

### Upload Claims
1. Navigate to the "Upload Claim" section (default view)
2. Drag and drop a PDF file or click "Choose File"
3. Click "Submit for Triage" to process the claim
4. The system will automatically switch to the dashboard to show results

### View Results
1. Navigate to the "Triage Dashboard" section
2. View processed claims with:
   - Severity scores (color-coded)
   - Complexity levels
   - Suggested team assignments
   - Risk flags and warnings
   - Reassign options

## Features Overview

### Upload Section
- Clean, modern hero section with clear value proposition
- Large, intuitive file upload area with drag and drop support
- PDF file validation
- Loading states with spinner during processing
- Feature highlights showcasing key benefits

### Triage Dashboard
- Card-based layout for easy claim review
- Color-coded severity indicators (red/yellow/green)
- Comprehensive claim information display
- Flag system for risk identification
- One-click reassignment functionality

### Responsive Design
- Mobile-first approach
- Adaptive layouts for all screen sizes
- Touch-friendly interface elements
- Optimized for both desktop and mobile workflows

## Mock Data

The application uses generated mock data for demonstration purposes. In a production environment, this would be replaced with real API calls to your claims processing backend.

## Customization

The application is built with Tailwind CSS, making it easy to customize:
- Colors: Modify the color palette in the component files
- Layout: Adjust spacing and sizing using Tailwind utilities
- Components: Extend or modify the react-bits components as needed

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
