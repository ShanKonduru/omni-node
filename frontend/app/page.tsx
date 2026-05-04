'use client'

import { useState } from 'react'

export default function Home() {
  const [command, setCommand] = useState('')

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-bold mb-2">🌐 OmniNode</h1>
          <p className="text-gray-400 text-lg">Universal MCP Client</p>
        </header>

        <div className="max-w-4xl mx-auto">
          {/* Command Input */}
          <div className="bg-gray-800 rounded-lg shadow-2xl p-6 mb-6">
            <div className="flex items-center gap-3">
              <span className="text-green-400 text-xl font-mono">$</span>
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                placeholder="Type / to see available commands..."
                className="flex-1 bg-transparent border-none outline-none text-white text-lg font-mono placeholder-gray-500"
                autoFocus
              />
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="font-semibold mb-2">⚡ Quick Start</h3>
              <p className="text-sm text-gray-400">
                Press <code className="bg-gray-700 px-1 rounded">/</code> to see all commands
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="font-semibold mb-2">🔌 Servers</h3>
              <p className="text-sm text-gray-400">
                Connect to MCP servers via stdio or SSE
              </p>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <h3 className="font-semibold mb-2">🎯 Smart Routing</h3>
              <p className="text-sm text-gray-400">
                Automatic namespace resolution for tools
              </p>
            </div>
          </div>

          {/* Features */}
          <div className="bg-gray-800/30 rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-4">Features</h2>
            <ul className="space-y-2 text-gray-300">
              <li>✅ Universal MCP server registration</li>
              <li>✅ Slash-command interface with autocomplete</li>
              <li>✅ Smart namespace resolution</li>
              <li>✅ Encrypted credential storage</li>
              <li>✅ Real-time tool discovery</li>
              <li>✅ Execution history</li>
            </ul>
          </div>

          {/* Getting Started */}
          <div className="mt-8 text-center text-gray-400">
            <p>👉 To get started, register your first MCP server</p>
            <p className="text-sm mt-2">
              Backend: <code className="bg-gray-700 px-2 py-1 rounded">http://localhost:8000/docs</code>
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
