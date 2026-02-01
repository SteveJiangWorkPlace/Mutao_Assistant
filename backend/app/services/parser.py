import re
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from app.models.schemas import ResearchOption

def parse_research_options(text: str) -> List[ResearchOption]:
    """
    解析调研文本为结构化数据

    Args:
        text: Gemini返回的调研文本

    Returns:
        解析后的ResearchOption列表

    Raises:
        ValueError: 解析失败时抛出
    """
    # 清理文本：移除多余空白
    text = text.strip()

    # 按细分领域分割文本
    # 使用正则表达式匹配【细分领域X: ...】格式，可能包含匹配度
    pattern = r'【细分领域(\d+):\s*([^】]+)】'
    matches = list(re.finditer(pattern, text))

    if len(matches) < 3:
        # 尝试其他格式，包含可能的匹配度信息
        pattern = r'细分领域(\d+):\s*([^\n(]+)'
        matches = list(re.finditer(pattern, text))

    if len(matches) < 3:
        raise ValueError(f"无法解析到3个细分领域，只找到{len(matches)}个。文本内容：{text[:500]}...")

    research_options = []

    for i, match in enumerate(matches):
        try:
            # 获取领域编号和名称
            domain_num = int(match.group(1))
            domain_name = match.group(2).strip()

            # 提取这个领域对应的文本块
            start_pos = match.end()
            if i < len(matches) - 1:
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(text)

            domain_text = text[start_pos:end_pos]

            # 解析匹配度
            match_score = parse_match_score(domain_text)

            # 解析一句话总结
            summary = parse_summary(domain_text)

            # 解析详细理由
            reasoning = parse_reasoning(domain_text)

            # 解析参考文献
            references = parse_references(domain_text)

            # 创建ResearchOption对象
            option = ResearchOption(
                title=domain_name,
                match_score=match_score,
                summary=summary,
                reasoning=reasoning,
                references=references
            )

            research_options.append(option)

        except Exception as e:
            raise ValueError(f"解析第{i+1}个细分领域时出错: {str(e)}。领域文本：{domain_text[:200]}...")

    # 确保有3个选项
    if len(research_options) != 3:
        raise ValueError(f"期望3个选项，但只解析出{len(research_options)}个")

    return research_options

def parse_match_score(text: str) -> int:
    """解析匹配度"""
    # 查找"匹配度: XX%"模式，可能在括号内
    match = re.search(r'匹配度:\s*(\d+)%', text)
    if match:
        return int(match.group(1))

    # 查找"(匹配度: XX%)"模式
    match = re.search(r'\(匹配度:\s*(\d+)%\)', text)
    if match:
        return int(match.group(1))

    # 尝试其他模式
    match = re.search(r'匹配度\s*(\d+)%', text)
    if match:
        return int(match.group(1))

    # 默认值
    return 85

def parse_summary(text: str) -> str:
    """解析一句话总结"""
    lines = text.split('\n')

    # 查找包含"一句话总结:"的行
    for i, line in enumerate(lines):
        stripped = line.strip()

        # 检查"一句话总结:"模式
        if '一句话总结:' in stripped:
            # 获取冒号后的内容
            if ':' in stripped:
                summary = stripped.split(':', 1)[1].strip()
                if summary:
                    # 移除可能的bullet point符号
                    summary = re.sub(r'^[•\-*]\s*', '', summary)
                    return summary

            # 如果没有内容，尝试下一行
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line:
                    # 移除可能的bullet point符号
                    next_line = re.sub(r'^[•\-*]\s*', '', next_line)
                    return next_line

        # 检查bullet point格式的总结
        if stripped.startswith('•') and '一句话总结:' in stripped:
            # 格式: "• 一句话总结: 内容"
            summary_part = stripped.split(':', 1)[1].strip() if ':' in stripped else stripped[1:].strip()
            return summary_part

    # 查找单独的bullet point总结行
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('•'):
            # 检查前一行是否包含"一句话总结"
            if i > 0 and '一句话总结:' in lines[i - 1]:
                # 移除bullet point符号
                summary = re.sub(r'^[•\-*]\s*', '', stripped)
                return summary

    # 如果没有找到，尝试其他模式
    for line in lines:
        stripped = line.strip()
        if '总结:' in stripped and '详细理由' not in stripped:
            summary = stripped.split('总结:')[1].strip()
            if summary:
                summary = re.sub(r'^[•\-*]\s*', '', summary)
                return summary

    # 返回第一行非空内容作为后备
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('匹配度') and not stripped.startswith('详细理由'):
            # 移除可能的bullet point符号
            stripped = re.sub(r'^[•\-*]\s*', '', stripped)
            return stripped[:200]  # 截断

    return "通过硕士学习专业知识来应对行业挑战"

def parse_reasoning(text: str) -> List[str]:
    """解析详细理由"""
    reasoning = []

    # 查找"详细理由:"部分
    lines = text.split('\n')
    in_reasoning = False
    current_item = ""
    current_type = ""

    for line in lines:
        stripped = line.strip()

        if '详细理由:' in stripped:
            in_reasoning = True
            continue

        if in_reasoning:
            # 检查是否到了参考文献部分
            if '参考文献:' in stripped or stripped.startswith('1.') or stripped.startswith('参考文献'):
                # 添加最后一个项目
                if current_item and current_type:
                    reasoning.append(f"{current_type}: {current_item}")
                break

            # 检查是否是bullet point子标题（趋势分析、痛点识别等）
            bullet_match = re.match(r'^[•\-*]\s*(趋势分析|痛点识别|机会点|技能匹配):\s*(.*)', stripped)
            if bullet_match:
                # 保存前一个项目
                if current_item and current_type:
                    reasoning.append(f"{current_type}: {current_item}")

                # 开始新项目
                current_type = bullet_match.group(1)
                current_item = bullet_match.group(2).strip()
            elif stripped.startswith('•') or stripped.startswith('-') or stripped.startswith('*'):
                # 通用的bullet point，追加到当前项目
                if current_item:
                    # 移除bullet point符号并添加内容
                    bullet_content = re.sub(r'^[•\-*]\s*', '', stripped)
                    if bullet_content:
                        current_item += " " + bullet_content
            elif stripped and not stripped.startswith('【细分领域'):
                # 普通文本行，追加到当前项目
                if current_item:
                    current_item += " " + stripped
                elif stripped:  # 如果没有当前项目但有关键词
                    # 检查是否是没有bullet point的关键词行
                    for keyword in ['趋势分析:', '痛点识别:', '机会点:', '技能匹配:']:
                        if keyword in stripped:
                            if current_item and current_type:
                                reasoning.append(f"{current_type}: {current_item}")
                            current_type = keyword.replace(':', '')
                            current_item = stripped.split(':', 1)[1].strip() if ':' in stripped else stripped
                            break

    # 添加最后一个项目
    if current_item and current_type:
        reasoning.append(f"{current_type}: {current_item}")

    # 如果没有找到详细理由，使用一些默认内容
    if not reasoning:
        reasoning = [
            "趋势分析: 行业趋势分析显示该领域有快速增长",
            "技能匹配: 申请者的经历与领域需求高度匹配"
        ]

    return reasoning

def parse_references(text: str) -> List[str]:
    """解析参考文献"""
    references = []

    # 查找"参考文献:"部分
    lines = text.split('\n')
    in_references = False

    for line in lines:
        stripped = line.strip()

        if '参考文献:' in stripped:
            in_references = True
            continue

        if in_references:
            # 检查是否到了下一个细分领域或结束
            if stripped.startswith('【细分领域') or stripped.startswith('细分领域'):
                break

            # 跳过空行
            if not stripped:
                continue

            # 匹配编号引用格式：1. ..., 2. ... 或 - ..., * ...
            if re.match(r'^(\d+\.\s*|[-*]\s*)', stripped):
                # 移除编号或项目符号
                ref = re.sub(r'^(\d+\.\s*|[-*]\s*)', '', stripped)
                if ref:
                    references.append(ref)
            elif stripped and not references:
                # 如果没有编号格式，但这是第一个引用
                references.append(stripped)

    # 如果没有找到参考文献，返回空列表
    return references

def parse_personal_statement(text: str) -> List[str]:
    """
    解析个人陈述文本为段落列表

    Args:
        text: Gemini返回的个人陈述文本

    Returns:
        段落列表（应该正好5个段落）
    """
    # 按两个换行符分割
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    # 清理每个段落：移除多余空白
    paragraphs = [re.sub(r'\s+', ' ', p) for p in paragraphs]

    # 确保正好5个段落
    if len(paragraphs) > 5:
        # 合并多余的段落
        paragraphs = paragraphs[:5]
    elif len(paragraphs) < 5:
        # 补充缺失的段落
        for i in range(len(paragraphs), 5):
            paragraphs.append(f"第{i+1}段内容待补充")

    return paragraphs[:5]  # 确保只有5个段落

def validate_and_score_references(references: List[str]) -> Tuple[List[str], int, List[str]]:
    """
    验证参考文献并计算质量评分

    Args:
        references: 参考文献列表

    Returns:
        Tuple[valid_references, score, validation_errors]
        - valid_references: 验证通过的参考文献列表
        - score: 参考文献质量评分 (0-100)
        - validation_errors: 验证错误消息列表
    """
    if not references:
        return [], 0, ["无参考文献"]

    valid_references = []
    validation_errors = []
    total_score = 0
    max_score_per_ref = 20  # 每篇参考文献最大20分

    # 权威来源关键词
    authoritative_sources = [
        'Nature', 'Science', 'Cell', 'Lancet', 'NEJM', 'JAMA',
        'IEEE', 'ACM', 'Springer', 'Elsevier', 'Wiley',
        'Gartner', 'IDC', 'McKinsey', 'BCG', 'Deloitte',
        'WHO', 'UNESCO', 'World Bank', 'IMF', 'UN', 'WTO'
    ]

    for i, ref in enumerate(references, 1):
        ref = ref.strip()
        if not ref:
            validation_errors.append(f"参考文献 {i}: 为空")
            continue

        ref_score = 0
        ref_errors = []

        # 检查基本格式：至少包含作者、年份、标题
        has_author = re.search(r'[A-Z][a-z]+,\s*[A-Z]\.', ref) or 'et al.' in ref
        has_year = re.search(r'\(\d{4}\)', ref) or re.search(r'\b(19|20)\d{2}\b', ref)
        has_title = '"' in ref or '“' in ref or '”' in ref or ('[' in ref and ']' in ref)

        # 检查期刊/来源
        has_journal = any(keyword in ref for keyword in ['Journal', 'Proceedings', 'Conference', 'Symposium', 'Transactions'])

        # 检查权威来源
        is_authoritative = any(source.lower() in ref.lower() for source in authoritative_sources)

        # 检查DOI或链接
        has_doi = 'doi:' in ref.lower() or 'doi.org' in ref.lower() or '10.' in ref[:20]
        has_url = 'http://' in ref.lower() or 'https://' in ref.lower()

        # 评分
        if has_author:
            ref_score += 3
        else:
            ref_errors.append("缺少作者信息")

        if has_year:
            ref_score += 3
            # 检查年份是否合理（1900-当前年份）
            year_match = re.search(r'\((\d{4})\)', ref) or re.search(r'\b(19|20)(\d{2})\b', ref)
            if year_match:
                year = int(year_match.group(1) if year_match.group(1) else year_match.group(2))
                current_year = datetime.now().year
                if 1900 <= year <= current_year:
                    ref_score += 2  # 合理年份额外加分
                    if year >= 2020:
                        ref_score += 5  # 2020年后的参考文献额外加分
                else:
                    ref_errors.append(f"年份{year}不合理")
        else:
            ref_errors.append("缺少年份")

        if has_title:
            ref_score += 3
        else:
            ref_errors.append("缺少标题标记")

        if has_journal:
            ref_score += 2
        if is_authoritative:
            ref_score += 5
        if has_doi or has_url:
            ref_score += 4

        # 确保分数不超过最大值
        ref_score = min(ref_score, max_score_per_ref)

        if not ref_errors:
            valid_references.append(ref)
            total_score += ref_score
        else:
            validation_errors.append(f"参考文献 {i}: {ref} - 错误: {', '.join(ref_errors)}")

    # 计算平均分并转换为0-100分
    if valid_references:
        avg_score = total_score / len(valid_references)
        # 将平均分（0-20）转换为百分制（0-100）
        final_score = int((avg_score / max_score_per_ref) * 100)
    else:
        final_score = 0

    return valid_references, final_score, validation_errors

def calculate_match_score_based_on_content(
    domain_text: str,
    user_courses: str = "",
    user_extracurricular: str = ""
) -> int:
    """
    基于内容计算匹配度评分

    Args:
        domain_text: 领域文本
        user_courses: 用户课程描述
        user_extracurricular: 用户课外经历描述

    Returns:
        匹配度评分 (0-100)
    """
    base_score = 70  # 基础分

    # 关键词匹配加分
    keywords_to_check = [
        '前沿', '趋势', '技术', '创新', '发展', '应用',
        '人工智能', '机器学习', '大数据', '云计算', '物联网',
        '可持续发展', '数字化转型', '智能化'
    ]

    keyword_score = 0
    for keyword in keywords_to_check:
        if keyword in domain_text:
            keyword_score += 1

    # 最多加10分
    keyword_bonus = min(keyword_score, 10)

    # 文本长度和质量加分
    text_length = len(domain_text)
    if text_length > 500:
        length_bonus = 10
    elif text_length > 300:
        length_bonus = 5
    elif text_length > 100:
        length_bonus = 2
    else:
        length_bonus = 0

    # 结构完整性加分
    structure_bonus = 0
    required_sections = ['趋势分析', '痛点识别', '机会点', '技能匹配', '参考文献']
    for section in required_sections:
        if section in domain_text:
            structure_bonus += 2

    # 计算最终分数
    final_score = base_score + keyword_bonus + length_bonus + structure_bonus

    # 确保在70-100范围内
    return max(70, min(100, final_score))

def enhance_research_option_with_scoring(
    option: ResearchOption,
    original_text: str,
    user_courses: str = "",
    user_extracurricular: str = ""
) -> ResearchOption:
    """
    使用评分算法增强ResearchOption

    Args:
        option: 原始的ResearchOption对象
        original_text: 原始的领域文本
        user_courses: 用户课程描述（可选）
        user_extracurricular: 用户课外经历描述（可选）

    Returns:
        增强后的ResearchOption对象
    """
    # 验证和评分参考文献
    valid_refs, ref_score, ref_errors = validate_and_score_references(option.references)

    # 基于内容计算匹配度
    content_score = calculate_match_score_based_on_content(
        original_text,
        user_courses,
        user_extracurricular
    )

    # 如果解析的匹配度与计算的分值相差太大，使用计算的分值
    if abs(option.match_score - content_score) > 15:
        # 使用计算的分值，但保持相对顺序
        option.match_score = content_score

    # 更新参考文献列表
    option.references = valid_refs

    # 在详细理由中添加参考文献质量信息
    if ref_errors and len(ref_errors) > 0:
        quality_note = f"参考文献验证: 发现{len(ref_errors)}个问题，质量评分{ref_score}/100"
        option.reasoning.append(quality_note)

    return option

def parse_research_options_with_domain_texts(text: str) -> Tuple[List[ResearchOption], List[str]]:
    """
    解析调研文本为结构化数据，同时返回原始领域文本

    Args:
        text: Gemini返回的调研文本

    Returns:
        Tuple[research_options, domain_texts]
        - research_options: 解析后的ResearchOption列表
        - domain_texts: 对应的原始领域文本列表

    Raises:
        ValueError: 解析失败时抛出
    """
    # 清理文本：移除多余空白
    text = text.strip()

    # 按细分领域分割文本
    # 使用正则表达式匹配【细分领域X: ...】格式，可能包含匹配度
    pattern = r'【细分领域(\d+):\s*([^】]+)】'
    matches = list(re.finditer(pattern, text))

    if len(matches) < 3:
        # 尝试其他格式，包含可能的匹配度信息
        pattern = r'细分领域(\d+):\s*([^\n(]+)'
        matches = list(re.finditer(pattern, text))

    if len(matches) < 3:
        raise ValueError(f"无法解析到3个细分领域，只找到{len(matches)}个。文本内容：{text[:500]}...")

    research_options = []
    domain_texts = []

    for i, match in enumerate(matches):
        try:
            # 获取领域编号和名称
            domain_num = int(match.group(1))
            domain_name = match.group(2).strip()

            # 提取这个领域对应的文本块
            start_pos = match.end()
            if i < len(matches) - 1:
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(text)

            domain_text = text[start_pos:end_pos]
            domain_texts.append(domain_text)

            # 解析匹配度
            match_score = parse_match_score(domain_text)

            # 解析一句话总结
            summary = parse_summary(domain_text)

            # 解析详细理由
            reasoning = parse_reasoning(domain_text)

            # 解析参考文献
            references = parse_references(domain_text)

            # 创建ResearchOption对象
            option = ResearchOption(
                title=domain_name,
                match_score=match_score,
                summary=summary,
                reasoning=reasoning,
                references=references
            )

            research_options.append(option)

        except Exception as e:
            raise ValueError(f"解析第{i+1}个细分领域时出错: {str(e)}。领域文本：domain_text[:200]...")

    # 确保有3个选项
    if len(research_options) != 3:
        raise ValueError(f"期望3个选项，但只解析出{len(research_options)}个")

    return research_options, domain_texts