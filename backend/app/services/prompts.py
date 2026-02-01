"""
提示词模板管理
包含PS写作模块使用的所有提示词模板
"""
from typing import List

# 增强版调研提示词
ENHANCED_RESEARCH_PROMPT = """
你是一个留学申请顾问，需要分析申请者的背景信息，提供专业领域的前沿研究方向和深度行业调研。

申请者信息：
- 目标学校：{school}
- 申请专业：{major}
- 相关课程：{courses}
- 课外经历：{extracurricular}

任务要求：
1. 从课外经历中提取最相关的细分领域（申请者可能感兴趣的研究方向）
2. 找出3个最匹配的细分领域，按匹配度从高到低排序
3. 对每个领域进行深度行业调研，包括：
   - 行业趋势分析（2020年后的最新趋势）
   - 前沿理论引用（具体理论名称、提出者、核心观点）
   - 技术发展趋势
   - 市场痛点识别
   - 技能匹配度分析
4. 详细理由部分必须包含：
   - 至少2个真实的前沿理论或技术趋势引用
   - 具体的行业数据或案例支持
   - 与申请者经历的直接关联分析
5. 参考文献要求真实、权威、前沿：
   - 优先引用：Nature, Science, IEEE, ACM等顶级期刊2020年后的论文
   - 行业报告：Gartner, IDC, McKinsey等权威机构报告
   - 学术会议：最新学术会议论文
   - 专业网站：WHO（世界卫生组织）、UNESCO（联合国教科文组织）、World Bank（世界银行）、IMF（国际货币基金组织）等国际组织官方网站

输出格式（严格遵循，不使用任何Markdown符号）：
【细分领域1: [领域名称]】 (匹配度: [XX]%)

一句话总结:
• [我通过硕士学习什么知识来应对什么行业趋势/痛点]

详细理由:
• 趋势分析: [具体趋势描述，包含前沿理论引用]
• 痛点识别: [具体痛点分析，包含真实案例]
• 机会点: [具体机会说明，包含技术发展趋势]
• 技能匹配: [与申请者经历的相关性分析]

参考文献:
1. [作者] ([年份]). "[标题]", [期刊/机构], DOI/链接
2. [作者] ([年份]). "[标题]", [期刊/机构], DOI/链接

【细分领域2: ...】
（同样格式）

注意：只输出纯文本，不要使用Markdown符号。确保所有参考文献真实存在。
"""

# 个人陈述提示词
PERSONAL_STATEMENT_PROMPT = """
你是一个专业的留学文书顾问，需要基于用户选择的细分领域生成完整的个人陈述。

申请者信息：
- 目标学校：{school}
- 申请专业：{major}
- 相关课程：{courses}
- 课外经历：{extracurricular}
- 选择的细分领域：{selected_domain}

个人陈述要求（严格按照以下5段结构，每段为自然的中文段落，不使用任何列表符号、Markdown格式或分段标题）：

第一段：申请动机
开头一句话精准概括想通过硕士学位探索的细分领域或想解决的行业痛点，展开较为具体的叙述和理由（为什么对这个领域感兴趣），联系期待通过所申请的专业掌握什么技能来应对这样的挑战。

第二段：学习经历
基于提供的课程信息，识别与申请专业最相关的课程，阐述这些课程的教授内容，包括关键概念和方法学，强调课程之间的联系（如XX是XX的基础，或课程间有交集关联），富有逻辑性，避免平铺直叙。

第三段：课外经历
开头与学习经历进行自然衔接，将最相关的课外经历（用户输入的）结合起来。每个经历的撰写逻辑：背景是什么，我负责了什么工作，承担什么职责，我的感悟和体会（课堂外学到的技能、认识到的行业痛点、想解决的问题）。经历之间要有递进关系（时间递进或行业感悟由浅到深），结尾精简总结强调就读硕士想学习的知识技能。

第四段：选校理由
说明目标学校的课程在硕士级别教授的关键概念或方法学，阐述这些课程对申请者有什么帮助，把描述组合成自然的中文段落，强调课程之间的联系，融入前面提到的想法和动机，语气朴素专业，避免夸张。

第五段：职业规划
毕业后的职业规划（毕业硕士应届生可达成的），想去的公司类型，想做的职位，想探索的工作内容，与硕士学习内容的关联性。

请直接输出5个段落，段落之间用两个换行符分隔。不要添加任何解释、说明、标题或格式符号。
"""

def format_enhanced_research_prompt(school: str, major: str, courses: str, extracurricular: str) -> str:
    """
    格式化增强版调研提示词

    Args:
        school: 目标学校
        major: 申请专业
        courses: 相关课程描述
        extracurricular: 课外经历描述

    Returns:
        格式化后的提示词
    """
    return ENHANCED_RESEARCH_PROMPT.format(
        school=school,
        major=major,
        courses=courses,
        extracurricular=extracurricular
    )

def format_personal_statement_prompt(
    school: str,
    major: str,
    courses: str,
    extracurricular: str,
    selected_domain: str
) -> str:
    """
    格式化个人陈述提示词

    Args:
        school: 目标学校
        major: 申请专业
        courses: 相关课程描述
        extracurricular: 课外经历描述
        selected_domain: 选择的细分领域

    Returns:
        格式化后的提示词
    """
    return PERSONAL_STATEMENT_PROMPT.format(
        school=school,
        major=major,
        courses=courses,
        extracurricular=extracurricular,
        selected_domain=selected_domain
    )

def validate_enhanced_research_prompt(prompt: str) -> List[str]:
    """
    验证增强版调研提示词格式

    Args:
        prompt: 格式化后的提示词

    Returns:
        错误消息列表，空列表表示通过验证
    """
    errors = []

    # 检查必要的占位符
    required_placeholders = ['{school}', '{major}', '{courses}', '{extracurricular}']
    for placeholder in required_placeholders:
        if placeholder not in prompt:
            errors.append(f"提示词缺少必要占位符: {placeholder}")

    # 检查关键要求部分
    required_sections = [
        '任务要求',
        '输出格式',
        '细分领域1',
        '参考文献'
    ]

    for section in required_sections:
        if section not in prompt:
            errors.append(f"提示词缺少必要部分: {section}")

    return errors

def validate_personal_statement_prompt(prompt: str) -> List[str]:
    """
    验证个人陈述提示词格式

    Args:
        prompt: 格式化后的提示词

    Returns:
        错误消息列表，空列表表示通过验证
    """
    errors = []

    # 检查必要的占位符
    required_placeholders = ['{school}', '{major}', '{courses}', '{extracurricular}', '{selected_domain}']
    for placeholder in required_placeholders:
        if placeholder not in prompt:
            errors.append(f"提示词缺少必要占位符: {placeholder}")

    # 检查段落结构要求
    required_sections = [
        '第一段：申请动机',
        '第二段：学习经历',
        '第三段：课外经历',
        '第四段：选校理由',
        '第五段：职业规划'
    ]

    for section in required_sections:
        if section not in prompt:
            errors.append(f"提示词缺少必要段落说明: {section}")

    return errors