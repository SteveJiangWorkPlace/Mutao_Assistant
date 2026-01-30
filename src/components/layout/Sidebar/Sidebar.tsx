import React from 'react'
import { Icon } from '@/components'
import styles from './Sidebar.module.css'

export interface SidebarProps {
  isCollapsed: boolean
  activeTool: 'ps-write' | 'ps-review' | 'rl-write' | 'cv-write'
  onToolSelect: (tool: SidebarProps['activeTool']) => void
  onToggle: () => void
}

const Sidebar: React.FC<SidebarProps> = ({
  isCollapsed,
  activeTool,
  onToolSelect,
  onToggle
}) => {
  const menuItems = [
    {
      id: 'ps-write' as const,
      label: 'PS写作',
      icon: 'psWrite' as const,
      description: 'Personal Statement Writing'
    },
    {
      id: 'ps-review' as const,
      label: 'PS修改',
      icon: 'psReview' as const,
      description: 'Personal Statement Review'
    },
    {
      id: 'rl-write' as const,
      label: 'RL写作',
      icon: 'rlWrite' as const,
      description: 'Recommendation Letter Writing'
    },
    {
      id: 'cv-write' as const,
      label: 'CV写作',
      icon: 'cvWrite' as const,
      description: 'Curriculum Vitae Writing'
    }
  ]

  return (
    <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
      <div className={styles.header}>
        {!isCollapsed && (
          <div className={styles.logo}>
            <span className={styles.logoText}>Mutao Assistant</span>
            <span className={styles.logoSubtext}>文书写作工具</span>
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
                  title={isCollapsed ? item.description : item.label}
                >
                  <span className={styles.menuIcon}>
                    <Icon
                      name={item.icon}
                      size="md"
                      variant={isActive ? 'primary' : 'default'}
                    />
                  </span>
                  {!isCollapsed && (
                    <>
                      <span className={styles.menuLabel}>{item.label}</span>
                      <span className={styles.menuDescription}>{item.description}</span>
                    </>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {!isCollapsed && (
        <div className={styles.footer}>
          <div className={styles.version}>v0.1.0</div>
          <div className={styles.copyright}>© 2024 Mutao Assistant</div>
        </div>
      )}
    </aside>
  )
}

export default Sidebar