"""
单章运行协议工作流
实现Step 0-7的完整流程
"""
from typing import Dict, Any, Optional
from agents import (
    RadarAgent, ArchitectAgent, WriterAgent,
    AuditorAgent, ReviserAgent
)
from agents.continuity_guard import ContinuityGuardAgent
from agents.ledger_updater import LedgerUpdaterAgent
from agents.arc_reviewer import ArcReviewerAgent
from utils import get_file_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChapterWorkflow:
    """章节生成工作流"""
    
    def __init__(self):
        self.file_manager = get_file_manager()
        self.radar = RadarAgent()
        self.architect = ArchitectAgent()
        self.writer = WriterAgent()
        self.auditor = AuditorAgent()
        self.reviser = ReviserAgent()
        self.continuity_guard = ContinuityGuardAgent()
        # Ledger Updater需要项目路径用于版本管理
        project_path = self.file_manager.project_root
        self.ledger_updater = LedgerUpdaterAgent(project_path)
        self.arc_reviewer = ArcReviewerAgent()
    
    def run(
        self,
        chapter_num: int,
        chapter_task: Dict[str, Any],
        genre: str = "",
        volume_plan: str = "",
        skip_radar: bool = False,
        chapter_outline: str = "",
        volume_outline: str = "",
        general_outline: str = "",
        require_user_confirm: bool = True,
        volume_num: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行单章生成流程
        
        Args:
            chapter_num: 章节编号
            chapter_task: 章节任务输入卡
            genre: 题材
            volume_plan: 卷目标
            skip_radar: 是否跳过Radar
            chapter_outline: 章节细纲
            volume_outline: 卷纲
            general_outline: 总纲
            require_user_confirm: 是否需要用户确认
            
        Returns:
            生成结果
        """
        logger.info(f"开始生成第{chapter_num}章")
        
        result = {
            "chapter_num": chapter_num,
            "status": "running",
            "outputs": {}
        }
        
        try:
            # Step 0: 准备输入（已在参数中提供）
            logger.info("Step 0: 准备输入完成")
            
            # Step 1: Radar（可跳过）
            radar_output = ""
            if not skip_radar and self.radar.should_run(chapter_num):
                logger.info("Step 1: 执行Radar")
                radar_output = self.radar.execute(
                    chapter_num=chapter_num,
                    genre=genre,
                    volume_plan=volume_plan
                )
                result["outputs"]["radar"] = radar_output
            else:
                logger.info("Step 1: 跳过Radar")
            
            # Step 2: Architect
            logger.info("Step 2: 执行Architect")
            # 读取章节细纲（如果有）
            chapter_outline = kwargs.get("chapter_outline", "")
            architect_output = self.architect.execute(
                chapter_num=chapter_num,
                chapter_task=chapter_task,
                volume_plan=volume_plan,
                radar_suggestions=radar_output,
                chapter_outline=chapter_outline
            )
            result["outputs"]["architect"] = architect_output
            
            # Step 3: Writer
            logger.info("Step 3: 执行Writer")
            writer_output = self.writer.execute(
                chapter_num=chapter_num,
                architect_plan=architect_output,
                genre=genre
            )
            result["outputs"]["writer_draft_v1"] = writer_output
            
            # Step 4: Auditor（初检）
            logger.info("Step 4: 执行Auditor初检")
            audit_v1 = self.auditor.execute(
                chapter_num=chapter_num,
                draft=writer_output,
                genre=genre
            )
            result["outputs"]["audit_v1"] = audit_v1
            
            # Step 5: Reviser
            logger.info("Step 5: 执行Reviser")
            revised_output = self.reviser.execute(
                chapter_num=chapter_num,
                draft=writer_output,
                audit_report=audit_v1
            )
            result["outputs"]["revised_v1"] = revised_output
            
            # Step 6: Auditor复检（循环直到通过）
            max_iterations = 3
            iteration = 0
            final_draft = revised_output
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Step 6: Auditor复检（第{iteration}次）")
                
                audit_v2 = self.auditor.execute(
                    chapter_num=chapter_num,
                    draft=final_draft,
                    genre=genre
                )
                result["outputs"][f"audit_v2_iter{iteration}"] = audit_v2
                
                # 检查是否通过（简单判断：是否有严重问题）
                if self._check_audit_passed(audit_v2):
                    logger.info("审计通过")
                    break
                
                if iteration < max_iterations:
                    logger.info("审计未通过，继续修订")
                    final_draft = self.reviser.execute(
                        chapter_num=chapter_num,
                        draft=final_draft,
                        audit_report=audit_v2
                    )
                    result["outputs"][f"revised_v{iteration+1}"] = final_draft
                else:
                    logger.warning("达到最大迭代次数，使用当前版本")
            
            # Step 7: Continuity Guard（连续性守卫）
            logger.info("Step 7: 执行Continuity Guard检查")
            all_memory = self.file_manager.get_all_memory_files()
            
            continuity_result = self.continuity_guard.execute(
                chapter_num=chapter_num,
                draft=final_draft,
                chapter_outline=chapter_outline,
                volume_outline=volume_outline or "",
                general_outline=general_outline or "",
                all_memory=all_memory
            )
            
            result["outputs"]["continuity_check"] = continuity_result["report"]
            
            if continuity_result.get("has_critical"):
                logger.warning("发现Critical问题，需要修复")
                if require_user_confirm:
                    print("\n" + "=" * 60)
                    print("连续性检查发现Critical问题")
                    print("=" * 60)
                    print(continuity_result["report"])
                    confirm = input("\n是否继续？(y/n): ").strip().lower()
                    if confirm != 'y':
                        result["status"] = "error"
                        result["error"] = "用户取消：存在Critical问题"
                        return result
            
            if not continuity_result["passed"]:
                logger.warning("连续性检查未通过")
                if require_user_confirm:
                    print("\n连续性检查未完全通过，但可以继续。")
            
            # Step 8: Arc Reviewer（弧线审查员）- 每10-20章进行一次
            arc_review_result = None
            revision_plan = None
            if self.arc_reviewer.should_review(chapter_num):
                logger.info(f"Step 8: 执行Arc Reviewer（第{chapter_num}章，触发弧线审查）")
                
                # 读取卷纲和总纲
                volume_outline_content = volume_outline or ""
                general_outline_content = general_outline or ""
                
                arc_review_result = self.arc_reviewer.execute(
                    chapter_num=chapter_num,
                    volume_num=kwargs.get("volume_num", 1),
                    volume_outline=volume_outline_content,
                    general_outline=general_outline_content,
                    all_memory=all_memory
                )
                
                result["outputs"]["arc_review"] = arc_review_result["report"]
                
                if require_user_confirm:
                    print("\n" + "=" * 60)
                    print("弧线审查")
                    print("=" * 60)
                    print("弧线审查报告：")
                    print("-" * 60)
                    print(arc_review_result["report"][:2000] + "..." if len(arc_review_result["report"]) > 2000 else arc_review_result["report"])
                    print("-" * 60)
                    
                    # 如果审查报告包含修订建议，询问用户是否需要生成修订计划
                    if arc_review_result.get("has_revision_suggestions"):
                        print("\n⚠️  审查报告包含修订建议，可能需要调整后续章节规划。")
                        generate_revision = input("\n是否生成修订计划？(y/n，默认n): ").strip().lower()
                        
                        if generate_revision == 'y':
                            print("\n正在生成修订计划...")
                            revision_plan = self.arc_reviewer.generate_revision_plan(
                                arc_review_report=arc_review_result["report"],
                                volume_outline=volume_outline_content,
                                all_memory=all_memory
                            )
                            
                            result["outputs"]["revision_plan"] = revision_plan
                            
                            print("\n修订计划：")
                            print("-" * 60)
                            print(revision_plan[:2000] + "..." if len(revision_plan) > 2000 else revision_plan)
                            print("-" * 60)
                            
                            # 询问用户是否应用修订
                            apply_revision = input("\n是否应用此修订计划？（将更新卷纲）(y/n，默认n): ").strip().lower()
                            
                            if apply_revision == 'y':
                                # 需要用户手动确认应用修订
                                print("\n⚠️  修订计划需要手动应用到卷纲文件。")
                                print("请根据修订计划修改卷纲文件：")
                                volume_num_for_path = kwargs.get("volume_num", 1)
                                outline_filename = f'第{volume_num_for_path}卷-卷纲.md'
                                outline_path = self.file_manager.project_root / 'outlines' / outline_filename
                                print(f"  文件位置: {outline_path}")
                                
                                confirm_applied = input("\n确认已手动应用修订？(y/n): ").strip().lower()
                                if confirm_applied == 'y':
                                    logger.info("用户确认已应用修订计划")
                                    result["outputs"]["revision_applied"] = True
                                else:
                                    logger.info("用户取消应用修订计划")
                                    result["outputs"]["revision_applied"] = False
                            else:
                                print("\n跳过应用修订计划。")
                                result["outputs"]["revision_applied"] = False
                        else:
                            print("\n跳过生成修订计划。")
                    else:
                        print("\n审查报告未发现需要修订的问题。")
                    
                    input("\n按回车继续...")
            
            # Step 9: Ledger Updater（账本更新器）- 支持版本管理和增量更新
            logger.info("Step 9: 执行Ledger Updater")
            
            # 创建版本备份（在更新前）
            if self.ledger_updater.version_manager:
                logger.info("创建ledger版本备份")
                for ledger_name in ["chapter_summaries", "current_state", "pending_hooks", 
                                   "character_matrix", "emotional_arcs", "particle_ledger", "subplot_board"]:
                    old_content = all_memory.get(ledger_name, "")
                    if old_content:
                        self.ledger_updater.create_version_before_update(
                            ledger_name, old_content, chapter_num
                        )
            
            ledger_result = self.ledger_updater.execute(
                chapter_num=chapter_num,
                final_chapter=final_draft,
                all_memory=all_memory
            )
            
            result["outputs"]["ledger_update"] = ledger_result["report"]
            result["outputs"]["ledger_conflicts"] = ledger_result.get("conflicts", {})
            result["outputs"]["ledger_incremental"] = ledger_result.get("incremental_updates", {})
            
            # 更新memory文件（使用改进的合并方法）
            if require_user_confirm:
                print("\n" + "=" * 60)
                print("账本更新")
                print("=" * 60)
                print("账本更新报告：")
                print("-" * 60)
                print(ledger_result["report"][:1000] + "..." if len(ledger_result["report"]) > 1000 else ledger_result["report"])
                print("-" * 60)
                
                # 显示冲突检测结果
                conflicts = ledger_result.get("conflicts", {})
                if conflicts:
                    print("\n⚠️  检测到冲突：")
                    for ledger_name, conflict_list in conflicts.items():
                        print(f"\n  {ledger_name}:")
                        for conflict in conflict_list[:3]:  # 只显示前3个
                            print(f"    - {conflict}")
                    if sum(len(c) for c in conflicts.values()) > 3:
                        print(f"    ... 还有 {sum(len(c) for c in conflicts.values()) - 3} 个冲突")
                    
                    confirm_conflict = input("\n发现冲突，是否仍要继续更新？(y/n): ").strip().lower()
                    if confirm_conflict != 'y':
                        print("跳过账本更新（保留原版本）")
                        return result
                
                # 显示增量更新
                incremental = ledger_result.get("incremental_updates", {})
                if incremental:
                    print("\n📊 增量更新摘要：")
                    for ledger_name, diff in incremental.items():
                        added_count = len(diff.get("added", []))
                        removed_count = len(diff.get("removed", []))
                        modified_count = len(diff.get("modified", []))
                        if added_count or removed_count or modified_count:
                            print(f"  {ledger_name}: +{added_count} -{removed_count} ~{modified_count}")
                
                confirm = input("\n确认更新账本？(y/n): ").strip().lower()
                if confirm == 'y':
                    self._update_ledgers(ledger_result, all_memory)
                else:
                    print("跳过账本更新（保留原版本）")
            else:
                self._update_ledgers(ledger_result, all_memory)
            
            # Step 10: Committer（保存最终章节）
            logger.info("Step 10: 保存最终章节")
            self._commit_chapter(chapter_num, final_draft, chapter_task)
            
            # 保存最终章节
            self.file_manager.save_chapter(chapter_num, final_draft, "final")
            
            result["status"] = "completed"
            result["final_draft"] = final_draft
            logger.info(f"第{chapter_num}章生成完成")
            
        except Exception as e:
            logger.error(f"生成第{chapter_num}章时出错: {str(e)}", exc_info=True)
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def _check_audit_passed(self, audit_report: str) -> bool:
        """检查审计是否通过"""
        # 简单判断：如果没有"严重问题"或"必须修复"，则认为通过
        # TODO: 可以改进为更精确的判断
        if "严重问题" in audit_report or "必须修复" in audit_report:
            # 检查是否所有严重问题都已修复
            lines = audit_report.split('\n')
            in_severe_section = False
            for line in lines:
                if "严重问题" in line or "必须修复" in line:
                    in_severe_section = True
                elif in_severe_section and line.strip().startswith('#'):
                    break
                elif in_severe_section and line.strip() and not line.strip().startswith('-'):
                    # 有未修复的严重问题
                    return False
            return True
        return True
    
    def _commit_chapter(
        self,
        chapter_num: int,
        final_draft: str,
        chapter_task: Dict[str, Any]
    ):
        """提交章节（已由Ledger Updater处理）"""
        logger.info("章节已提交")
    
    def _update_ledgers(self, ledger_result: Dict[str, Any], all_memory: Dict[str, str]):
        """更新ledger文件（使用改进的合并方法、版本管理、增量更新）"""
        logger.info("更新ledger文件")
        
        # 使用LedgerUpdater的合并方法
        ledger_updater = self.ledger_updater
        
        # 获取解析后的内容（优先使用LLM解析的结果）
        parsed = ledger_result.get("parsed", {})
        
        # 更新各个ledger文件
        ledger_types = {
            "chapter_summaries": "chapter_summaries",
            "current_state": "current_state",
            "pending_hooks": "pending_hooks",
            "character_matrix": "character_matrix",
            "emotional_arcs": "emotional_arcs",
            "particle_ledger": "particle_ledger",
            "subplot_board": "subplot_board"
        }
        
        for key, ledger_name in ledger_types.items():
            # 优先使用parsed结果，如果没有则使用原始提取结果
            new_content = parsed.get(key) or ledger_result.get(key, "")
            
            if new_content:
                current = all_memory.get(ledger_name, "")
                updated = ledger_updater._merge_ledger_content(
                    current,
                    new_content,
                    ledger_name
                )
                
                # 写入前创建版本（如果还没有创建）
                if ledger_updater.version_manager:
                    # 检查是否已有版本（在execute中已创建）
                    pass
                
                self.file_manager.write_canon(ledger_name, updated)
                logger.info(f"已更新 {ledger_name}")
        
        # 如果有Open Questions，可以保存到单独文件或添加到pending_hooks
        open_questions = parsed.get("open_questions") or ledger_result.get("open_questions", "")
        if open_questions:
            logger.info("发现Open Questions，建议手动处理")
            # 可以保存到单独文件
            open_questions_file = self.file_manager.memory_dir / "open_questions.md"
            if open_questions_file.exists():
                current_questions = open_questions_file.read_text(encoding="utf-8")
                updated_questions = current_questions + "\n\n" + open_questions
            else:
                updated_questions = f"# Open Questions\n\n{open_questions}"
            open_questions_file.write_text(updated_questions, encoding="utf-8")
