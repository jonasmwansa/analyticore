import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { 
  Upload, FileSpreadsheet, Database, Table, 
  Check, X, Loader2, ExternalLink, RefreshCw
} from 'lucide-react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { integrationsAPI } from '../../api';

// Google Sheets Icon Component
const GoogleSheetsIcon = ({ className }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3Z" fill="#0F9D58"/>
    <path d="M19 3H12V21H19C20.1 21 21 20.1 21 19V5C21 3.9 20.1 3 19 3Z" fill="#0F9D58"/>
    <path d="M7 7H17V9H7V7Z" fill="white"/>
    <path d="M7 11H17V13H7V11Z" fill="white"/>
    <path d="M7 15H13V17H7V15Z" fill="white"/>
  </svg>
);

function DataSourcePicker({ projectId, onImportComplete }) {
  const [sourceType, setSourceType] = useState('file');
  const [loading, setLoading] = useState(false);
  
  // Google Sheets state
  const [sheetsStatus, setSheetsStatus] = useState({ connected: false, configured: false });
  const [spreadsheets, setSpreadsheets] = useState([]);
  const [selectedSpreadsheet, setSelectedSpreadsheet] = useState(null);
  const [sheetMetadata, setSheetMetadata] = useState(null);
  const [selectedSheet, setSelectedSheet] = useState('');
  const [sheetsLoading, setSheetsLoading] = useState(false);
  
  // Database state
  const [dbType, setDbType] = useState('mysql');
  const [dbConfig, setDbConfig] = useState({
    host: '',
    port: '',
    database: '',
    user: '',
    password: '',
    table: '',
    query: ''
  });
  const [dbTables, setDbTables] = useState([]);
  const [connectionTested, setConnectionTested] = useState(false);

  useEffect(() => {
    if (sourceType === 'google_sheets') {
      checkSheetsStatus();
    }
  }, [sourceType]);

  // Google Sheets Functions
  const checkSheetsStatus = async () => {
    try {
      const response = await integrationsAPI.getSheetsStatus();
      setSheetsStatus(response.data);
      if (response.data.connected) {
        loadSpreadsheets();
      }
    } catch (error) {
      console.error('Error checking sheets status:', error);
    }
  };

  const connectGoogleSheets = async () => {
    try {
      const response = await integrationsAPI.getSheetsAuthUrl();
      if (response.data.auth_url) {
        window.location.href = response.data.auth_url;
      } else if (response.data.error) {
        toast.error(response.data.error);
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to initiate Google Sheets connection');
    }
  };

  const disconnectGoogleSheets = async () => {
    try {
      await integrationsAPI.disconnectSheets();
      setSheetsStatus({ connected: false, configured: true });
      setSpreadsheets([]);
      setSelectedSpreadsheet(null);
      toast.success('Disconnected from Google Sheets');
    } catch (error) {
      toast.error('Failed to disconnect');
    }
  };

  const loadSpreadsheets = async () => {
    setSheetsLoading(true);
    try {
      const response = await integrationsAPI.listSpreadsheets();
      setSpreadsheets(response.data.spreadsheets || []);
    } catch (error) {
      toast.error('Failed to load spreadsheets');
    } finally {
      setSheetsLoading(false);
    }
  };

  const selectSpreadsheet = async (spreadsheetId) => {
    setSelectedSpreadsheet(spreadsheetId);
    setSelectedSheet('');
    setSheetMetadata(null);
    
    try {
      const response = await integrationsAPI.getSpreadsheetMetadata(spreadsheetId);
      setSheetMetadata(response.data);
      if (response.data.sheets?.length > 0) {
        setSelectedSheet(response.data.sheets[0].title);
      }
    } catch (error) {
      toast.error('Failed to load spreadsheet details');
    }
  };

  const importFromSheets = async () => {
    if (!selectedSpreadsheet) {
      toast.error('Please select a spreadsheet');
      return;
    }
    
    setLoading(true);
    try {
      const response = await integrationsAPI.importFromSheets(projectId, {
        spreadsheet_id: selectedSpreadsheet,
        sheet_name: selectedSheet || null
      });
      toast.success('Data imported successfully from Google Sheets!');
      onImportComplete?.(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  // Database Functions
  const testConnection = async () => {
    if (!dbConfig.host || !dbConfig.database || !dbConfig.user) {
      toast.error('Please fill in host, database, and user fields');
      return;
    }
    
    setLoading(true);
    try {
      const testFn = dbType === 'mysql' 
        ? integrationsAPI.testMySQLConnection 
        : integrationsAPI.testPostgreSQLConnection;
      
      const response = await testFn({
        host: dbConfig.host,
        port: dbConfig.port || (dbType === 'mysql' ? '3306' : '5432'),
        database: dbConfig.database,
        user: dbConfig.user,
        password: dbConfig.password
      });
      
      if (response.data.success) {
        toast.success('Connection successful!');
        setDbTables(response.data.tables || []);
        setConnectionTested(true);
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error(error.response?.data?.message || 'Connection failed');
    } finally {
      setLoading(false);
    }
  };

  const importFromDatabase = async () => {
    if (!dbConfig.table && !dbConfig.query) {
      toast.error('Please select a table or enter a query');
      return;
    }
    
    setLoading(true);
    try {
      const response = await integrationsAPI.importFromDatabase(projectId, {
        db_type: dbType,
        host: dbConfig.host,
        port: dbConfig.port || (dbType === 'mysql' ? '3306' : '5432'),
        database: dbConfig.database,
        user: dbConfig.user,
        password: dbConfig.password,
        table: dbConfig.table,
        query: dbConfig.query
      });
      toast.success(`Data imported successfully from ${dbType.toUpperCase()}!`);
      onImportComplete?.(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Import failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Source Type Selector */}
      <div className="flex gap-3 justify-center flex-wrap">
        <Button
          variant={sourceType === 'file' ? 'default' : 'outline'}
          onClick={() => setSourceType('file')}
          data-testid="source-file-btn"
          className={sourceType === 'file' ? 'bg-[#6366F1] text-white' : ''}
        >
          <Upload className="w-4 h-4 mr-2" />
          File Upload
        </Button>
        <Button
          variant={sourceType === 'google_sheets' ? 'default' : 'outline'}
          onClick={() => setSourceType('google_sheets')}
          data-testid="source-sheets-btn"
          className={sourceType === 'google_sheets' ? 'bg-[#0F9D58] text-white' : ''}
        >
          <GoogleSheetsIcon className="w-4 h-4 mr-2" />
          Google Sheets
        </Button>
        <Button
          variant={sourceType === 'database' ? 'default' : 'outline'}
          onClick={() => setSourceType('database')}
          data-testid="source-db-btn"
          className={sourceType === 'database' ? 'bg-[#3B82F6] text-white' : ''}
        >
          <Database className="w-4 h-4 mr-2" />
          Database
        </Button>
      </div>

      {/* File Upload Content */}
      {sourceType === 'file' && (
        <Card className="bg-white border border-slate-200 rounded-xl p-8 shadow-sm">
          <div className="text-center py-8">
            <div className="w-20 h-20 bg-[#EEF2FF] rounded-full flex items-center justify-center mx-auto mb-6">
              <Upload className="w-10 h-10 text-[#6366F1]" />
            </div>
            <h2 className="text-2xl font-bold text-[#0F172A] mb-3">Upload Your Data</h2>
            <p className="text-[#64748B] mb-6">Supported formats: CSV, Excel (.xlsx, .xls), JSON</p>
            
            <input
              type="file"
              accept=".csv,.xlsx,.xls,.json"
              onChange={(e) => {
                if (e.target.files[0]) {
                  onImportComplete?.({ file: e.target.files[0] });
                }
              }}
              disabled={loading}
              id="file-upload"
              data-testid="file-upload-input"
              className="hidden"
            />
            <label htmlFor="file-upload">
              <Button
                as="span"
                disabled={loading}
                data-testid="upload-file-btn"
                className="bg-[#6366F1] hover:bg-[#4F46E5] text-white rounded-lg h-12 px-8 font-semibold shadow-md shadow-indigo-500/20 cursor-pointer"
              >
                {loading ? 'Uploading...' : 'Choose File'}
              </Button>
            </label>
          </div>
        </Card>
      )}

      {/* Google Sheets Content */}
      {sourceType === 'google_sheets' && (
        <Card className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          {!sheetsStatus.configured ? (
            <div className="text-center py-8">
              <GoogleSheetsIcon className="w-16 h-16 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-[#0F172A] mb-2">Google Sheets Not Configured</h3>
              <p className="text-[#64748B] mb-4">
                To enable Google Sheets integration, please configure the following environment variables:
              </p>
              <div className="bg-slate-50 rounded-lg p-4 text-left max-w-md mx-auto">
                <code className="text-sm text-slate-700">
                  GOOGLE_SHEETS_CLIENT_ID=your_client_id<br/>
                  GOOGLE_SHEETS_CLIENT_SECRET=your_client_secret
                </code>
              </div>
            </div>
          ) : !sheetsStatus.connected ? (
            <div className="text-center py-8">
              <GoogleSheetsIcon className="w-16 h-16 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-[#0F172A] mb-2">Connect to Google Sheets</h3>
              <p className="text-[#64748B] mb-6">
                Connect your Google account to import data from your spreadsheets
              </p>
              <Button
                onClick={connectGoogleSheets}
                data-testid="connect-sheets-btn"
                className="bg-[#0F9D58] hover:bg-[#0D8A4C] text-white rounded-lg h-12 px-8 font-semibold"
              >
                <ExternalLink className="w-4 h-4 mr-2" />
                Connect Google Sheets
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Connected Header */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <Check className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-[#0F172A]">Connected</p>
                    <p className="text-sm text-[#64748B]">{sheetsStatus.email}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={loadSpreadsheets} disabled={sheetsLoading}>
                    <RefreshCw className={`w-4 h-4 mr-1 ${sheetsLoading ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                  <Button variant="outline" size="sm" onClick={disconnectGoogleSheets}>
                    Disconnect
                  </Button>
                </div>
              </div>

              {/* Spreadsheet Selection */}
              <div className="space-y-4">
                <Label className="text-[#0F172A] font-medium">Select Spreadsheet</Label>
                {sheetsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-[#6366F1]" />
                  </div>
                ) : spreadsheets.length === 0 ? (
                  <p className="text-[#64748B] text-center py-4">No spreadsheets found</p>
                ) : (
                  <Select value={selectedSpreadsheet || ''} onValueChange={selectSpreadsheet}>
                    <SelectTrigger data-testid="spreadsheet-select" className="bg-white">
                      <SelectValue placeholder="Choose a spreadsheet..." />
                    </SelectTrigger>
                    <SelectContent className="bg-white max-h-64">
                      {spreadsheets.map((sheet) => (
                        <SelectItem key={sheet.id} value={sheet.id}>
                          <div className="flex items-center gap-2">
                            <FileSpreadsheet className="w-4 h-4 text-[#0F9D58]" />
                            {sheet.name}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}

                {/* Sheet Selection (if spreadsheet has multiple sheets) */}
                {sheetMetadata && sheetMetadata.sheets?.length > 1 && (
                  <div className="space-y-2">
                    <Label className="text-[#0F172A] font-medium">Select Sheet</Label>
                    <Select value={selectedSheet} onValueChange={setSelectedSheet}>
                      <SelectTrigger data-testid="sheet-select" className="bg-white">
                        <SelectValue placeholder="Choose a sheet..." />
                      </SelectTrigger>
                      <SelectContent className="bg-white">
                        {sheetMetadata.sheets.map((sheet) => (
                          <SelectItem key={sheet.id} value={sheet.title}>
                            <div className="flex items-center justify-between gap-4">
                              <span>{sheet.title}</span>
                              <span className="text-xs text-[#64748B]">
                                {sheet.row_count} rows × {sheet.column_count} cols
                              </span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Import Button */}
                {selectedSpreadsheet && (
                  <Button
                    onClick={importFromSheets}
                    disabled={loading}
                    data-testid="import-sheets-btn"
                    className="w-full bg-[#0F9D58] hover:bg-[#0D8A4C] text-white rounded-lg h-12 font-semibold"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Importing...
                      </>
                    ) : (
                      <>
                        <FileSpreadsheet className="w-4 h-4 mr-2" />
                        Import Data
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          )}
        </Card>
      )}

      {/* Database Content */}
      {sourceType === 'database' && (
        <Card className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
          <div className="space-y-6">
            {/* Database Type Tabs */}
            <Tabs value={dbType} onValueChange={(v) => { setDbType(v); setConnectionTested(false); setDbTables([]); }}>
              <TabsList className="bg-slate-100 p-1 rounded-lg">
                <TabsTrigger 
                  value="mysql" 
                  className="data-[state=active]:bg-white data-[state=active]:text-[#3B82F6] rounded-md"
                >
                  MySQL
                </TabsTrigger>
                <TabsTrigger 
                  value="postgresql"
                  className="data-[state=active]:bg-white data-[state=active]:text-[#3B82F6] rounded-md"
                >
                  PostgreSQL
                </TabsTrigger>
              </TabsList>

              <TabsContent value="mysql" className="space-y-4 mt-4">
                <ConnectionForm 
                  config={dbConfig} 
                  setConfig={setDbConfig} 
                  defaultPort="3306"
                />
              </TabsContent>
              
              <TabsContent value="postgresql" className="space-y-4 mt-4">
                <ConnectionForm 
                  config={dbConfig} 
                  setConfig={setDbConfig} 
                  defaultPort="5432"
                />
              </TabsContent>
            </Tabs>

            {/* Test Connection Button */}
            <Button
              onClick={testConnection}
              disabled={loading}
              variant="outline"
              data-testid="test-connection-btn"
              className="w-full"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : connectionTested ? (
                <Check className="w-4 h-4 mr-2 text-green-600" />
              ) : (
                <Database className="w-4 h-4 mr-2" />
              )}
              {connectionTested ? 'Connection Verified' : 'Test Connection'}
            </Button>

            {/* Table Selection */}
            {connectionTested && dbTables.length > 0 && (
              <div className="space-y-4 pt-4 border-t border-slate-200">
                <div className="space-y-2">
                  <Label className="text-[#0F172A] font-medium">Select Table</Label>
                  <Select 
                    value={dbConfig.table} 
                    onValueChange={(v) => setDbConfig({...dbConfig, table: v, query: ''})}
                  >
                    <SelectTrigger data-testid="table-select" className="bg-white">
                      <SelectValue placeholder="Choose a table..." />
                    </SelectTrigger>
                    <SelectContent className="bg-white max-h-64">
                      {dbTables.map((table) => (
                        <SelectItem key={table} value={table}>
                          <div className="flex items-center gap-2">
                            <Table className="w-4 h-4 text-[#3B82F6]" />
                            {table}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="text-center text-sm text-[#64748B]">or</div>

                <div className="space-y-2">
                  <Label className="text-[#0F172A] font-medium">Custom SQL Query</Label>
                  <textarea
                    value={dbConfig.query}
                    onChange={(e) => setDbConfig({...dbConfig, query: e.target.value, table: ''})}
                    placeholder="SELECT * FROM your_table WHERE ..."
                    className="w-full h-24 px-3 py-2 border border-slate-200 rounded-lg text-sm font-mono resize-none focus:outline-none focus:ring-2 focus:ring-[#3B82F6]"
                    data-testid="sql-query-input"
                  />
                </div>

                {/* Import Button */}
                <Button
                  onClick={importFromDatabase}
                  disabled={loading || (!dbConfig.table && !dbConfig.query)}
                  data-testid="import-db-btn"
                  className="w-full bg-[#3B82F6] hover:bg-[#2563EB] text-white rounded-lg h-12 font-semibold"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Importing...
                    </>
                  ) : (
                    <>
                      <Database className="w-4 h-4 mr-2" />
                      Import Data
                    </>
                  )}
                </Button>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}

// Connection Form Component
function ConnectionForm({ config, setConfig, defaultPort }) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label className="text-[#0F172A] font-medium">Host</Label>
        <Input
          value={config.host}
          onChange={(e) => setConfig({...config, host: e.target.value})}
          placeholder="localhost"
          data-testid="db-host-input"
        />
      </div>
      <div className="space-y-2">
        <Label className="text-[#0F172A] font-medium">Port</Label>
        <Input
          value={config.port}
          onChange={(e) => setConfig({...config, port: e.target.value})}
          placeholder={defaultPort}
          data-testid="db-port-input"
        />
      </div>
      <div className="space-y-2">
        <Label className="text-[#0F172A] font-medium">Database</Label>
        <Input
          value={config.database}
          onChange={(e) => setConfig({...config, database: e.target.value})}
          placeholder="my_database"
          data-testid="db-name-input"
        />
      </div>
      <div className="space-y-2">
        <Label className="text-[#0F172A] font-medium">Username</Label>
        <Input
          value={config.user}
          onChange={(e) => setConfig({...config, user: e.target.value})}
          placeholder="root"
          data-testid="db-user-input"
        />
      </div>
      <div className="col-span-2 space-y-2">
        <Label className="text-[#0F172A] font-medium">Password</Label>
        <Input
          type="password"
          value={config.password}
          onChange={(e) => setConfig({...config, password: e.target.value})}
          placeholder="••••••••"
          data-testid="db-password-input"
        />
      </div>
    </div>
  );
}

export default DataSourcePicker;
