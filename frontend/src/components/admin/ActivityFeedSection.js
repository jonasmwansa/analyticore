import React from 'react';
import { Activity } from 'lucide-react';
import { Card } from '../ui/card';

export function ActivityFeedSection({ activityFeed }) {
  return (
    <div className="space-y-6" data-testid="feed-section">
      <h2 className="text-xl font-bold text-white">Real-time Activity Feed</h2>
      
      <Card className="bg-slate-800 border-slate-700 p-6">
        <div className="space-y-3 max-h-[600px] overflow-y-auto">
          {activityFeed.map((activity, idx) => (
            <div key={idx} className="flex items-start gap-4 p-3 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors">
              <div className="w-10 h-10 bg-indigo-500/20 rounded-full flex items-center justify-center flex-shrink-0">
                <Activity className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">{activity.user_name || activity.user_email}</span>
                  <span className="text-xs text-slate-500">{new Date(activity.timestamp).toLocaleString()}</span>
                </div>
                <p className="text-sm text-slate-400 mt-1">
                  <span className="text-indigo-400 capitalize">{activity.action?.replace(/_/g, ' ')}</span>
                  {' on '}
                  <span className="text-slate-300">{activity.resource_type}</span>
                </p>
              </div>
            </div>
          ))}
          {activityFeed.length === 0 && (
            <p className="text-slate-400 text-center py-8">No recent activity</p>
          )}
        </div>
      </Card>
    </div>
  );
}

export default ActivityFeedSection;
