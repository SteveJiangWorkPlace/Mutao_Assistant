import React from 'react'
import { Icon, Input } from '@/components'
import styles from './Sidebar.module.css'

export interface SidebarProps {
  isCollapsed: boolean
  activeTool: 'ps-write' | 'ps-review' | 'rl-write' | 'cv-write'
  onToolSelect: (tool: SidebarProps['activeTool']) => void
  onToggle: () => void
  apiKey: string
  onApiKeyChange: (key: string) => void
}

const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  activeTool,
  onToolSelect,
  onToggle,
  apiKey,
  onApiKeyChange
}) => {
  const menuItems = [
    {
      id: 'ps-write' as const,
      label: 'PS写作',
      icon: 'psWrite' as const
    },
    {
      id: 'ps-review' as const,
      label: 'PS修改',
      icon: 'psReview' as const
    },
    {
      id: 'rl-write' as const,
      label: 'RL写作',
      icon: 'rlWrite' as const
    },
    {
      id: 'cv-write' as const,
      label: 'CV写作',
      icon: 'cvWrite' as const
    }
  ]

  return (
    <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
      <div className={styles.header}>
        {!isCollapsed && (
          <div className={styles.logo}>
            <img
              src="/logopic.svg"
              alt="木桃留学"
              className={styles.logoImage}
            />
            <div className={styles.logoTexts}>
              <span className={styles.logoText}>木桃留学</span>
              <span className={styles.logoSubtext}>文书写作辅助工具</span>
            </div>
          </div>
        )}
        <button
          className={styles.toggleButton}
          onClick={onToggle}
          aria-label={isCollapsed ? '展开侧边栏' : '折叠侧边栏'}
          title={isCollapsed ? '展开侧边栏' : '折叠侧边栏'}
        >
          <Icon
            name={isCollapsed ? 'expand' : 'collapse'}
            size="sm"
            variant="default"
          />
        </button>
      </div>

      <nav className={styles.nav}>
        <ul className={styles.menuList}>
          {menuItems.map((item) => {
            const isActive = activeTool === item.id
            return (
              <li key={item.id} className={styles.menuItem}>
                <button
                  className={`${styles.menuButton} ${isActive ? styles.active : ''}`}
                  onClick={() => onToolSelect(item.id)}
                  aria-label={item.label}
                  title={item.label}
                >
                  <span className={styles.menuIcon}>
                    <Icon
                      name={item.icon}
                      size="md"
                      variant="default"
                    />
                  </span>
                  {!isCollapsed && (
                    <span className={styles.menuLabel}>{item.label}</span>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {!isCollapsed && (
        <>
          <div className={styles.apiKeySection}>
            <Input
              label="Google API Key"
              type="password"
              value={apiKey}
              onChange={(e) => onApiKeyChange(e.target.value)}
              placeholder="请输入Google API Key"
              fullWidth
            />
          </div>
          <div className={styles.footer}>
            <div className={styles.version}>v0.1.0</div>
            <div className={styles.copyright}>© 2024 Mutao Assistant</div>
          </div>
        </>
      )}
    </aside>
  )
}

export default Sidebar