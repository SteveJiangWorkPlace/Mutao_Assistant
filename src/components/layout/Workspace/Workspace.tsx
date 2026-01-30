import React, { useState } from 'react'
import { Textarea, Button, Icon, Card } from '@/components'
import styles from './Workspace.module.css'

export interface WorkspaceProps {
  isSidebarCollapsed: boolean
  activeTool: 'ps-write' | 'ps-review' | 'rl-write' | 'cv-write'
}

const Workspace: React.FC<WorkspaceProps> = ({
  isSidebarCollapsed,
  activeTool
}) => {
  const [text, setText] = useState('')
  const [previewText, setPreviewText] = useState('')
  const [splitRatio, setSplitRatio] = useState(50) // 50% editor, 50% preview

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value
    setText(newText)
    setPreviewText(newText) // In a real app, this would process the text
  }

  const handleSplitRatioChange = (ratio: number) => {
    setSplitRatio(ratio)
  }

  const handleSave = () => {
    // In a real app, this would save to backend
    console.log('Saving text:', text)
    alert('保存成功！')
  }

  const handleDownload = () => {
    // In a real app, this would generate a file
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${activeTool}-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const getToolTitle = () => {
    switch (activeTool) {
      case 'ps-write': return 'Personal Statement 写作工具'
      case 'ps-review': return 'Personal Statement 修改工具'
      case 'rl-write': return 'Recommendation Letter 写作工具'
      case 'cv-write': return 'Curriculum Vitae 写作工具'
      default: return '文书写作工具'
    }
  }

  const getToolDescription = () => {
    switch (activeTool) {
      case 'ps-write': return '撰写个人陈述，突出您的学术背景、研究兴趣和职业目标'
      case 'ps-review': return '优化和润色您的个人陈述，提高可读性和说服力'
      case 'rl-write': return '撰写推荐信，展示申请人的能力和成就'
      case 'cv-write': return '创建专业的简历，突出您的教育背景、工作经验和技能'
      default: return '专业的文书写作工具'
    }
  }

  return (
    <main className={`${styles.workspace} ${isSidebarCollapsed ? styles.sidebarCollapsed : ''}`}>
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <h1 className={styles.title}>{getToolTitle()}</h1>
          <p className={styles.description}>{getToolDescription()}</p>
        </div>

        <div className={styles.actions}>
          <Button
            variant="secondary"
            icon={<Icon name="save" size="sm" />}
            onClick={handleSave}
          >
            保存
          </Button>
          <Button
            variant="primary"
            icon={<Icon name="download" size="sm" />}
            onClick={handleDownload}
          >
            下载
          </Button>
        </div>
      </div>

      <div className={styles.splitControls}>
        <button
          className={`${styles.splitButton} ${splitRatio === 100 ? styles.active : ''}`}
          onClick={() => handleSplitRatioChange(100)}
          title="仅编辑器"
        >
          <Icon name="edit" size="sm" />
          <span>编辑器</span>
        </button>
        <button
          className={`${styles.splitButton} ${splitRatio === 50 ? styles.active : ''}`}
          onClick={() => handleSplitRatioChange(50)}
          title="并排视图"
        >
          <Icon name="expand" size="sm" />
          <span>并排</span>
        </button>
        <button
          className={`${styles.splitButton} ${splitRatio === 0 ? styles.active : ''}`}
          onClick={() => handleSplitRatioChange(0)}
          title="仅预览"
        >
          <Icon name="preview" size="sm" />
          <span>预览</span>
        </button>
      </div>

      <div className={styles.content}>
        <div
          className={styles.editorSection}
          style={{
            width: splitRatio === 100 ? '100%' : splitRatio === 0 ? '0%' : `${splitRatio}%`,
            display: splitRatio === 0 ? 'none' : 'flex'
          }}
        >
          <Card variant="elevated" padding="medium" fullWidth>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>
                <Icon name="edit" size="sm" variant="primary" />
                编辑器
              </h2>
              <div className={styles.wordCount}>
                字数: {text.length}
              </div>
            </div>
            <Textarea
              value={text}
              onChange={handleTextChange}
              placeholder="在这里输入您的文书内容..."
              rows={20}
              fullWidth
              resize="vertical"
            />
            <div className={styles.editorTips}>
              <h3>写作提示：</h3>
              <ul>
                <li>保持语言简洁明了</li>
                <li>使用具体的例子来支持您的观点</li>
                <li>检查语法和拼写错误</li>
                <li>确保内容与申请目标相关</li>
              </ul>
            </div>
          </Card>
        </div>

        <div
          className={styles.previewSection}
          style={{
            width: splitRatio === 0 ? '100%' : splitRatio === 100 ? '0%' : `${100 - splitRatio}%`,
            display: splitRatio === 100 ? 'none' : 'flex'
          }}
        >
          <Card variant="elevated" padding="medium" fullWidth>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>
                <Icon name="preview" size="sm" variant="primary" />
                预览
              </h2>
              <div className={styles.formatInfo}>
                格式: 纯文本
              </div>
            </div>
            <div className={styles.previewContent}>
              {previewText ? (
                <pre className={styles.previewText}>{previewText}</pre>
              ) : (
                <div className={styles.emptyPreview}>
                  <Icon name="preview" size="xl" variant="secondary" />
                  <p>输入内容后，这里会显示预览</p>
                </div>
              )}
            </div>
            <div className={styles.previewStats}>
              <div className={styles.stat}>
                <span className={styles.statLabel}>字符数:</span>
                <span className={styles.statValue}>{previewText.length}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>行数:</span>
                <span className={styles.statValue}>{previewText.split('\n').length}</span>
              </div>
              <div className={styles.stat}>
                <span className={styles.statLabel}>段落:</span>
                <span className={styles.statValue}>{previewText.split('\n\n').filter(p => p.trim()).length}</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </main>
  )
}

export default Workspace