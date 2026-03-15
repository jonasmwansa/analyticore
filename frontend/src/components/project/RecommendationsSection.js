import React from 'react';
import { Wand2, AlertCircle, Play } from 'lucide-react';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Checkbox } from '../ui/checkbox';

export function RecommendationsSection({ 
  recommendations, 
  selectedRules, 
  transforming, 
  onToggleRecommendation, 
  onApplyTransformations,
  onGoToAnalyze,
  isRecommendationSelected
}) {
  if (recommendations.length === 0) {
    return (
      <Card className="bg-white border border-slate-200 rounded-xl p-12 shadow-sm text-center">
        <Wand2 className="w-16 h-16 text-[#94A3B8] mx-auto mb-4" />
        <h3 className="text-xl font-bold text-[#0F172A] mb-2">No Recommendations Yet</h3>
        <p className="text-[#64748B] mb-6">Run the pipeline to generate cleaning and transformation recommendations from your dataset.</p>
        <Button
          onClick={onGoToAnalyze}
          data-testid="goto-analyze-btn"
          className="bg-[#8B5CF6] hover:bg-[#7C3AED] text-white rounded-lg h-11 px-6 font-semibold shadow-md shadow-violet-500/20"
        >
          Run Pipeline
        </Button>
      </Card>
    );
  }

  return (
    <>
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-2xl font-bold text-[#0F172A] mb-1">AI Cleaning Recommendations</h3>
          <p className="text-[#64748B]">Review the generated recommendations, then choose which extra transformations to apply.</p>
        </div>
        <Button
          onClick={onApplyTransformations}
          disabled={selectedRules.length === 0 || transforming}
          data-testid="apply-transformations-btn"
          className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-11 px-6 font-semibold shadow-md shadow-indigo-500/20 disabled:opacity-50"
        >
          {transforming ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              Applying...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Apply Selected ({selectedRules.length})
            </>
          )}
        </Button>
      </div>

      <div className="space-y-3">
        {recommendations.map((rec, index) => (
          <Card
            key={index}
            data-testid={`recommendation-${index}`}
            className={`recommendation-item bg-white border rounded-xl p-5 shadow-sm cursor-pointer ${
              isRecommendationSelected(index) ? 'border-[#6366F1] ring-2 ring-[#6366F1] ring-opacity-20' : 'border-slate-200'
            }`}
            onClick={() => onToggleRecommendation(index)}
          >
            <div className="flex items-start gap-4">
              <Checkbox
                checked={isRecommendationSelected(index)}
                onCheckedChange={() => onToggleRecommendation(index)}
                data-testid={`recommendation-checkbox-${index}`}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Badge className="bg-[#EEF2FF] text-[#6366F1] hover:bg-[#EEF2FF] font-semibold">
                    {rec.column}
                  </Badge>
                  <Badge className="bg-slate-100 text-slate-700 hover:bg-slate-100 font-medium">
                    {rec.action_type.replace('_', ' ').toUpperCase()}
                  </Badge>
                </div>
                <p className="text-sm text-[#F59E0B] font-medium mb-1">
                  <AlertCircle className="w-4 h-4 inline mr-1" />
                  {rec.issue}
                </p>
                <p className="text-sm text-[#0F172A]">{rec.recommendation}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </>
  );
}

export default RecommendationsSection;
