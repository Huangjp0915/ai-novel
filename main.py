"""
主程序入口
支持多小说项目管理
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from utils import get_client, get_file_manager
from utils.project_manager import get_project_manager
from utils.project_initializer import ProjectInitializer
from utils.outline_manager import OutlineManager
from utils.setting_checker import SettingChecker
from workflow import ChapterWorkflow
from agents.outline_generator import (
    GeneralOutlineAgent,
    VolumeOutlineAgent,
    ChapterOutlineAgent
)
from agents.outline_checker import (
    GeneralOutlineChecker,
    VolumeOutlineChecker,
    ChapterOutlineChecker
)
from agents.continuity_guard import ContinuityGuardAgent
from agents.ledger_updater import LedgerUpdaterAgent
import logging

# 加载环境变量
load_dotenv()

# 配置日志（初始配置，项目路径确定后会更新）
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 控制台处理器
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def setup_project_logging(project_path: Path):
    """为项目设置日志"""
    log_file = project_path / "logs" / "ai_novel.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

# 全局变量：当前项目ID
_current_project_id: str = None


def check_environment():
    """检查环境配置"""
    logger.info("检查环境配置...")
    
    # 检查Ollama连接
    client = get_client()
    if not client.check_connection():
        logger.error("无法连接到Ollama，请确保Ollama已启动")
        logger.info("启动命令: ollama serve")
        return False
    
    logger.info(f"Ollama连接成功，使用模型: {client.model}")
    
    # 检查模型是否存在
    models = client.list_models()
    if client.model not in models:
        logger.error(f"模型 {client.model} 不存在")
        logger.info(f"可用模型: {', '.join(models)}")
        logger.info(f"下载命令: ollama pull {client.model}")
        return False
    
    logger.info(f"模型 {client.model} 可用")
    return True


def select_or_create_project():
    """
    选择或创建项目
    
    Returns:
        (project_id, project_path) 或 None
    """
    project_manager = get_project_manager()
    projects = project_manager.list_projects()
    
    print("\n" + "=" * 60)
    print("项目管理")
    print("=" * 60)
    
    if not projects:
        # 没有项目，创建新项目
        print("\n当前没有小说项目。")
        return create_new_project(project_manager)
    else:
        # 有项目，询问用户
        print(f"\n找到 {len(projects)} 个已有项目：")
        print("\n已有项目列表：")
        for i, project in enumerate(projects, 1):
            genre_info = f" [{project['genre']}]" if project.get('genre') else ""
            print(f"  {i}. {project['name']}{genre_info}")
            if project.get('last_modified'):
                print(f"     最后修改: {project['last_modified'][:10]}")
        
        print("\n请选择：")
        print("  1. 使用已有项目")
        print("  2. 创建新项目")
        print("  0. 退出")
        
        choice = input("\n请输入选项 (0-2): ").strip()
        
        if choice == "0":
            return None
        elif choice == "1":
            return select_existing_project(project_manager, projects)
        elif choice == "2":
            return create_new_project(project_manager)
        else:
            print("无效选项，请重试")
            return select_or_create_project()


def select_existing_project(project_manager, projects):
    """选择已有项目"""
    print("\n" + "=" * 60)
    print("选择项目")
    print("=" * 60)
    
    for i, project in enumerate(projects, 1):
        genre_info = f" [{project['genre']}]" if project.get('genre') else ""
        print(f"  {i}. {project['name']}{genre_info}")
        if project.get('last_modified'):
            print(f"     最后修改: {project['last_modified'][:10]}")
    
    while True:
        try:
            choice = input(f"\n请选择项目 (1-{len(projects)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(projects):
                project = projects[index]
                project_path = project_manager.get_project_path(project['id'])
                print(f"\n已选择项目: {project['name']}")
                return project['id'], project_path
            else:
                print(f"请输入 1-{len(projects)} 之间的数字")
        except ValueError:
            print("请输入有效的数字")
        except KeyboardInterrupt:
            return None


def create_new_project(project_manager):
    """创建新项目"""
    print("\n" + "=" * 60)
    print("创建新项目")
    print("=" * 60)
    
    print("\n请输入项目信息：")
    
    while True:
        project_name = input("项目名称（小说名称）: ").strip()
        if project_name:
            break
        print("项目名称不能为空，请重新输入")
    
    print("\n可选题材：")
    genres = ["玄幻", "都市", "都市异能", "仙侠", "科幻", "其他"]
    for i, genre in enumerate(genres, 1):
        print(f"  {i}. {genre}")
    
    genre_choice = input("\n请选择题材 (1-6，直接回车跳过): ").strip()
    genre = ""
    if genre_choice:
        try:
            genre_index = int(genre_choice) - 1
            if 0 <= genre_index < len(genres):
                genre = genres[genre_index]
        except ValueError:
            pass
    
    description = input("项目描述（可选，直接回车跳过）: ").strip()
    
    # 创建项目
    print("\n正在创建项目...")
    project_id = project_manager.create_project(
        project_name=project_name,
        genre=genre,
        description=description
    )
    
    project_path = project_manager.get_project_path(project_id)
    
    # 初始化项目
    print("正在初始化项目文件...")
    initializer = ProjectInitializer(project_path)
    initializer.initialize()
    
    print(f"\n✓ 项目创建成功！")
    print(f"  项目名称: {project_name}")
    print(f"  项目路径: {project_path}")
    print(f"\n请填写 memory/ 目录下的文件，特别是：")
    print(f"  - 世界观.md")
    print(f"  - 主角卡.md")
    print(f"  - 力量体系.md")
    print(f"  - 金手指设计.md")
    print(f"\n文件位置: {project_path / 'memory'}")
    
    return project_id, project_path


def initialize_project(project_path: Path):
    """初始化项目环境"""
    global _current_project_id
    
    # 设置文件管理器使用项目路径
    file_manager = get_file_manager()
    file_manager.set_project_path(project_path)
    
    # 确保所有memory文件存在
    file_manager.init_canon_files()
    
    logger.info(f"项目路径: {project_path}")


def create_chapter_task_template():
    """创建章节任务输入卡模板"""
    return {
        "书名": "",
        "章节编号": 0,
        "当前卷": "",
        "目标字数": 3000,
        "本章功能": "推进主线",
        "必须发生的事件": [],
        "不能发生的事": [],
        "本章重点角色": [],
        "建议情绪基调": "",
        "上章结尾钩子": "",
        "本章结束后期待留下的状态": []
    }


def get_project_info(project_path: Path):
    """获取项目信息"""
    import json
    info_file = project_path / "config" / "project_info.json"
    if info_file.exists():
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}


def main():
    """主函数"""
    print("=" * 60)
    print("AI小说连载系统")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        print("\n环境检查失败，请修复后重试")
        return
    
    print("\n环境检查通过！")
    
    # 选择或创建项目
    result = select_or_create_project()
    if result is None:
        print("\n已退出")
        return
    
    project_id, project_path = result
    
    # 初始化项目
    initialize_project(project_path)
    
    # 设置项目日志
    setup_project_logging(project_path)
    
    # 获取项目信息
    project_info = get_project_info(project_path)
    project_name = project_info.get("name", project_path.name)
    genre = project_info.get("genre", "")
    
    print("\n" + "=" * 60)
    print(f"当前项目: {project_name}")
    if genre:
        print(f"题材: {genre}")
    print("=" * 60)
    
    # 检查设定文件
    file_manager = get_file_manager()
    setting_checker = SettingChecker(file_manager)
    all_filled, check_result = setting_checker.check_all_settings()
    
    setting_checker.display_check_result(check_result)
    
    if not all_filled:
        print("\n⚠️  必须填写的文件尚未完成，请先填写这些文件。")
        print("\n请选择：")
        print("  1. 继续（我将稍后提醒）")
        print("  2. 退出，稍后填写")
        
        choice = input("\n请输入选项 (1-2): ").strip()
        if choice == "2":
            print("\n已退出，请填写memory文件后重新运行。")
            return
    
    # 确认设定
    print("\n" + "=" * 60)
    print("设定确认")
    print("=" * 60)
    print("\n请确认所有设定文件是否已正确填写。")
    print("如需修改，请编辑 memory/ 目录下的文件。")
    
    confirm = input("\n所有设定已确认无误？(y/n): ").strip().lower()
    if confirm != 'y':
        print("\n请修改设定文件后重新运行。")
        return
    
    # 生成总纲流程
    outline_manager = OutlineManager(project_path)
    
    if not outline_manager.general_outline_exists():
        print("\n" + "=" * 60)
        print("生成总纲")
        print("=" * 60)
        
        # 询问目标总字数
        print("\n请输入小说目标总字数：")
        print("  示例：1000000（100万字）、500000（50万字）、2000000（200万字）")
        
        while True:
            word_count_input = input("\n目标总字数（默认：1000000，即100万字）: ").strip()
            try:
                if word_count_input:
                    target_word_count = int(word_count_input)
                else:
                    target_word_count = 1000000
                
                if target_word_count < 100000:
                    print("⚠️  总字数过少，建议至少10万字")
                    confirm = input("是否仍使用此字数？(y/n): ").strip().lower()
                    if confirm == 'y':
                        break
                else:
                    break
            except ValueError:
                print("请输入有效的数字")
        
        print(f"\n目标总字数：{target_word_count:,}字（约{target_word_count/10000:.1f}万字）")
        print(f"假设每章3000字，预计约{target_word_count//3000}章")
        
        print("\n正在根据所有设定生成总纲...")
        
        all_memory = file_manager.get_all_memory_files()
        general_outline_agent = GeneralOutlineAgent()
        general_outline = general_outline_agent.execute(
            project_name=project_name,
            genre=genre or "玄幻",
            all_memory=all_memory,
            target_word_count=target_word_count
        )
        
        outline_manager.save_general_outline(general_outline, target_word_count)
        print("\n✓ 总纲已生成！")
        print(f"  保存位置: {project_path / 'outlines' / '总纲.md'}")
        
        # 显示总纲预览
        print("\n总纲预览（前500字）：")
        print("-" * 60)
        print(general_outline[:500] + "..." if len(general_outline) > 500 else general_outline)
        print("-" * 60)
        
        # 总纲检查
        print("\n" + "=" * 60)
        print("总纲检查")
        print("=" * 60)
        print("\n正在检查总纲是否满足设定集要求...")
        
        general_outline_checker = GeneralOutlineChecker()
        check_result = general_outline_checker.execute(
            general_outline=general_outline,
            all_memory=all_memory
        )
        
        print("\n检查报告：")
        print("-" * 60)
        print(check_result["report"])
        print("-" * 60)
        
        if not check_result["passed"]:
            print("\n⚠️  总纲检查未通过，发现以下问题：")
            print("请修改总纲文件后重新运行。")
            print(f"总纲文件: {project_path / 'outlines' / '总纲.md'}")
            
            confirm = input("\n是否仍要继续？(y/n): ").strip().lower()
            if confirm != 'y':
                return
        else:
            print("\n✓ 总纲检查通过！")
        
        confirm = input("\n总纲是否满意？(y/n): ").strip().lower()
        if confirm != 'y':
            print("\n请修改总纲文件后重新运行。")
            print(f"总纲文件: {project_path / 'outlines' / '总纲.md'}")
            return
    else:
        print("\n✓ 总纲已存在，跳过生成。")
    
    # 检查已有卷纲
    print("\n" + "=" * 60)
    print("卷纲管理")
    print("=" * 60)
    
    # 查找所有已存在的卷纲
    existing_volumes = []
    for vol_num in range(1, 20):  # 最多检查20卷
        if outline_manager.volume_outline_exists(vol_num):
            existing_volumes.append(vol_num)
    
    if existing_volumes:
        print(f"\n找到 {len(existing_volumes)} 个已有卷纲：")
        for vol_num in existing_volumes:
            print(f"  - 第{vol_num}卷")
        
        print("\n请选择：")
        print("  1. 使用已有卷纲（继续操作）")
        print("  2. 生成新卷纲")
        
        choice = input("\n请输入选项 (1-2): ").strip()
        
        if choice == "1":
            # 使用已有卷纲
            print("\n请选择要使用的卷号：")
            for i, vol_num in enumerate(existing_volumes, 1):
                print(f"  {i}. 第{vol_num}卷")
            
            vol_choice = input(f"\n请输入选项 (1-{len(existing_volumes)}): ").strip()
            try:
                vol_index = int(vol_choice) - 1
                if 0 <= vol_index < len(existing_volumes):
                    volume_num = existing_volumes[vol_index]
                else:
                    volume_num = existing_volumes[0]
            except ValueError:
                volume_num = existing_volumes[0]
            
            print(f"\n✓ 已选择第{volume_num}卷")
        else:
            # 生成新卷纲
            volume_num_input = input("\n请输入要生成的卷号: ").strip()
            try:
                volume_num = int(volume_num_input) if volume_num_input else 1
            except ValueError:
                volume_num = 1
            
            volume_name = input(f"第{volume_num}卷名称 (可选): ").strip() or f"第{volume_num}卷"
            
            print(f"\n正在生成第{volume_num}卷卷纲...")
            
            general_outline = outline_manager.read_general_outline()
            all_memory = file_manager.get_all_memory_files()
            
            volume_outline_agent = VolumeOutlineAgent()
            volume_outline = volume_outline_agent.execute(
                project_name=project_name,
                volume_num=volume_num,
                volume_name=volume_name,
                general_outline=general_outline,
                all_memory=all_memory
            )
            
            outline_manager.save_volume_outline(volume_num, volume_outline)
            print(f"\n✓ 第{volume_num}卷卷纲已生成！")
            print(f"  保存位置: {project_path / 'outlines' / f'第{volume_num}卷-卷纲.md'}")
            
            # 显示卷纲预览
            print("\n卷纲预览（前500字）：")
            print("-" * 60)
            print(volume_outline[:500] + "..." if len(volume_outline) > 500 else volume_outline)
            print("-" * 60)
            
            # 卷纲检查
            print("\n" + "=" * 60)
            print("卷纲检查")
            print("=" * 60)
            print("\n正在检查卷纲是否满足总纲要求和设定集...")
            
            volume_outline_checker = VolumeOutlineChecker()
            check_result = volume_outline_checker.execute(
                volume_num=volume_num,
                volume_outline=volume_outline,
                general_outline=general_outline,
                all_memory=all_memory
            )
            
            print("\n检查报告：")
            print("-" * 60)
            print(check_result["report"])
            print("-" * 60)
            
            # 特别检查章节数
            if check_result.get("general_chapters") and check_result.get("volume_chapters"):
                if abs(check_result["general_chapters"] - check_result["volume_chapters"]) > 5:
                    print(f"\n⚠️  章节数不匹配警告：")
                    print(f"  总纲要求约 {check_result['general_chapters']} 章")
                    print(f"  卷纲只有 {check_result['volume_chapters']} 章")
                    print("  请检查并修改卷纲。")
            
            if not check_result["passed"]:
                print("\n⚠️  卷纲检查未通过，发现以下问题：")
                print("请修改卷纲文件后重新运行。")
                print(f"卷纲文件: {project_path / 'outlines' / f'第{volume_num}卷-卷纲.md'}")
                
                confirm = input("\n是否仍要继续？(y/n): ").strip().lower()
                if confirm != 'y':
                    return
            else:
                print("\n✓ 卷纲检查通过！")
            
            confirm = input("\n卷纲是否满意？(y/n): ").strip().lower()
            if confirm != 'y':
                print("\n请修改卷纲文件后重新运行。")
                print(f"卷纲文件: {project_path / 'outlines' / f'第{volume_num}卷-卷纲.md'}")
                return
    else:
        # 没有卷纲，询问生成
        volume_num_input = input("\n没有找到已有卷纲，请输入要生成的卷号 (默认: 1): ").strip()
        try:
            volume_num = int(volume_num_input) if volume_num_input else 1
        except ValueError:
            volume_num = 1
        
        volume_name = input(f"第{volume_num}卷名称 (可选): ").strip() or f"第{volume_num}卷"
        
        print(f"\n正在生成第{volume_num}卷卷纲...")
        
        general_outline = outline_manager.read_general_outline()
        all_memory = file_manager.get_all_memory_files()
        
        volume_outline_agent = VolumeOutlineAgent()
        volume_outline = volume_outline_agent.execute(
            project_name=project_name,
            volume_num=volume_num,
            volume_name=volume_name,
            general_outline=general_outline,
            all_memory=all_memory
        )
        
        outline_manager.save_volume_outline(volume_num, volume_outline)
        print(f"\n✓ 第{volume_num}卷卷纲已生成！")
        print(f"  保存位置: {project_path / 'outlines' / f'第{volume_num}卷-卷纲.md'}")
        
        # 显示卷纲预览
        print("\n卷纲预览（前500字）：")
        print("-" * 60)
        print(volume_outline[:500] + "..." if len(volume_outline) > 500 else volume_outline)
        print("-" * 60)
        
        # 卷纲检查
        print("\n" + "=" * 60)
        print("卷纲检查")
        print("=" * 60)
        print("\n正在检查卷纲是否满足总纲要求和设定集...")
        
        volume_outline_checker = VolumeOutlineChecker()
        check_result = volume_outline_checker.execute(
            volume_num=volume_num,
            volume_outline=volume_outline,
            general_outline=general_outline,
            all_memory=all_memory
        )
        
        print("\n检查报告：")
        print("-" * 60)
        print(check_result["report"])
        print("-" * 60)
        
        # 特别检查章节数
        if check_result.get("general_chapters") and check_result.get("volume_chapters"):
            if abs(check_result["general_chapters"] - check_result["volume_chapters"]) > 5:
                print(f"\n⚠️  章节数不匹配警告：")
                print(f"  总纲要求约 {check_result['general_chapters']} 章")
                print(f"  卷纲只有 {check_result['volume_chapters']} 章")
                print("  请检查并修改卷纲。")
        
        if not check_result["passed"]:
            print("\n⚠️  卷纲检查未通过，发现以下问题：")
            print("请修改卷纲文件后重新运行。")
            print(f"卷纲文件: {project_path / 'outlines' / f'第{volume_num}卷-卷纲.md'}")
            
            confirm = input("\n是否仍要继续？(y/n): ").strip().lower()
            if confirm != 'y':
                return
        else:
            print("\n✓ 卷纲检查通过！")
        
        confirm = input("\n卷纲是否满意？(y/n): ").strip().lower()
        if confirm != 'y':
            print("\n请修改卷纲文件后重新运行。")
            print(f"卷纲文件: {project_path / 'outlines' / f'第{volume_num}卷-卷纲.md'}")
            return
    
    # 保存volume_num到全局，供后续使用
    global _current_volume_num, _current_chapter_num
    _current_volume_num = volume_num
    _current_chapter_num = None
    
    # 检查已有细纲
    print("\n" + "=" * 60)
    print("细纲管理")
    print("=" * 60)
    
    # 查找所有已存在的细纲
    existing_chapters = []
    for ch_num in range(1, 200):  # 最多检查200章
        if outline_manager.read_chapter_outline(volume_num, ch_num):
            existing_chapters.append(ch_num)
    
    generate_outline = 'n'  # 默认不生成新细纲
    chapter_num = 1  # 默认章节编号
    
    if existing_chapters:
        print(f"\n找到 {len(existing_chapters)} 个已有细纲：")
        if len(existing_chapters) <= 20:
            for ch_num in existing_chapters:
                print(f"  - 第{ch_num}章")
        else:
            print(f"  - 第{existing_chapters[0]}章 到 第{existing_chapters[-1]}章（共{len(existing_chapters)}章）")
        
        print("\n请选择：")
        print("  1. 使用已有细纲（继续生成正文）")
        print("  2. 生成新细纲（单个）")
        print("  3. 批量生成细纲")
        
        choice = input("\n请输入选项 (1-3): ").strip()
        
        if choice == "1":
            # 使用已有细纲
            print("\n请选择要使用的章节：")
            if len(existing_chapters) <= 20:
                for i, ch_num in enumerate(existing_chapters, 1):
                    print(f"  {i}. 第{ch_num}章")
                ch_choice = input(f"\n请输入选项 (1-{len(existing_chapters)}): ").strip()
                try:
                    ch_index = int(ch_choice) - 1
                    if 0 <= ch_index < len(existing_chapters):
                        chapter_num = existing_chapters[ch_index]
                    else:
                        chapter_num = existing_chapters[0]
                except ValueError:
                    chapter_num = existing_chapters[0]
            else:
                ch_input = input(f"\n请输入章节编号 (范围: {existing_chapters[0]}-{existing_chapters[-1]}): ").strip()
                try:
                    chapter_num = int(ch_input)
                    if chapter_num not in existing_chapters:
                        print(f"⚠️  第{chapter_num}章细纲不存在，使用第{existing_chapters[0]}章")
                        chapter_num = existing_chapters[0]
                except ValueError:
                    chapter_num = existing_chapters[0]
            
            print(f"\n✓ 已选择第{chapter_num}章")
            generate_outline = 'n'  # 不生成新细纲
        elif choice == "2":
            # 生成单个细纲
            chapter_num_input = input("\n请输入要生成的章节编号: ").strip()
            try:
                chapter_num = int(chapter_num_input) if chapter_num_input else 1
            except ValueError:
                chapter_num = 1
            generate_outline = 'y'
        else:
            # 批量生成细纲
            print("\n批量生成细纲")
            print("-" * 60)
            start_input = input("起始章节编号: ").strip()
            end_input = input("结束章节编号: ").strip()
            
            try:
                start_ch = int(start_input) if start_input else 1
                end_ch = int(end_input) if end_input else start_ch
            except ValueError:
                print("输入无效，取消批量生成")
                return
            
            if start_ch > end_ch:
                start_ch, end_ch = end_ch, start_ch
            
            print(f"\n将生成第{start_ch}章到第{end_ch}章的细纲（共{end_ch - start_ch + 1}章）")
            confirm = input("确认批量生成？(y/n): ").strip().lower()
            if confirm != 'y':
                return
            
            general_outline = outline_manager.read_general_outline()
            volume_outline = outline_manager.read_volume_outline(volume_num)
            all_memory = file_manager.get_all_memory_files()
            chapter_outline_agent = ChapterOutlineAgent()
            chapter_outline_checker = ChapterOutlineChecker()
            
            for ch_num in range(start_ch, end_ch + 1):
                if outline_manager.read_chapter_outline(volume_num, ch_num):
                    print(f"\n第{ch_num}章细纲已存在，跳过")
                    continue
                
                print(f"\n正在生成第{ch_num}章细纲...")
                
                chapter_outline = chapter_outline_agent.execute(
                    project_name=project_name,
                    volume_num=volume_num,
                    chapter_num=ch_num,
                    volume_outline=volume_outline,
                    all_memory=all_memory
                )
                
                outline_manager.save_chapter_outline(volume_num, ch_num, chapter_outline)
                print(f"✓ 第{ch_num}章细纲已生成")
                
                # 细纲检查
                check_result = chapter_outline_checker.execute(
                    chapter_num=ch_num,
                    chapter_outline=chapter_outline,
                    volume_outline=volume_outline,
                    general_outline=general_outline,
                    all_memory=all_memory
                )
                
                if not check_result["passed"]:
                    print(f"⚠️  第{ch_num}章细纲检查未完全通过")
            
            print(f"\n✓ 批量生成完成！共生成 {end_ch - start_ch + 1} 章细纲")
            chapter_num = start_ch  # 默认从第一章开始
            generate_outline = 'n'
    else:
        # 没有细纲，询问生成
        print("\n没有找到已有细纲")
        print("\n请选择：")
        print("  1. 生成单个细纲")
        print("  2. 批量生成细纲")
        
        choice = input("\n请输入选项 (1-2): ").strip()
        
        if choice == "2":
            # 批量生成
            print("\n批量生成细纲")
            print("-" * 60)
            start_input = input("起始章节编号 (默认: 1): ").strip()
            end_input = input("结束章节编号: ").strip()
            
            try:
                start_ch = int(start_input) if start_input else 1
                end_ch = int(end_input) if end_input else start_ch
            except ValueError:
                print("输入无效，取消批量生成")
                return
            
            if start_ch > end_ch:
                start_ch, end_ch = end_ch, start_ch
            
            print(f"\n将生成第{start_ch}章到第{end_ch}章的细纲（共{end_ch - start_ch + 1}章）")
            confirm = input("确认批量生成？(y/n): ").strip().lower()
            if confirm != 'y':
                return
            
            general_outline = outline_manager.read_general_outline()
            volume_outline = outline_manager.read_volume_outline(volume_num)
            all_memory = file_manager.get_all_memory_files()
            chapter_outline_agent = ChapterOutlineAgent()
            chapter_outline_checker = ChapterOutlineChecker()
            
            for ch_num in range(start_ch, end_ch + 1):
                print(f"\n正在生成第{ch_num}章细纲...")
                
                chapter_outline = chapter_outline_agent.execute(
                    project_name=project_name,
                    volume_num=volume_num,
                    chapter_num=ch_num,
                    volume_outline=volume_outline,
                    all_memory=all_memory
                )
                
                outline_manager.save_chapter_outline(volume_num, ch_num, chapter_outline)
                print(f"✓ 第{ch_num}章细纲已生成")
                
                # 细纲检查
                check_result = chapter_outline_checker.execute(
                    chapter_num=ch_num,
                    chapter_outline=chapter_outline,
                    volume_outline=volume_outline,
                    general_outline=general_outline,
                    all_memory=all_memory
                )
                
                if not check_result["passed"]:
                    print(f"⚠️  第{ch_num}章细纲检查未完全通过")
            
            print(f"\n✓ 批量生成完成！共生成 {end_ch - start_ch + 1} 章细纲")
            chapter_num = start_ch
            generate_outline = 'n'
        else:
            # 生成单个细纲
            chapter_num_input = input("\n请输入要生成的章节编号 (默认: 1): ").strip()
            try:
                chapter_num = int(chapter_num_input) if chapter_num_input else 1
            except ValueError:
                chapter_num = 1
            generate_outline = 'y'
    
    # 生成单个细纲（如果需要）
    if generate_outline == 'y':
        if not outline_manager.read_chapter_outline(volume_num, chapter_num):
            print(f"\n正在生成第{volume_num}卷第{chapter_num}章细纲...")
            
            general_outline = outline_manager.read_general_outline()
            volume_outline = outline_manager.read_volume_outline(volume_num)
            all_memory = file_manager.get_all_memory_files()
            
            chapter_outline_agent = ChapterOutlineAgent()
            chapter_outline = chapter_outline_agent.execute(
                project_name=project_name,
                volume_num=volume_num,
                chapter_num=chapter_num,
                volume_outline=volume_outline,
                all_memory=all_memory
            )
            
            outline_manager.save_chapter_outline(volume_num, chapter_num, chapter_outline)
            print(f"\n✓ 第{volume_num}卷第{chapter_num}章细纲已生成！")
            print(f"  保存位置: {project_path / 'outlines' / f'第{volume_num}卷' / f'第{chapter_num}章-细纲.md'}")
            
            # 显示细纲预览
            print("\n细纲预览（前500字）：")
            print("-" * 60)
            print(chapter_outline[:500] + "..." if len(chapter_outline) > 500 else chapter_outline)
            print("-" * 60)
            
            # 细纲检查
            print("\n" + "=" * 60)
            print("细纲检查")
            print("=" * 60)
            print("\n正在检查细纲是否满足总纲、卷纲和设定集...")
            
            chapter_outline_checker = ChapterOutlineChecker()
            check_result = chapter_outline_checker.execute(
                chapter_num=chapter_num,
                chapter_outline=chapter_outline,
                volume_outline=volume_outline,
                general_outline=general_outline,
                all_memory=all_memory
            )
            
            print("\n检查报告：")
            print("-" * 60)
            print(check_result["report"])
            print("-" * 60)
            
            if not check_result["passed"]:
                print("\n⚠️  细纲检查未通过，发现以下问题：")
                print("请修改细纲文件后重新运行。")
                print(f"细纲文件: {project_path / 'outlines' / f'第{volume_num}卷' / f'第{chapter_num}章-细纲.md'}")
                
                confirm = input("\n是否仍要继续？(y/n): ").strip().lower()
                if confirm != 'y':
                    return
            else:
                print("\n✓ 细纲检查通过！")
            
            confirm = input("\n细纲是否满意？(y/n): ").strip().lower()
            if confirm != 'y':
                print("\n请修改细纲文件后重新运行。")
                print(f"细纲文件: {project_path / 'outlines' / f'第{volume_num}卷' / f'第{chapter_num}章-细纲.md'}")
                return
        else:
            print(f"\n✓ 第{chapter_num}章细纲已存在，跳过生成。")
    
    # 现在可以开始生成正文
    print("\n" + "=" * 60)
    print("准备生成正文")
    print("=" * 60)
    
    # 确定章节编号（如果之前没有生成细纲，需要输入）
    if generate_outline != 'y' or not outline_manager.read_chapter_outline(volume_num, chapter_num):
        chapter_num_input = input("\n请输入要生成的章节编号 (默认: 1): ").strip()
        try:
            chapter_num = int(chapter_num_input) if chapter_num_input else 1
        except ValueError:
            chapter_num = 1
    
    # 读取细纲（必须存在）
    chapter_outline = outline_manager.read_chapter_outline(volume_num, chapter_num)
    
    if not chapter_outline:
        print(f"\n❌ 错误：第{volume_num}卷第{chapter_num}章的细纲不存在！")
        print("请先生成细纲后再生成正文。")
        return
    
    print(f"\n✓ 找到第{volume_num}卷第{chapter_num}章的细纲")
    print(f"  细纲长度：{len(chapter_outline)}字符")
    
    # 读取总纲和卷纲
    general_outline = outline_manager.read_general_outline()
    volume_outline_content = outline_manager.read_volume_outline(volume_num)
    
    if not general_outline:
        print("\n❌ 错误：总纲不存在！")
        return
    
    if not volume_outline_content:
        print(f"\n❌ 错误：第{volume_num}卷卷纲不存在！")
        return
    
    print(f"✓ 总纲已加载：{len(general_outline)}字符")
    print(f"✓ 卷纲已加载：{len(volume_outline_content)}字符")
    
    # 自动生成chapter_task（从细纲中提取信息，使用默认值）
    print("\n正在准备章节任务信息...")
    
    chapter_task = {
        "书名": project_name,
        "章节编号": chapter_num,
        "当前卷": f"第{volume_num}卷",
        "目标字数": 3000,  # 默认3000字
        "本章功能": "推进主线",  # 默认值，细纲中会包含更详细的信息
        "必须发生的事件": [],  # 细纲中会包含事件信息
        "不能发生的事": [],
        "本章重点角色": [],  # 可以从细纲中提取
        "建议情绪基调": "",
        "上章结尾钩子": "",
        "本章结束后期待留下的状态": []
    }
    
    print(f"\n章节信息：")
    print(f"  章节编号：第{chapter_num}章")
    print(f"  当前卷：第{volume_num}卷")
    print(f"  目标字数：{chapter_task['目标字数']}字")
    print(f"  数据来源：细纲 + 总纲 + 卷纲 + 设定集")
    
    # 确认开始生成
    print("\n" + "=" * 60)
    confirm = input("确认开始生成章节？(y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    print("\n开始生成章节...\n")
    
    # 创建工作流
    workflow = ChapterWorkflow()
    
    result = workflow.run(
        chapter_num=chapter_task["章节编号"],
        chapter_task=chapter_task,
        genre=genre or "玄幻",
        volume_plan="",
        skip_radar=False,
        chapter_outline=chapter_outline,  # 传递细纲
        volume_outline=volume_outline_content,  # 传递卷纲
        general_outline=general_outline,  # 传递总纲
        require_user_confirm=True,  # 需要用户确认
        volume_num=volume_num  # 传递卷号
    )
    
    # 更新项目修改时间
    project_manager = get_project_manager()
    project_manager.update_project_modified(project_id)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("生成结果")
    print("=" * 60)
    print(f"状态: {result['status']}")
    
    if result['status'] == 'completed':
        chapter_num = chapter_task["章节编号"]
        chapter_filename = f'chapter_{chapter_num:03d}.md'
        chapter_path = project_path / 'chapters' / chapter_filename
        print(f"\n章节已保存到: {chapter_path}")
        print(f"最终字数: {len(result.get('final_draft', ''))}字")
    elif result['status'] == 'error':
        print(f"\n错误: {result.get('error', '未知错误')}")
    
    print("\n完成！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        logger.error(f"程序异常: {str(e)}", exc_info=True)
        print(f"\n程序异常: {str(e)}")
