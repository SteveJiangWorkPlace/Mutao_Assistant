import React, { useState, useEffect, useRef } from 'react'
import { Textarea, Button, Icon, Card, Input, FileUpload } from '@/components'
import type { UploadedFile } from '@/components/ui/FileUpload/FileUpload'
import styles from './Workspace.module.css'

export interface WorkspaceProps {
  isSidebarCollapsed: boolean
  activeTool: 'ps-write' | 'ps-review' | 'rl-write' | 'cv-write'
  apiKey: string
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
  activeTool,
  apiKey
}) => {
  const [text, setText] = useState('')
  const [splitRatio, setSplitRatio] = useState(65) // 65% editor, 35% preview

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
  const [streamingText, setStreamingText] = useState<string>('') // 流式输出当前文本
  const [isStreaming, setIsStreaming] = useState<boolean>(false) // 流式输出状态
  const [streamingStep, setStreamingStep] = useState<'research' | 'statement' | null>(null) // 当前流式步骤

  // 流式输出缓冲优化（参考Python示例）
  const streamingBufferRef = useRef<string>('')
  const streamingBufferTimerRef = useRef<NodeJS.Timeout | null>(null)
  const lastUpdateTimeRef = useRef<number>(0)
  const BUFFER_SIZE = 200 // 字符阈值
  const UPDATE_INTERVAL = 50 // 毫秒

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

  const callGeminiAPI = async (prompt: string) => {
    if (!apiKey) {
      throw new Error('请先在侧边栏输入Google API Key')
    }

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      console.log(`调用后端API: ${apiBaseUrl}/api/gemini/generate`)

      const response = await fetch(`${apiBaseUrl}/api/gemini/ps-write/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          school: schoolInfo.school,
          major: schoolInfo.major,
          courses: courseInfo,
          extracurricular: text,
          api_key: apiKey,
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
  const callGeminiAPIStream = async (
    prompt: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void
  ): Promise<void> => {
    if (!apiKey) {
      throw new Error('请先在侧边栏输入Google API Key')
    }

    try {
      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      console.log(`调用后端流式API: ${apiBaseUrl}/api/gemini/stream`)

      const response = await fetch(`${apiBaseUrl}/api/gemini/ps-write/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          school: schoolInfo.school,
          major: schoolInfo.major,
          courses: courseInfo,
          extracurricular: text,
          api_key: apiKey,
          model_name: 'gemini-2.5-pro',
          temperature: 0.7,
          max_output_tokens: 4000
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`后端流式API调用失败: ${response.status} ${errorText}`)
      }

      // 处理流式响应
      const reader = response.body?.getReader()
      const decoder = new TextDecoder('utf-8')

      if (!reader) {
        throw new Error('无法获取响应流读取器')
      }

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            const trimmedLine = line.trim()
            if (!trimmedLine || trimmedLine === 'data: [DONE]') continue

            if (line.startsWith('data: ')) {
              const data = line.slice(6) // 移除'data: '前缀
              try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                  const cleanedText = cleanMarkdown(parsed.content)
                  onChunk(cleanedText)
                }
              } catch (e) {
                console.warn('解析流式响应数据失败:', e)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }

      console.log('后端流式API调用完成')
      onComplete()

    } catch (error) {
      console.error('调用后端流式API失败:', error)
      throw new Error(`后端流式API调用失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  // 处理流式输出分块
  const handleStreamChunk = (chunk: string) => {
    console.log('收到流式分块:', chunk.length, '字符，内容:', chunk.substring(0, 100))
    setStreamingText(prev => {
      const newText = prev + chunk
      console.log('流式文本累积长度:', newText.length)

      // 如果是调研结果生成阶段，尝试解析JSON
      if (streamingStep === 'research') {
        // 尝试从累积文本中提取JSON
        const jsonMatch = newText.match(/\{[\s\S]*\}/)
        if (jsonMatch) {
          try {
            const parsed = JSON.parse(jsonMatch[0])
            if (parsed.options && Array.isArray(parsed.options)) {
              const optionsWithIds = parsed.options.map((opt: any, index: number) => ({
                ...opt,
                id: `opt_${Date.now()}_${index}`
              }))
              setResearchOptions(optionsWithIds)
            }
          } catch (e) {
            // JSON解析失败，继续累积文本
          }
        }
      }

      return newText
    })
  }


  // 流式输出完成处理
  const handleStreamComplete = () => {
    setIsStreaming(false)
    setStreamingStep(null)

    if (streamingStep === 'research') {
      setWorkflowStep('research')
    } else if (streamingStep === 'statement') {
      setPersonalStatement(streamingText)
      setWorkflowStep('statement')
    }

    setStreamingText('') // 清空流式文本缓存
    saveWorkflowState() // 保存进度
  }

  // 开始流式生成（调研结果）
  const startResearchStream = async () => {
    if (!schoolInfo.major || !text.trim()) {
      alert('请填写申请专业信息和课外经历')
      return
    }

    setIsStreaming(true)
    setStreamingStep('research')
    setStreamingText('')
    setResearchOptions([])

    try {
      // 临时使用原有提示词，阶段三会替换为buildResearchPrompt()
      const prompt = buildPrompt()
      await callGeminiAPIStream(prompt, handleBufferedChunk, handleStreamComplete)
    } catch (error) {
      console.error('流式生成失败:', error)
      setIsStreaming(false)
      setStreamingStep(null)
      alert(`生成失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  // 开始流式生成（个人陈述）
  const startStatementStream = async () => {
    if (!selectedOptionId) {
      alert('请先选择一个研究方向')
      return
    }

    const selectedOption = researchOptions.find(opt => opt.id === selectedOptionId)
    if (!selectedOption) return

    setIsStreaming(true)
    setStreamingStep('statement')
    setStreamingText('')
    setPersonalStatement('')

    try {
      // 临时使用原有提示词，阶段四会替换为buildStatementPrompt()
      const prompt = `基于以下研究方向生成个人陈述：${selectedOption.title}\n\n${text}`
      await callGeminiAPIStream(prompt, handleBufferedChunk, handleStreamComplete)
    } catch (error) {
      console.error('流式生成失败:', error)
      setIsStreaming(false)
      setStreamingStep(null)
      alert(`生成失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  const handleGenerateAnalysis = async () => {
    if (!apiKey) {
      alert('请先在侧边栏输入Google API Key')
      return
    }

    if (!schoolInfo.major || !text.trim()) {
      alert('请填写申请专业信息和课外经历')
      return
    }

    setIsGenerating(true)
    setAnalysisResult('')

    try {
      const prompt = buildPrompt()
      console.log('调用Gemini API，提示词长度:', prompt.length)

      const result = await callGeminiAPI(prompt)
      console.log('Gemini API响应:', result)

      setAnalysisResult(result)
      // 分析结果已保存，预览将自动更新

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
    const state = {
      workflowStep,
      researchOptions,
      selectedOptionId,
      personalStatement,
      schoolInfo,
      courseInfo,
      text,
      streamingText: isStreaming ? streamingText : '', // 仅保存非流式时的文本
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

        // 如果之前有未完成的流式文本，显示恢复提示
        if (state.streamingText) {
          console.log('检测到未完成的生成内容，需要重新生成')
        }
      }
    } catch (error) {
      console.error('加载保存状态失败:', error)
    }
  }

  // 清空保存的状态
  const clearWorkflowState = () => {
    localStorage.removeItem('ps-write-workflow-v2')
    setWorkflowStep('input')
    setResearchOptions([])
    setSelectedOptionId(null)
    setPersonalStatement('')
    setStreamingText('')
    setIsStreaming(false)
    setStreamingStep(null)
  }

  // 组件挂载时加载状态
  useEffect(() => {
    loadWorkflowState()
  }, [])

  // 状态变化时自动保存（流式过程中不保存，避免频繁写入）
  useEffect(() => {
    if (!isStreaming) {
      saveWorkflowState()
    }
  }, [workflowStep, researchOptions, selectedOptionId, personalStatement, schoolInfo, courseInfo, text, isStreaming])

  // 整合所有数据到预览中
  // 格式化调研结果用于预览显示
  const formatResearchOptionsForPreview = (): string => {
    if (researchOptions.length === 0) {
      return '暂无调研结果。'
    }

    return researchOptions
      .sort((a, b) => b.matchScore - a.matchScore)
      .map((opt, index) => {
        return `选项 ${index + 1}：【${opt.title}】
匹配度：${opt.matchScore}%
简要描述：${opt.description}

详细理由：${opt.reasoning}

参考文献：${opt.references}

${'='.repeat(60)}\n`
      })
      .join('\n')
  }

  const generatePreviewText = (): string => {
    if (activeTool !== 'ps-write') {
      return text
    }

    // 流式输出优先显示
    if (isStreaming) {
      return streamingText || '正在生成内容...'
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

  const handleSplitRatioChange = (ratio: number) => {
    setSplitRatio(ratio)
  }

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
              {isStreaming && (
                <span className={styles.streamingBadge}>
                  {streamingStep === 'research' ? '正在生成调研结果...' : '正在生成个人陈述...'}
                </span>
              )}
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
                    onClick={startResearchStream}
                    fullWidth
                    icon={<Icon name="preview" size="sm" />}
                    disabled={isStreaming}
                  >
                    {isStreaming && streamingStep === 'research' ? '流式生成中...' : '开始生成分析'}
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
              <pre className={styles.previewText}>{generatePreviewText()}</pre>
            </div>
          </Card>
        </div>
      </div>
    </main>
  )
}

export default Workspace