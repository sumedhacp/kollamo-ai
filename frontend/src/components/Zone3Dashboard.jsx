import React, { useState, useMemo } from 'react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, 
  BarChart, Bar, XAxis, YAxis 
} from 'recharts';
import { BarChart3, Search, Download, TrendingUp, Filter } from 'lucide-react';

const SENTIMENT_COLORS = {
  Positive: '#10b981', // Emerald
  Negative: '#f43f5e', // Rose
  Neutral: '#64748b'   // Slate
};

export default function Zone3Dashboard({ batchData }) {
  const [activeTab, setActiveTab] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Zero-latency in-memory comment filter
  const filteredComments = useMemo(() => {
    if (!batchData?.comments) return [];
    return batchData.comments.filter((item) => {
      const matchesTab = activeTab === 'ALL' || item.label === activeTab;
      const matchesQuery = item.comment.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.author.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesTab && matchesQuery;
    });
  }, [batchData, activeTab, searchQuery]);

  const pieChartData = useMemo(() => {
    if (!batchData?.sentiment_distribution) return [];
    return Object.entries(batchData.sentiment_distribution).map(([name, value]) => ({
      name,
      value
    }));
  }, [batchData]);

  // Export to CSV Function
  const exportCSV = () => {
    if (!filteredComments.length) return;
    const headers = "Comment ID,Author,Sentiment,Confidence,Likes,Text\n";
    const rows = filteredComments.map(c => 
      `"${c.comment_id}","${c.author}","${c.label}","${c.confidence}%","${c.like_count}","${c.comment.replace(/"/g, '""')}"`
    ).join("\n");
    
    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `kollamo_sentiment_report_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!batchData) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center text-slate-500">
        <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-20 text-emerald-400" />
        <h3 className="text-sm font-semibold text-slate-400">Zone 3: Sentiment Telemetry Standby</h3>
        <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
          Extract and analyze comments in Zone 2 to trigger real-time statistical distributions, polarity meters, and filtered audits.
        </p>
      </div>
    );
  }

  const nss = batchData.net_sentiment_score ?? 0;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
            <BarChart3 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Zone 3: Sentiment Telemetry & Filter Matrix</h2>
            <p className="text-xs text-slate-400">Global distribution, Net Sentiment Score (NSS), and granular table audits</p>
          </div>
        </div>

        <button
          onClick={exportCSV}
          className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3 py-2 rounded-xl transition flex items-center gap-1.5 border border-slate-700"
        >
          <Download className="w-3.5 h-3.5 text-emerald-400" />
          <span>Export CSV</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400 font-medium">Total Analyzed</span>
          <div className="text-3xl font-extrabold text-white mt-1">{batchData.total_analyzed}</div>
          <div className="text-[11px] text-slate-500 mt-1">Evaluated items</div>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400 font-medium">Positive Ratio</span>
          <div className="text-3xl font-extrabold text-emerald-400 mt-1">
            {batchData.sentiment_percentages.Positive || 0}%
          </div>
          <div className="text-[11px] text-slate-500 mt-1">{batchData.sentiment_distribution.Positive} comments</div>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400 font-medium">Negative Ratio</span>
          <div className="text-3xl font-extrabold text-rose-400 mt-1">
            {batchData.sentiment_percentages.Negative || 0}%
          </div>
          <div className="text-[11px] text-slate-500 mt-1">{batchData.sentiment_distribution.Negative} comments</div>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400 font-medium">Net Sentiment Score (NSS)</span>
          <div className={`text-3xl font-extrabold mt-1 ${nss >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {nss > 0 ? `+${nss}` : nss}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Benchmark: -100 to +100</div>
        </div>
      </div>

      {/* Visual Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 h-64 flex flex-col items-center justify-center">
          <span className="text-xs text-slate-400 font-semibold mb-2">Sentiment Proportions (Donut)</span>
          <ResponsiveContainer width="100%" height="85%">
            <PieChart>
              <Pie
                data={pieChartData}
                dataKey="value"
                nameKey="name"
                innerRadius={50}
                outerRadius={75}
                paddingAngle={4}
              >
                {pieChartData.map((entry) => (
                  <Cell key={entry.name} fill={SENTIMENT_COLORS[entry.name] || '#64748b'} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: 8, fontSize: 12 }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Legend verticalAlign="bottom" height={24} iconSize={8} wrapperStyle={{ fontSize: 11 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 h-64 flex flex-col items-center justify-center">
          <span className="text-xs text-slate-400 font-semibold mb-2">Class Count Comparison</span>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={pieChartData}>
              <XAxis dataKey="name" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#090d16', borderColor: '#1e293b', borderRadius: 8, fontSize: 12 }}
                itemStyle={{ color: '#f8fafc' }}
              />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {pieChartData.map((entry) => (
                  <Cell key={entry.name} fill={SENTIMENT_COLORS[entry.name] || '#64748b'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Filter Tabs & In-Memory Search */}
      <div className="space-y-4 pt-2">
        <div className="flex flex-col md:flex-row justify-between gap-3 items-center">
          <div className="flex gap-2">
            {['ALL', 'Positive', 'Negative', 'Neutral'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition ${
                  activeTab === tab
                    ? 'bg-slate-100 border-slate-100 text-slate-950 font-bold'
                    : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          <div className="relative w-full md:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search comments or author..."
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
            />
          </div>
        </div>

        {/* Filtered Comments Table */}
        <div className="border border-slate-800 rounded-xl overflow-hidden max-h-80 overflow-y-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider sticky top-0">
              <tr>
                <th className="p-3">Comment</th>
                <th className="p-3 w-28">Sentiment</th>
                <th className="p-3 w-24 text-right">Confidence</th>
                <th className="p-3 w-28">Author</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 bg-slate-950/40">
              {filteredComments.length > 0 ? (
                filteredComments.map((item) => (
                  <tr key={item.comment_id} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 text-slate-200 font-normal">{item.comment}</td>
                    <td className="p-3">
                      <span
                        className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full inline-block"
                        style={{
                          backgroundColor: `${SENTIMENT_COLORS[item.label]}15`,
                          color: SENTIMENT_COLORS[item.label],
                          border: `1px solid ${SENTIMENT_COLORS[item.label]}30`
                        }}
                      >
                        {item.label}
                      </span>
                    </td>
                    <td className="p-3 text-right font-mono text-slate-400">{item.confidence}%</td>
                    <td className="p-3 text-slate-400 truncate max-w-[120px]">{item.author}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="p-6 text-center text-slate-500">
                    No comments match the active filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}