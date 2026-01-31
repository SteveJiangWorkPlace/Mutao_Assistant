import React, { useState } from 'react'
import { Sidebar, Workspace } from '@/components'
import styles from './AppLayout.module.css'

const AppLayout: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [activeTool, setActiveTool] = useState<'ps-write' | 'ps-review' | 'rl-write' | 'cv-write'>('ps-write')
  const [apiKey, setApiKey] = useState('')

  const handleToolSelect = (tool: typeof activeTool) => {
    setActiveTool(tool)
  }

  const handleSidebarToggle = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed)
  }

  const handleApiKeyChange = (key: string) => {
    setApiKey(key)
  }

  return (
    <div className={styles.appLayout}>
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        activeTool={activeTool}
        onToolSelect={handleToolSelect}
        onToggle={handleSidebarToggle}
        apiKey={apiKey}
        onApiKeyChange={handleApiKeyChange}
      />
      <Workspace
        isSidebarCollapsed={isSidebarCollapsed}
        activeTool={activeTool}
        apiKey={apiKey}
      />
    </div>
  )
}

export default AppLayout