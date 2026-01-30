# Mutao Assistant - 文书写作工具集合

专业的文书写作工具集合，提供PS写作、PS修改、RL写作、CV写作等功能。

## 功能特性

- **PS写作**: 撰写个人陈述，突出学术背景、研究兴趣和职业目标
- **PS修改**: 优化和润色个人陈述，提高可读性和说服力
- **RL写作**: 撰写推荐信，展示申请人的能力和成就
- **CV写作**: 创建专业的简历，突出教育背景、工作经验和技能
- **实时预览**: 编辑器和预览面板并排显示
- **响应式设计**: 适配桌面和移动设备
- **设计系统**: 统一的视觉设计语言

## 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **样式方案**: CSS Modules + CSS Custom Properties
- **状态管理**: Zustand
- **部署平台**: Netlify

## 设计系统

### 颜色主题
- 麻纸米白: `#F1ECE0` (背景色)
- 草木深绿: `#117C0D` (主色调)
- 麦秆暖黄: `#FAC75E` (辅助色)

### 字体系统
- 主要字体: Inter (Google Fonts)
- 字体大小: 12px - 36px 的刻度系统
- 字重: 300-700

### 间距系统
- 基础单位: 4px
- 间距刻度: 0-20 (对应 0-80px)

## 项目结构

```
mutao-assistant/
├── public/                    # 静态资源
├── src/
│   ├── assets/               # 图标、图片、字体
│   ├── components/           # 组件
│   │   ├── layout/          # 布局组件
│   │   ├── ui/              # UI基础组件
│   │   └── features/        # 功能组件
│   ├── styles/              # 样式系统
│   │   ├── design-system/   # 设计系统变量
│   │   ├── mixins/          # CSS Mixins
│   │   └── global.css       # 全局样式
│   ├── hooks/               # 自定义Hooks
│   ├── utils/               # 工具函数
│   ├── types/               # TypeScript类型定义
│   ├── App.tsx              # 主应用组件
│   └── main.tsx             # 应用入口
├── package.json
├── tsconfig.json
├── vite.config.ts
├── netlify.toml             # Netlify部署配置
└── README.md
```

## 开发指南

### 环境要求
- Node.js 18+
- npm 9+

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

### 类型检查
```bash
npm run type-check
```

### 代码检查
```bash
npm run lint
```

### 预览生产构建
```bash
npm run preview
```

## 部署

项目配置了Netlify部署，推送到main分支会自动部署。

### 手动部署到Netlify
1. 连接GitHub仓库到Netlify
2. 构建命令: `npm run build`
3. 发布目录: `dist`
4. 环境变量: 按需配置

## 组件开发规范

### 命名约定
- 组件: PascalCase (如 `Button.tsx`)
- 样式文件: 组件名.module.css (如 `Button.module.css`)
- 工具函数: camelCase (如 `formatText.ts`)

### 样式规范
- 使用CSS Modules避免样式冲突
- 通过设计系统变量统一样式
- 响应式设计使用媒体查询

### TypeScript规范
- 为所有组件和函数定义类型
- 使用接口定义组件Props
- 避免使用any类型

## 扩展计划

1. **后端集成**: 集成FastAPI后端服务
2. **AI辅助**: 集成AI写作建议功能
3. **模板系统**: 提供多种文书模板
4. **导出功能**: 支持PDF、Word、Markdown导出
5. **协作功能**: 多人协作编辑
6. **版本控制**: 文档版本历史
7. **多语言**: 国际化支持

## 许可证

MIT License