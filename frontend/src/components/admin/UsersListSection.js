import React from 'react';
import { Card } from '../ui/card';

export function UsersListSection({ users }) {
  return (
    <div className="space-y-6" data-testid="users-list-section">
      <h2 className="text-xl font-bold text-white">All Users ({users.length})</h2>
      
      <Card className="bg-slate-800 border-slate-700 p-6">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Email</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Name</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Status</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Projects</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Plan</th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-slate-400">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-sm text-white">{user.email}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{user.name}</td>
                  <td className="py-3 px-4">
                    {user.is_verified ? (
                      <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">Verified</span>
                    ) : (
                      <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded-full">Unverified</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-sm font-bold text-indigo-400">{user.project_count}</td>
                  <td className="py-3 px-4 text-sm text-slate-400 capitalize">{user.subscription}</td>
                  <td className="py-3 px-4 text-sm text-slate-400">{new Date(user.date_joined).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

export default UsersListSection;
