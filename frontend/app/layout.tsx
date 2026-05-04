import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'OmniNode - Universal MCP Client',
  description: 'A universal MCP client with slash-command interface',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
