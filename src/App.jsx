import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, Clock, Users, Shield, Scale } from 'lucide-react';
import TextType from './TextType';
import Prism from './Prism';
import PillNav from './PillNav';
import SpotlightCard from './SpotlightCard';

// Lightweight local UI primitives
const UIButton = ({ children, className = '', variant = 'secondary', ...props }) => {
  const base = 'inline-flex items-center justify-center rounded-md px-4 py-2 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-slate-200 text-slate-800 hover:bg-slate-300 focus:ring-slate-400',
    outline: 'border border-slate-300 text-slate-800 hover:bg-slate-50',
    dark: 'bg-slate-800 text-white hover:bg-slate-700 focus:ring-slate-500',
    darkOutline: 'border border-slate-600 text-white hover:bg-slate-800',
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>{children}</button>
  );
};

const UICard = ({ children, className = '', ...props }) => (
  <div className={`rounded-xl border border-slate-200 bg-white ${className}`} {...props}>{children}</div>
);

const UISpinner = ({ className = '' }) => (
  <svg className={`animate-spin h-5 w-5 ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
  </svg>
);

// Mock data for demonstration
const generateMockClaim = (claimId) => ({
  id: claimId,
  severity: Math.floor(Math.random() * 10) + 1,
  complexity: ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)],
  suggestedTeam: ['General Claims', 'Major Incidents Unit', 'Fraud Investigation', 'Legal Review'][Math.floor(Math.random() * 4)],
  flags: ['Litigation Risk', 'Fraudulent Activity Suspected', 'High Value', 'Urgent Review'].slice(0, Math.floor(Math.random() * 3) + 1),
  uploadDate: new Date().toLocaleDateString(),
  status: 'Pending Review'
});


// Upload Section Component
const UploadSection = ({ onFileUpload, isLoading }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (files) => {
    const fileArray = Array.from(files);
    const pdfFiles = fileArray.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length > 0) {
      setSelectedFiles(prev => [...prev, ...pdfFiles]);
    } else {
      alert('Please select PDF files');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    handleFileSelect(files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleSubmit = async () => {
    if (selectedFiles.length > 0) {
      await onFileUpload(selectedFiles);
    }
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const clearAllFiles = () => {
    setSelectedFiles([]);
  };

  return (
    <div className="pt-20 min-h-screen bg-black relative">
      {/* Background Animation */}
      <div style={{ width: '100%', height: '100%', position: 'absolute', top: 0, left: 0, zIndex: 0 }}>
        <Prism
          animationType="rotate"
          timeScale={0.5}
          height={3.5}
          baseWidth={5.5}
          scale={3.6}
          hueShift={0}
          colorFrequency={1}
          noise={0.5}
          glow={1}
        />
      </div>
      
      {/* Content */}
      <div className="relative z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section with Welcome Text */}
        <div className="text-center mb-12">
          <div className="mb-8">
            <TextType 
              text={["Welcome to Claims Triage"]}
              typingSpeed={75}
              pauseDuration={1500}
              showCursor={true}
              cursorCharacter="|"
              className="text-4xl md:text-6xl font-bold text-white"
            />
          </div>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed">
            Upload a claims document to automatically analyze, score, and route it to the correct team.
            Our AI-powered system processes your claims in seconds.
          </p>
        </div>

        {/* Upload Area */}
        <div className="bg-black/10 backdrop-blur-sm rounded-2xl shadow-xl p-8 mb-8 border border-white/10" style={{
          background: 'linear-gradient(135deg, rgba(0,0,0,0.1) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.5) 100%)'
        }}>
          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
              isDragOver 
                ? 'border-blue-400 bg-blue-500/10' 
                : selectedFiles.length > 0
                  ? 'border-green-400 bg-green-500/10' 
                  : 'border-white/30 hover:border-white/50'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <Upload className="h-16 w-16 mx-auto mb-4 text-slate-400" />
            {selectedFiles.length > 0 ? (
              <div>
                <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <p className="text-lg font-medium text-white mb-2">
                  {selectedFiles.length} File{selectedFiles.length > 1 ? 's' : ''} Selected
                </p>
                <div className="max-h-32 overflow-y-auto mb-4">
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-black/20 rounded-lg p-2 mb-2">
                      <span className="text-slate-300 text-sm truncate flex-1">{file.name}</span>
                      <button
                        onClick={() => removeFile(index)}
                        className="ml-2 text-red-400 hover:text-red-300 text-sm"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
                <button
                  onClick={clearAllFiles}
                  className="text-slate-400 hover:text-slate-300 text-sm mb-4"
                >
                  Clear All
                </button>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium text-white mb-2">Upload Documents</p>
                <p className="text-slate-300 mb-4">or drag and drop files here (PDF only)</p>
              </div>
            )}
            
            <UIButton
              variant="darkOutline"
              onClick={() => {
                console.log('Choose File button clicked');
                if (fileInputRef.current) {
                  fileInputRef.current.click();
                } else {
                  console.error('File input ref is null');
                }
              }}
              className="mb-4"
            >
              Choose Files
            </UIButton>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              multiple
              onChange={(e) => handleFileSelect(e.target.files)}
              className="hidden"
            />
          </div>

          {/* Submit Button */}
          <div className="text-center">
            <UIButton
              onClick={handleSubmit}
              disabled={selectedFiles.length === 0 || isLoading}
              className="px-8 py-3 text-lg font-semibold"
            >
              {isLoading ? (
                <>
                  <UISpinner className="mr-2 text-white" />
                  Processing...
                </>
              ) : (
                'Submit for Triage'
              )}
            </UIButton>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <SpotlightCard className="custom-spotlight-card bg-black/5" spotlightColor="rgba(0, 229, 255, 0.15)">
            <div className="text-center">
              <Clock className="h-12 w-12 mx-auto mb-4 text-blue-400" />
              <h3 className="text-lg font-semibold text-white mb-2">Lightning Fast</h3>
              <p className="text-slate-300">Process claims in under 30 seconds</p>
            </div>
          </SpotlightCard>
          
          <SpotlightCard className="custom-spotlight-card bg-black/5" spotlightColor="rgba(34, 197, 94, 0.15)">
            <div className="text-center">
              <Shield className="h-12 w-12 mx-auto mb-4 text-green-400" />
              <h3 className="text-lg font-semibold text-white mb-2">AI-Powered</h3>
              <p className="text-slate-300">Advanced machine learning analysis</p>
            </div>
          </SpotlightCard>
          
          <SpotlightCard className="custom-spotlight-card bg-black/5" spotlightColor="rgba(168, 85, 247, 0.15)">
            <div className="text-center">
              <Users className="h-12 w-12 mx-auto mb-4 text-purple-400" />
              <h3 className="text-lg font-semibold text-white mb-2">Smart Routing</h3>
              <p className="text-slate-300">Automatically assign to the right team</p>
            </div>
          </SpotlightCard>
        </div>
        </div>
      </div>
    </div>
  );
};

// Triage Dashboard Component
const TriageDashboard = ({ claims, onReassign }) => {
  const getSeverityColor = (score) => {
    if (score >= 8) return 'text-red-400 bg-red-900/30';
    if (score >= 5) return 'text-yellow-400 bg-yellow-900/30';
    return 'text-green-400 bg-green-900/30';
  };

  const getFlagColor = (flag) => {
    const colors = {
      'Litigation Risk': 'bg-red-900/30 text-red-300',
      'Fraudulent Activity Suspected': 'bg-orange-900/30 text-orange-300',
      'High Value': 'bg-blue-900/30 text-blue-300',
      'Urgent Review': 'bg-purple-900/30 text-purple-300'
    };
    return colors[flag] || 'bg-gray-900/30 text-gray-300';
  };

  if (claims.length === 0) {
    return (
      <div className="pt-20 min-h-screen bg-black">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <FileText className="h-24 w-24 mx-auto mb-6 text-slate-600" />
            <h2 className="text-2xl font-bold text-white mb-4">No Claims Processed Yet</h2>
            <p className="text-slate-300 mb-8">Upload a claims document to see the triage results here.</p>
            <UIButton variant="primary" className="px-6 py-3">
              Upload Your First Claim
            </UIButton>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-20 min-h-screen bg-black">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Triage Dashboard</h2>
          <p className="text-slate-300">Review and manage processed claims</p>
        </div>

        <div className="grid gap-6">
          {claims.map((claim) => (
            <div key={claim.id} className="p-6 bg-slate-900 shadow-lg rounded-xl border border-slate-700">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold text-white">
                      Claim ID: {claim.id}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(claim.severity)}`}>
                      Severity: {claim.severity}/10
                    </span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm font-medium text-slate-400 mb-1">Complexity</p>
                      <p className="text-lg text-white">{claim.complexity}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-400 mb-1">Suggested Team</p>
                      <p className="text-lg text-white">{claim.suggestedTeam}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-400 mb-1">Upload Date</p>
                      <p className="text-lg text-white">{claim.uploadDate}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-400 mb-1">Status</p>
                      <p className="text-lg text-white">{claim.status}</p>
                    </div>
                  </div>

                  {claim.flags && claim.flags.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-slate-400 mb-2">Flags</p>
                      <div className="flex flex-wrap gap-2">
                        {claim.flags.map((flag, index) => (
                          <span
                            key={index}
                            className={`px-3 py-1 rounded-full text-xs font-medium ${getFlagColor(flag)}`}
                          >
                            {flag}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="mt-4 lg:mt-0 lg:ml-6">
                  <UIButton
                    variant="darkOutline"
                    onClick={() => onReassign(claim.id)}
                    className="w-full lg:w-auto"
                  >
                    <Scale className="h-4 w-4 mr-2" />
                    Reassign
                  </UIButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const [activeView, setActiveView] = useState('upload');
  const [claims, setClaims] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUpload = async (files) => {
    setIsLoading(true);
    
    try {
      // Simulate API call for each file
      const fileArray = Array.isArray(files) ? files : [files];
      await new Promise(resolve => setTimeout(resolve, 2000 * fileArray.length));
      
      // Mock API response for each file
      const newClaims = fileArray.map((file, index) => 
        generateMockClaim(`CL-${Date.now()}-${index}`)
      );

      setClaims(prevClaims => [...newClaims, ...prevClaims]);
      setActiveView('dashboard');
    } catch (error) {
      console.error('Error processing claims:', error);
      alert('Error processing claims. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReassign = (claimId) => {
    // Mock reassign functionality
    alert(`Reassigning claim ${claimId}...`);
  };

  // Navigation items with click handlers
  const navItems = [
    { 
      label: 'Upload', 
      href: '#upload', 
      onClick: (e) => {
        e.preventDefault();
        setActiveView('upload');
      }
    },
    { 
      label: 'Dashboard', 
      href: '#dashboard', 
      onClick: (e) => {
        e.preventDefault();
        setActiveView('dashboard');
      }
    },
    { label: 'About', href: '#about' },
    { label: 'Contact', href: '#contact' }
  ];

  return (
    <div className="min-h-screen bg-black relative">
      <PillNav
        logo="/src/logo.svg"
        logoAlt="Claims Triage Agent Logo"
        items={navItems}
        activeHref={activeView === 'upload' ? '#upload' : '#dashboard'}
        className="custom-nav"
        ease="power2.easeOut"
        baseColor="#000000"
        pillColor="#ffffff"
        hoveredPillTextColor="#ffffff"
        pillTextColor="#000000"
        onMobileMenuClick={() => {}}
      />
      
      {activeView === 'upload' ? (
        <UploadSection onFileUpload={handleFileUpload} isLoading={isLoading} />
      ) : (
        <TriageDashboard claims={claims} onReassign={handleReassign} />
      )}
    </div>
  );
};

export default App;
