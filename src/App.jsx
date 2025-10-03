import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, Clock, Users, Shield, Scale } from 'lucide-react';

// Lightweight local UI primitives
const UIButton = ({ children, className = '', variant = 'secondary', ...props }) => {
  const base = 'inline-flex items-center justify-center rounded-md px-4 py-2 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-slate-200 text-slate-800 hover:bg-slate-300 focus:ring-slate-400',
    outline: 'border border-slate-300 text-slate-800 hover:bg-slate-50',
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

// Header Component
const Header = ({ activeView, setActiveView }) => {
  return (
    <header className="bg-blue-600 text-white shadow-lg fixed w-full top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <FileText className="h-8 w-8 mr-3" />
            <h1 className="text-xl font-bold">Claims Triage Agent</h1>
          </div>
          <nav className="flex space-x-4">
            <UIButton
              variant={activeView === 'upload' ? 'primary' : 'secondary'}
              onClick={() => setActiveView('upload')}
              className="px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Upload Claim
            </UIButton>
            <UIButton
              variant={activeView === 'dashboard' ? 'primary' : 'secondary'}
              onClick={() => setActiveView('dashboard')}
              className="px-4 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Triage Dashboard
            </UIButton>
          </nav>
        </div>
      </div>
    </header>
  );
};

// Upload Section Component
const UploadSection = ({ onFileUpload, isLoading }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    } else {
      alert('Please select a PDF file');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFileSelect(file);
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
    if (selectedFile) {
      await onFileUpload(selectedFile);
    }
  };

  return (
    <div className="pt-20 min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-800 mb-6">
            Intelligent Claims Triage, <span className="text-blue-600">Instantly</span>
          </h1>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Upload a claims document to automatically analyze, score, and route it to the correct team.
            Our AI-powered system processes your claims in seconds.
          </p>
        </div>

        {/* Upload Area */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div
            className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
              isDragOver 
                ? 'border-blue-500 bg-blue-50' 
                : selectedFile 
                  ? 'border-green-500 bg-green-50' 
                  : 'border-slate-300 hover:border-blue-400'
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <Upload className="h-16 w-16 mx-auto mb-4 text-slate-400" />
            {selectedFile ? (
              <div>
                <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <p className="text-lg font-medium text-slate-800 mb-2">File Selected</p>
                <p className="text-slate-600 mb-4">{selectedFile.name}</p>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium text-slate-800 mb-2">Upload Document</p>
                <p className="text-slate-600 mb-4">or drag and drop a file here</p>
              </div>
            )}
            
            <UIButton
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              className="mb-4"
            >
              Choose File
            </UIButton>
            
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={(e) => handleFileSelect(e.target.files[0])}
              className="hidden"
            />
          </div>

          {/* Submit Button */}
          <div className="text-center">
            <UIButton
              onClick={handleSubmit}
              disabled={!selectedFile || isLoading}
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
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <Clock className="h-12 w-12 mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-semibold text-slate-800 mb-2">Lightning Fast</h3>
            <p className="text-slate-600">Process claims in under 30 seconds</p>
          </div>
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <Shield className="h-12 w-12 mx-auto mb-4 text-green-600" />
            <h3 className="text-lg font-semibold text-slate-800 mb-2">AI-Powered</h3>
            <p className="text-slate-600">Advanced machine learning analysis</p>
          </div>
          <div className="text-center p-6 bg-white rounded-lg shadow-md">
            <Users className="h-12 w-12 mx-auto mb-4 text-purple-600" />
            <h3 className="text-lg font-semibold text-slate-800 mb-2">Smart Routing</h3>
            <p className="text-slate-600">Automatically assign to the right team</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Triage Dashboard Component
const TriageDashboard = ({ claims, onReassign }) => {
  const getSeverityColor = (score) => {
    if (score >= 8) return 'text-red-600 bg-red-100';
    if (score >= 5) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getFlagColor = (flag) => {
    const colors = {
      'Litigation Risk': 'bg-red-100 text-red-800',
      'Fraudulent Activity Suspected': 'bg-orange-100 text-orange-800',
      'High Value': 'bg-blue-100 text-blue-800',
      'Urgent Review': 'bg-purple-100 text-purple-800'
    };
    return colors[flag] || 'bg-gray-100 text-gray-800';
  };

  if (claims.length === 0) {
    return (
      <div className="pt-20 min-h-screen bg-slate-50">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <FileText className="h-24 w-24 mx-auto mb-6 text-slate-300" />
            <h2 className="text-2xl font-bold text-slate-800 mb-4">No Claims Processed Yet</h2>
            <p className="text-slate-600 mb-8">Upload a claims document to see the triage results here.</p>
            <UIButton variant="primary" className="px-6 py-3">
              Upload Your First Claim
            </UIButton>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-20 min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-slate-800 mb-2">Triage Dashboard</h2>
          <p className="text-slate-600">Review and manage processed claims</p>
        </div>

        <div className="grid gap-6">
          {claims.map((claim) => (
            <UICard key={claim.id} className="p-6 bg-white shadow-lg rounded-xl">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-semibold text-slate-800">
                      Claim ID: {claim.id}
                    </h3>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(claim.severity)}`}>
                      Severity: {claim.severity}/10
                    </span>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm font-medium text-slate-600 mb-1">Complexity</p>
                      <p className="text-lg text-slate-800">{claim.complexity}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-600 mb-1">Suggested Team</p>
                      <p className="text-lg text-slate-800">{claim.suggestedTeam}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-600 mb-1">Upload Date</p>
                      <p className="text-lg text-slate-800">{claim.uploadDate}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-600 mb-1">Status</p>
                      <p className="text-lg text-slate-800">{claim.status}</p>
                    </div>
                  </div>

                  {claim.flags && claim.flags.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-medium text-slate-600 mb-2">Flags</p>
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
                    variant="outline"
                    onClick={() => onReassign(claim.id)}
                    className="w-full lg:w-auto"
                  >
                    <Scale className="h-4 w-4 mr-2" />
                    Reassign
                  </UIButton>
                </div>
              </div>
            </UICard>
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

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock API response
      const mockResponse = {
        success: true,
        data: generateMockClaim(`CL-${Date.now()}`)
      };

      if (mockResponse.success) {
        setClaims(prevClaims => [mockResponse.data, ...prevClaims]);
        setActiveView('dashboard');
      }
    } catch (error) {
      console.error('Error processing claim:', error);
      alert('Error processing claim. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReassign = (claimId) => {
    // Mock reassign functionality
    alert(`Reassigning claim ${claimId}...`);
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Header activeView={activeView} setActiveView={setActiveView} />
      
      {activeView === 'upload' ? (
        <UploadSection onFileUpload={handleFileUpload} isLoading={isLoading} />
      ) : (
        <TriageDashboard claims={claims} onReassign={handleReassign} />
      )}
    </div>
  );
};

export default App;
