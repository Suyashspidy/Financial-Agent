# Financial Agent - Claims Triage System

A modern React-based claims triage application with AI-powered document processing, featuring a beautiful animated UI with multiple file upload capabilities.

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Node.js** (version 16.0 or higher)
- **npm** (comes with Node.js) or **yarn**
- **Git** (for cloning the repository)

### Installation Steps

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd Financial-Agent
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```
   
   This will install all required packages including:
   - React 18
   - Vite (build tool)
   - Tailwind CSS (styling)
   - Lucide React (icons)
   - GSAP (animations)
   - OGL (WebGL for 3D animations)

3. **Start the development server**:
   ```bash
   npm run dev
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5173
   ```
   
   *Note: If port 5173 is in use, Vite will automatically use the next available port (e.g., 5174)*

## 🎯 Features

### Core Functionality
- **Multiple File Upload**: Upload multiple PDF documents simultaneously
- **Drag & Drop Support**: Intuitive file selection with drag and drop
- **AI-Powered Processing**: Simulated AI analysis of uploaded documents
- **Claims Dashboard**: View and manage processed claims
- **Smart Routing**: Automatic team assignment based on claim analysis

### UI/UX Features
- **Animated Background**: 3D Prism WebGL animation
- **Typing Animation**: Dynamic text effects using GSAP
- **Spotlight Cards**: Interactive hover effects on feature cards
- **Pill Navigation**: Modern, animated navigation bar
- **Transparent Design**: Glass-morphism UI with backdrop blur effects
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Development

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build the application for production
- `npm run preview` - Preview the production build locally
- `npm run lint` - Run ESLint for code quality checks

### Project Structure

```
src/
├── App.jsx                 # Main application component
├── TextType.jsx           # Typing animation component
├── Prism.jsx              # 3D WebGL background animation
├── PillNav.jsx            # Navigation component
├── SpotlightCard.jsx      # Interactive card component
├── index.css              # Global styles and Tailwind CSS
└── main.jsx               # Application entry point
```

### Key Components

#### UploadSection
- Handles multiple file uploads
- Drag and drop functionality
- File management (add/remove files)
- Progress indicators

#### TriageDashboard
- Displays processed claims
- Shows claim details and analysis
- Team assignment information
- Reassignment functionality

#### PillNav
- Centered navigation bar
- Smooth animations with GSAP
- Mobile-responsive design
- Active state management

## 🎨 Styling

The application uses **Tailwind CSS** for styling with custom components:

- **Color Scheme**: Dark theme with transparent elements
- **Typography**: Modern font stack with proper hierarchy
- **Animations**: GSAP-powered smooth transitions
- **Layout**: Responsive grid system
- **Effects**: Backdrop blur, gradients, and shadows

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory for any environment-specific configurations:

```env
VITE_API_URL=your_api_url_here
VITE_APP_TITLE=Financial Agent
```

### Build Configuration
The project uses Vite for building. Configuration can be found in `vite.config.js`.

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

*Note: WebGL features require modern browser support*

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   # Kill process using port 5173
   lsof -ti:5173 | xargs kill -9
   ```

2. **Node modules issues**:
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Build errors**:
   ```bash
   # Check for syntax errors
   npm run lint
   ```

4. **WebGL not working**:
   - Ensure your browser supports WebGL
   - Check browser console for WebGL errors
   - Try disabling hardware acceleration

### Development Tips

- Use React DevTools for debugging
- Check browser console for any errors
- Hot reload should work automatically
- File changes trigger automatic rebuilds

## 📦 Dependencies

### Core Dependencies
- `react` - UI library
- `react-dom` - DOM rendering
- `vite` - Build tool and dev server

### UI & Styling
- `tailwindcss` - CSS framework
- `lucide-react` - Icon library
- `gsap` - Animation library

### 3D Graphics
- `ogl` - WebGL library for 3D animations

### Development
- `@vitejs/plugin-react` - Vite React plugin
- `eslint` - Code linting
- `autoprefixer` - CSS vendor prefixes

## 🚀 Deployment

### Production Build

1. **Build the application**:
   ```bash
   npm run build
   ```

2. **Preview the build**:
   ```bash
   npm run preview
   ```

3. **Deploy the `dist` folder** to your hosting service

### Deployment Options

- **Vercel**: Connect your GitHub repository
- **Netlify**: Drag and drop the `dist` folder
- **AWS S3**: Upload the `dist` folder contents
- **GitHub Pages**: Use GitHub Actions for automatic deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Search existing GitHub issues
3. Create a new issue with detailed information
4. Include browser console logs and error messages

---

**Happy coding! 🎉**
