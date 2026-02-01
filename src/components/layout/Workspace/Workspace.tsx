import React, { useState, useEffect } from 'react'
import { Textarea, Button, Icon, Card, Input, FileUpload } from '@/components'
import type { UploadedFile } from '@/components/ui/FileUpload/FileUpload'
import styles from './Workspace.module.css'

export interface WorkspaceProps {
  isSidebarCollapsed: boolean
  activeTool: 'ps-write' | 'ps-review' | 'rl-write' | 'cv-write'
}

// PS写作工作流类型定义
interface ResearchOption {
  id: string;
  title: string;       // 研究方向标题（中文）
  description: string; // 简要描述（2-3句话）
  reasoning: string;   // 详细支持理由（包含前沿理论引用）
  references: string;  // 参考文献列表
  matchScore: number;  // 匹配度分数（70-100）
}

interface WorkflowState {
  workflowStep: 'input' | 'research' | 'statement';
  researchOptions: ResearchOption[];
  selectedOptionId: string | null;
  personalStatement: string;
  schoolInfo: { school: string; major: string };
  courseInfo: string;
  text: string;
  timestamp: string;
  version: string;
}

const Workspace: React.FC<WorkspaceProps> = ({
  isSidebarCollapsed,
  activeTool
}) => {
  const [text, setText] = useState('')
  const [splitRatio, setSplitRatio] = useState(65) // 65% editor, 35% preview
  const [isDragging, setIsDragging] = useState(false)

  // PS写作模块专用状态
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [schoolInfo, setSchoolInfo] = useState({ school: '', major: '' })
  const [courseInfo, setCourseInfo] = useState('')
  const [analysisResult, setAnalysisResult] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)

  // PS写作工作流状态（阶段一：基础架构）
  const [workflowStep, setWorkflowStep] = useState<'input' | 'research' | 'statement'>('input')
  const [researchOptions, setResearchOptions] = useState<ResearchOption[]>([])
  const [selectedOptionId, setSelectedOptionId] = useState<string | null>(null)
  const [personalStatement, setPersonalStatement] = useState<string>('')


  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value
    setText(newText)
  }

  // PS写作模块处理函数
  const handleFileUpload = (files: UploadedFile[]) => {
    setUploadedFiles(files)
  }

  const handleSchoolInfoChange = (field: 'school' | 'major', value: string) => {
    setSchoolInfo(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleCourseInfoChange = (value: string) => {
    setCourseInfo(value)
  }

  const buildPrompt = () => {
    const { school, major } = schoolInfo
    const courses = courseInfo
    const extracurricular = text

    return `你是一个留学申请顾问，需要根据申请者的背景信息，分析其课外经历与申请专业的匹配度，并提供专业领域的前沿研究方向和热点分析。

申请者信息：
- 目标学校：${school || '未填写'}
- 申请专业：${major || '未填写'}
- 相关课程信息：${courses || '未填写'}
- 课外经历：${extracurricular || '未填写'}

任务要求：
1. 从课外经历中提取与申请专业最相关的细分领域（申请者可能感兴趣的研究方向）
2. 针对这个细分领域，调研前沿的学术文献、行业报告或最新新闻
3. 分析该领域当前的热点问题、技术挑战或待解决的研究问题
4. 输出3个具体的研究方向，按照与申请者背景的匹配度从高到低排序

输出格式要求（请严格遵守）：
- 只输出纯文本，不要使用任何Markdown符号（如**、*、-、#等）
- 不要包含任何AI执行工作流的提示或解释性语言
- 每个研究方向按以下格式输出：
  [一句话概括主题，使用中文，加粗显示]（注意：实际输出时不要使用**符号，直接加粗文字）
  具体理由：详细说明为什么这个方向与申请者背景匹配，以及该方向的具体内容
  参考文献：列出参考的前沿学术文献、行业报告或新闻来源（使用斜体，但不要用*符号，直接斜体文字）

示例输出格式：
机器学习在医疗影像诊断中的应用
具体理由：申请者在课外经历中参与了医学影像处理项目，掌握了深度学习基础。当前医疗AI领域快速发展，该方向结合了申请者的计算机背景和医疗兴趣。
参考文献：Nature Medicine 2023年关于AI辅助诊断的综述；MIT Technology Review 2024年医疗AI行业报告

注意：实际输出时不要使用**或*等格式符号，直接使用加粗和斜体文字（用户会在富文本环境中查看）。`
  }

  const callGeminiAPI = async () => {
    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      console.log(`调用后端API: ${apiBaseUrl}/api/gemini/ps-write/generate`)

      const response = await fetch(`${apiBaseUrl}/api/gemini/ps-write/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
        },
        body: JSON.stringify({
          school: schoolInfo.school,
          major: schoolInfo.major,
          courses: courseInfo,
          extracurricular: text,
          model_name: 'gemini-2.5-pro',
          temperature: 0.7,
          max_output_tokens: 2000
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`后端API调用失败: ${response.status} ${errorText}`)
      }

      const data = await response.json()
      const result = data.result || '未收到有效回复'

      console.log(`后端API调用成功`)
      return result

    } catch (error) {
      console.error('调用后端API失败:', error)
      throw new Error(`后端API调用失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  // 流式API调用函数（阶段二：流式输出基础框架）- 改为调用后端流式API

  // 处理流式输出分块


  // 流式输出完成处理

  // 开始流式生成（调研结果）


  const handleGenerateAnalysis = async () => {
    if (!schoolInfo.major || !text.trim()) {
      alert('请填写申请专业信息和课外经历')
      return
    }

    setIsGenerating(true)
    setAnalysisResult('')

    try {
      const prompt = buildPrompt()
      console.log('调用Gemini API，提示词长度:', prompt.length)

      const result = await callGeminiAPI()
      console.log('Gemini API响应:', result)

      setAnalysisResult(result)
      // 分析结果已保存，预览将自动更新
      setWorkflowStep('research') // 进入调研结果显示阶段

      // 显示成功提示
      alert('分析生成成功！结果已显示在预览区域。')

    } catch (error) {
      console.error('生成分析失败:', error)
      alert(`生成分析失败: ${error instanceof Error ? error.message : '未知错误'}`)
    } finally {
      setIsGenerating(false)
    }
  }

  // Markdown清理工具函数
  const cleanMarkdown = (text: string): string => {
    // 分步清理所有Markdown符号
    return text
      // 移除粗体和斜体
      .replace(/\*\*(.*?)\*\*/g, '$1')
      .replace(/\*(?!\*)(.*?)\*/g, '$1') // 避免匹配乘号

      // 移除标题
      .replace(/^#{1,6}\s+(.*)$/gm, '$1')

      // 移除列表
      .replace(/^[*-+]\s+(.*)$/gm, '$1')
      .replace(/^\d+\.\s+(.*)$/gm, '$1')

      // 移除代码块和行内代码
      .replace(/`{3}[\s\S]*?`{3}/g, '')
      .replace(/`(.*?)`/g, '$1')

      // 移除引用块
      .replace(/^>\s+(.*)$/gm, '$1')

      // 移除水平线
      .replace(/^[-*_]{3,}$/gm, '')

      // 移除链接和图片（保留文字）
      .replace(/\[(.*?)\]\(.*?\)/g, '$1')
      .replace(/!\[(.*?)\]\(.*?\)/g, '$1')

      // 移除HTML标签（简单处理）
      .replace(/<[^>]*>/g, '')

      // 移除多余的空行
      .replace(/\n\s*\n\s*\n/g, '\n\n')

      // 移除行首尾空格
      .replace(/^\s+|\s+$/gm, '')

      .trim()
  }

  // 临时记忆功能：保存工作流状态到localStorage
  const saveWorkflowState = () => {
    const state: WorkflowState = {
      workflowStep,
      researchOptions,
      selectedOptionId,
      personalStatement,
      schoolInfo,
      courseInfo,
      text,
      timestamp: new Date().toISOString(),
      version: '2.0' // 版本标识
    }

    try {
      localStorage.setItem('ps-write-workflow-v2', JSON.stringify(state))
      console.log('工作流状态已保存')
    } catch (error) {
      console.error('保存状态失败:', error)
    }
  }

  // 加载工作流状态
  const loadWorkflowState = () => {
    try {
      const saved = localStorage.getItem('ps-write-workflow-v2')
      if (!saved) return

      const state = JSON.parse(saved)

      // 仅加载非流式状态（避免恢复流式过程中的状态）
      if (state.version === '2.0') {
        setWorkflowStep(state.workflowStep || 'input')
        setResearchOptions(state.researchOptions || [])
        setSelectedOptionId(state.selectedOptionId || null)
        setPersonalStatement(state.personalStatement || '')
        setSchoolInfo(state.schoolInfo || { school: '', major: '' })
        setCourseInfo(state.courseInfo || '')
        setText(state.text || '')

      }
    } catch (error) {
      console.error('加载保存状态失败:', error)
    }
  }

  // 清空保存的状态
  // @ts-ignore - Function is defined but not used currently
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const clearWorkflowState = () => {
    localStorage.removeItem('ps-write-workflow-v2')
    setWorkflowStep('input')
    setResearchOptions([])
    setSelectedOptionId(null)
    setPersonalStatement('')
  }

  // 组件挂载时加载状态
  useEffect(() => {
    loadWorkflowState()
  }, [])

  // 状态变化时自动保存（流式过程中不保存，避免频繁写入）
  useEffect(() => {
    saveWorkflowState()
  }, [workflowStep, researchOptions, selectedOptionId, personalStatement, schoolInfo, courseInfo, text])

  // 整合所有数据到预览中
  // 格式化调研结果用于预览显示
  const formatResearchOptionsForPreview = (): string => {
    if (researchOptions.length === 0) {
      return '暂无调研结果。'
    }

    return researchOptions
      .sort((a, b) => b.matchScore - a.matchScore)
      .map((opt, index) => {
        // 处理reasoning，可能是字符串或字符串数组
        let reasoningText = opt.reasoning;
        if (Array.isArray(reasoningText)) {
          reasoningText = reasoningText.join('\n');
        }

        // 移除“详细理由：”前缀（如果存在）
        reasoningText = reasoningText.replace(/^详细理由：\s*/, '');

        return `细分领域${index + 1}: ${opt.title}

${reasoningText}

参考文献：
${opt.references}

${'='.repeat(60)}\n`
      })
      .join('\n')
  }

  const generatePreviewText = (): string => {
    if (activeTool !== 'ps-write') {
      return text
    }

    // 如果有分析结果，优先显示
    if (analysisResult && analysisResult.trim()) {
      return cleanMarkdown(analysisResult)
    }

    switch (workflowStep) {
      case 'input':
        return '请填写申请信息并点击"开始生成分析"。'

      case 'research':
        if (researchOptions.length > 0) {
          return formatResearchOptionsForPreview()
        }
        return '请点击"开始生成分析"获取调研结果。'

      case 'statement':
        if (personalStatement) {
          return personalStatement
        }
        return '个人陈述将在此显示。'

      default:
        return '请开始PS写作流程。'
    }
  }

  // 格式化预览文本，对标题和关键部分加粗
  const formatPreviewWithBoldTitles = (text: string): React.ReactNode => {
    if (!text) return text;

    // 使用正则表达式匹配需要加粗的部分：
    // 1. 细分领域标题（带或不带方括号）
    // 2. 小标题：趋势分析、痛点识别、机会点、技能匹配、参考文献
    const boldRegex = /(【细分领域\d+:\s*[^】]+】|细分领域\d+:\s*[^\n(]+|趋势分析:|痛点识别:|机会点:|技能匹配:|参考文献:)/g;

    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = boldRegex.exec(text)) !== null) {
      // 添加匹配前的文本
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index));
      }

      // 添加加粗的部分
      parts.push(
        <span key={match.index} style={{ fontWeight: 'bold' }}>
          {match[0]}
        </span>
      );

      lastIndex = match.index + match[0].length;
    }

    // 添加剩余文本
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex));
    }

    // 如果没有匹配到任何部分，返回原始文本
    if (parts.length === 0) {
      return text;
    }

    return (
      <div className={styles.previewTextFormatted}>
        {parts.map((part, index) => (
          <React.Fragment key={index}>{part}</React.Fragment>
        ))}
      </div>
    );
  };

  const handleSplitRatioChange = (ratio: number) => {
    setSplitRatio(ratio)
  }

  const handleDragStart = (e: React.MouseEvent) => {
    setIsDragging(true)
    e.preventDefault()

    // 防止文本选择，设置拖动光标
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
    document.body.style.webkitUserSelect = 'none'
    document.body.style.msUserSelect = 'none'
  }

  const handleDrag = (e: MouseEvent) => {
    if (!isDragging) return

    const workspaceElement = document.querySelector(`.${styles.content}`) as HTMLElement
    if (!workspaceElement) return

    const rect = workspaceElement.getBoundingClientRect()
    const x = e.clientX - rect.left
    const ratio = Math.min(Math.max((x / rect.width) * 100, 10), 90) // 限制在10%-90%之间

    setSplitRatio(ratio)
  }

  const handleDragEnd = () => {
    setIsDragging(false)

    // 恢复光标和用户选择
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    document.body.style.webkitUserSelect = ''
    document.body.style.msUserSelect = ''
  }

  // 添加全局鼠标事件监听
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleDrag)
      document.addEventListener('mouseup', handleDragEnd)
      return () => {
        document.removeEventListener('mousemove', handleDrag)
        document.removeEventListener('mouseup', handleDragEnd)
      }
    }
  }, [isDragging])

  const handleSave = () => {
    // 保存所有数据
    const dataToSave = {
      text,
      uploadedFiles: uploadedFiles.map(f => ({
        name: f.file.name,
        type: f.file.type,
        size: f.file.size,
        lastModified: f.file.lastModified
      })),
      schoolInfo,
      courseInfo,
      timestamp: new Date().toISOString(),
      tool: activeTool
    }

    console.log('Saving data:', dataToSave)

    // 在实际应用中，这里会保存到后端
    // 现在先保存到localStorage作为演示
    try {
      localStorage.setItem(`mutao-assistant-${activeTool}`, JSON.stringify(dataToSave))
      alert('保存成功！数据已保存到本地存储。')
    } catch (error) {
      console.error('保存失败:', error)
      alert('保存失败：' + (error instanceof Error ? error.message : '未知错误'))
    }
  }

  const handleDownload = () => {
    // 生成包含所有数据的文件
    const content = generatePreviewText()
    const blob = new Blob([content], { type: 'text/plain' })
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

          {/* 简单步骤指示器（阶段二测试用） */}
          {activeTool === 'ps-write' && (
            <div className={styles.workflowIndicator}>
              <span className={`${styles.stepDot} ${workflowStep === 'input' ? styles.active : ''}`}>信息输入</span>
              <span className={styles.stepSeparator}>→</span>
              <span className={`${styles.stepDot} ${workflowStep === 'research' ? styles.active : ''}`}>调研选择</span>
              <span className={styles.stepSeparator}>→</span>
              <span className={`${styles.stepDot} ${workflowStep === 'statement' ? styles.active : ''}`}>个人陈述</span>
            </div>
          )}
        </div>

        <div className={styles.buttonGroups}>
          <div className={styles.actions}>
            <Button
              variant="primary"
              size="small"
              icon={<Icon name="save" size="sm" />}
              onClick={handleSave}
            >
              保存
            </Button>
            <Button
              variant="primary"
              size="small"
              icon={<Icon name="download" size="sm" />}
              onClick={handleDownload}
            >
              下载
            </Button>
          </div>

          <div className={styles.splitControls}>
            <button
              className={`${styles.splitButton} ${splitRatio === 100 ? styles.active : ''}`}
              onClick={() => handleSplitRatioChange(100)}
              title="仅编辑模式"
            >
              <Icon name="edit" size="sm" />
              <span>编辑模式</span>
            </button>
            <button
              className={`${styles.splitButton} ${splitRatio === 65 ? styles.active : ''}`}
              onClick={() => handleSplitRatioChange(65)}
              title="并排视图 (编辑占65%, 预览占35%)"
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
        </div>
      </div>

      <div className={styles.content}>
        <div
          className={styles.editorSection}
          style={{
            width: splitRatio === 100 ? '100%' : splitRatio === 0 ? '0%' : `${splitRatio}%`,
            display: splitRatio === 0 ? 'none' : 'flex'
          }}
        >
          {activeTool === 'ps-write' ? (
            // PS写作专用界面
            <div className={styles.psWriteSection}>
              {/* 模块1: 申请信息 */}
              <div className={styles.module}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <Icon name="school" size="sm" variant="primary" />
                    申请专业信息
                  </h2>
                </div>
                <div className={styles.formFields}>
                  <Input
                    label="学校名称"
                    value={schoolInfo.school}
                    onChange={(e) => handleSchoolInfoChange('school', e.target.value)}
                    placeholder="请输入目标学校名称"
                    fullWidth
                  />
                  <Input
                    label="专业名称"
                    value={schoolInfo.major}
                    onChange={(e) => handleSchoolInfoChange('major', e.target.value)}
                    placeholder="请输入申请专业名称"
                    fullWidth
                  />
                  <Textarea
                    label="相关课程信息"
                    value={courseInfo}
                    onChange={(e) => handleCourseInfoChange(e.target.value)}
                    placeholder="请复制官网课程信息"
                    fullWidth
                    resize="vertical"
                    rows={4}
                  />
                </div>
              </div>

              {/* 模块2: 课外经历 */}
              <div className={styles.module}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <Icon name="edit" size="sm" variant="primary" />
                    输入学生课外经历
                  </h2>
                  <div className={styles.wordCount}>
                    字数: {text.length}
                  </div>
                </div>
                <div className={styles.editorContent}>
                  <Textarea
                    value={text}
                    onChange={handleTextChange}
                    placeholder="请复制粘贴学生课外信息"
                    fullWidth
                    resize="vertical"
                    rows={6}
                  />
                </div>
              </div>

              {/* 模块3: 文件上传 */}
              <div className={styles.module}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>
                    <Icon name="download" size="sm" variant="primary" />
                    上传成绩单
                  </h2>
                </div>
                <FileUpload
                  onFilesChange={handleFileUpload}
                  acceptedTypes="image/*,.pdf"
                  maxSize={10 * 1024 * 1024} // 10MB
                  maxFiles={5}
                />
                <div className={styles.generateButtonContainer}>
                  <Button
                    variant="primary"
                    size="medium"
                    onClick={handleGenerateAnalysis}
                    fullWidth
                    icon={<Icon name="preview" size="sm" />}
                    disabled={isGenerating}
                  >
                    {isGenerating ? '生成中...' : '开始生成分析'}
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            // 原有编辑器界面（其他工具使用）
            <Card variant="elevated" padding="medium" fullWidth>
              <div className={styles.sectionHeader}>
                <h2 className={styles.sectionTitle}>
                  <Icon name="edit" size="sm" variant="primary" />
                  编辑模式
                </h2>
                <div className={styles.wordCount}>
                  字数: {text.length}
                </div>
              </div>
              <div className={styles.editorContent}>
                <Textarea
                  value={text}
                  onChange={handleTextChange}
                  placeholder="在这里输入您的文书内容..."
                  fullWidth
                  resize="vertical"
                />
              </div>
            </Card>
          )}
        </div>

        {/* 可拖动的分隔条 */}
        {splitRatio !== 0 && splitRatio !== 100 && (
          <div
            className={styles.dividerBar}
            onMouseDown={handleDragStart}
            style={{ cursor: isDragging ? 'col-resize' : 'col-resize' }}
          />
        )}

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
            </div>
            <div className={styles.previewContent}>
              <div className={styles.previewTextContainer}>
                {isGenerating ? (
                  <div className={styles.loadingDots}>
                    <div className={styles.dot}></div>
                    <div className={styles.dot}></div>
                    <div className={styles.dot}></div>
                    <div className={styles.dot}></div>
                  </div>
                ) : (
                  formatPreviewWithBoldTitles(generatePreviewText())
                )}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </main>
  )
}

export default Workspace