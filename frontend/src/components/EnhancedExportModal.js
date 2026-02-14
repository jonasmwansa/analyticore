import React, { useState } from 'react';
import { toast } from 'sonner';
import { 
  Download, FileSpreadsheet, FileText, Image, BarChart3, 
  Loader2, Check, ChevronDown
} from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { enhancedExportsAPI } from '../api';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';

const EXPORT_OPTIONS = [
  {
    id: 'statistics',
    title: 'Summary Statistics',
    description: 'Descriptive statistics for all columns (mean, std, min, max, etc.)',
    icon: FileSpreadsheet,
    formats: ['csv', 'excel'],
  },
  {
    id: 'correlation',
    title: 'Correlation Matrix',
    description: 'Correlation coefficients between numeric columns',
    icon: BarChart3,
    formats: ['csv', 'excel'],
    hasMethod: true,
  },
  {
    id: 'distribution',
    title: 'Distribution Analysis',
    description: 'Histogram data, box plots, and normality tests',
    icon: FileText,
    formats: ['csv', 'excel'],
  },
  {
    id: 'visualization_correlation',
    title: 'Correlation Heatmap',
    description: 'Visual heatmap of correlations',
    icon: Image,
    formats: ['png', 'svg'],
    isVisualization: true,
    chartType: 'correlation',
  },
  {
    id: 'visualization_distribution',
    title: 'Distribution Charts',
    description: 'Histogram and box plot visualizations',
    icon: Image,
    formats: ['png', 'svg'],
    isVisualization: true,
    chartType: 'distribution',
  },
  {
    id: 'visualization_summary',
    title: 'Summary Dashboard',
    description: 'Overview charts and statistics visual',
    icon: Image,
    formats: ['png', 'svg'],
    isVisualization: true,
    chartType: 'summary',
  },
];

export function EnhancedExportModal({ open, onOpenChange, projectId }) {
  const [exporting, setExporting] = useState({});
  const [selectedFormats, setSelectedFormats] = useState({});
  const [correlationMethod, setCorrelationMethod] = useState('pearson');

  const handleFormatChange = (optionId, format) => {
    setSelectedFormats({ ...selectedFormats, [optionId]: format });
  };

  const downloadFile = (data, filename, contentType) => {
    let blob;
    
    if (data.encoding === 'base64') {
      const byteCharacters = atob(data.content);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      blob = new Blob([byteArray], { type: contentType });
    } else {
      blob = new Blob([data.content], { type: contentType });
    }
    
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleExport = async (option) => {
    const format = selectedFormats[option.id] || option.formats[0];
    
    setExporting({ ...exporting, [option.id]: true });
    
    try {
      let response;
      
      if (option.isVisualization) {
        response = await enhancedExportsAPI.exportVisualization(
          projectId, 
          option.chartType, 
          format
        );
      } else if (option.id === 'statistics') {
        response = await enhancedExportsAPI.exportStatistics(projectId, format);
      } else if (option.id === 'correlation') {
        response = await enhancedExportsAPI.exportCorrelation(projectId, format, correlationMethod);
      } else if (option.id === 'distribution') {
        response = await enhancedExportsAPI.exportDistribution(projectId, format);
      }
      
      if (response?.data) {
        downloadFile(response.data, response.data.filename, response.data.content_type);
        toast.success(`${option.title} exported successfully`);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to export ${option.title}`);
    } finally {
      setExporting({ ...exporting, [option.id]: false });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[650px] bg-white max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-[#0F172A]">
            <Download className="w-5 h-5 text-[#6366F1]" />
            Export Analysis Data
          </DialogTitle>
        </DialogHeader>

        <p className="text-sm text-[#64748B] mb-4">
          Export detailed analysis results in various formats
        </p>

        <div className="space-y-3">
          {EXPORT_OPTIONS.map((option) => (
            <Card key={option.id} className="p-4 border border-slate-200" data-testid={`export-option-${option.id}`}>
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-[#EEF2FF] flex items-center justify-center flex-shrink-0">
                  <option.icon className="w-5 h-5 text-[#6366F1]" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-[#0F172A]">{option.title}</h4>
                  <p className="text-sm text-[#64748B] mb-3">{option.description}</p>
                  
                  <div className="flex items-center gap-3 flex-wrap">
                    {/* Format selector */}
                    <Select
                      value={selectedFormats[option.id] || option.formats[0]}
                      onValueChange={(value) => handleFormatChange(option.id, value)}
                    >
                      <SelectTrigger className="w-28 h-9 bg-white" data-testid={`format-select-${option.id}`}>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-white">
                        {option.formats.map((format) => (
                          <SelectItem key={format} value={format}>
                            {format.toUpperCase()}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    
                    {/* Method selector for correlation */}
                    {option.hasMethod && (
                      <Select
                        value={correlationMethod}
                        onValueChange={setCorrelationMethod}
                      >
                        <SelectTrigger className="w-32 h-9 bg-white">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-white">
                          <SelectItem value="pearson">Pearson</SelectItem>
                          <SelectItem value="spearman">Spearman</SelectItem>
                          <SelectItem value="kendall">Kendall</SelectItem>
                        </SelectContent>
                      </Select>
                    )}
                    
                    {/* Export button */}
                    <Button
                      onClick={() => handleExport(option)}
                      disabled={exporting[option.id]}
                      size="sm"
                      className="bg-[#6366F1] hover:bg-[#4F46E5] text-white h-9"
                      data-testid={`export-btn-${option.id}`}
                    >
                      {exporting[option.id] ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <Download className="w-4 h-4 mr-1" />
                          Export
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <div className="flex justify-end pt-4 border-t border-slate-200 mt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default EnhancedExportModal;
