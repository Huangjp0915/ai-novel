"""
AI小说连载系统 - Web界面
基于Flask的Web应用
"""
import os
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# 导入项目模块
from utils.project_manager import ProjectManager
from utils.file_manager import FileManager
from utils.outline_manager import OutlineManager
from workflow import ChapterWorkflow
from agents.outline_generator import GeneralOutlineAgent, VolumeOutlineAgent, ChapterOutlineAgent
from agents.outline_checker import GeneralOutlineChecker, VolumeOutlineChecker, ChapterOutlineChecker

app = Flask(__name__)
CORS(app)

# 配置
app.config['SECRET_KEY'] = 'ai-novel-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 全局变量
current_project_path = None
project_manager = ProjectManager()
file_manager_instance = None
outline_manager_instance = None


def get_file_manager_instance():
    """获取当前项目的FileManager"""
    global file_manager_instance, current_project_path
    if current_project_path:
        if file_manager_instance and file_manager_instance.project_root != current_project_path:
            file_manager_instance.set_project_path(current_project_path)
        elif not file_manager_instance:
            file_manager_instance = FileManager()
            file_manager_instance.set_project_path(current_project_path)
        return file_manager_instance
    return None


def get_outline_manager_instance():
    """获取当前项目的OutlineManager"""
    global outline_manager_instance, current_project_path
    if current_project_path:
        if outline_manager_instance and outline_manager_instance.project_path != current_project_path:
            outline_manager_instance = OutlineManager(current_project_path)
        elif not outline_manager_instance:
            outline_manager_instance = OutlineManager(current_project_path)
        return outline_manager_instance
    return None


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')


@app.route('/api/projects', methods=['GET'])
def list_projects():
    """获取项目列表"""
    try:
        projects = project_manager.list_projects()
        # 转换项目数据格式
        projects_list = []
        for proj in projects:
            projects_list.append({
                'id': proj.get('id', ''),
                'name': proj.get('name', ''),
                'genre': proj.get('genre', ''),
                'created_at': proj.get('created_at', ''),
                'last_modified': proj.get('last_modified', ''),
                'path': str(proj.get('path', ''))
            })
        return jsonify({
            'success': True,
            'projects': projects_list
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/projects', methods=['POST'])
def create_project():
    """创建新项目"""
    try:
        data = request.json
        project_name = data.get('name', '')
        genre = data.get('genre', '玄幻')
        
        if not project_name:
            return jsonify({
                'success': False,
                'error': '项目名称不能为空'
            }), 400
        
        project_id = project_manager.create_project(project_name, genre)
        project_path = project_manager.get_project_path(project_id)
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'project_path': str(project_path)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/projects/<project_id>/select', methods=['POST'])
def select_project(project_id):
    """选择项目"""
    try:
        global current_project_path
        
        # URL解码项目ID（处理中文项目名）
        import urllib.parse
        project_id = urllib.parse.unquote(project_id)
        
        project_path = project_manager.get_project_path(project_id)
        
        if not project_path or not project_path.exists():
            return jsonify({
                'success': False,
                'error': '项目不存在'
            }), 404
        
        current_project_path = project_path
        
        # 获取项目信息
        project_info = project_manager.get_project_info(project_id)
        if not project_info:
            project_info = {
                'name': project_id,
                'genre': '未知',
                'created_at': '',
                'last_modified': ''
            }
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'project_path': str(project_path),
            'project_info': project_info
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/projects/current', methods=['GET'])
def get_current_project():
    """获取当前项目信息"""
    try:
        global current_project_path
        if not current_project_path:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        # 查找项目ID
        projects = project_manager.list_projects()
        project_id = None
        for proj in projects:
            if Path(proj['path']) == current_project_path:
                project_id = proj['id']
                break
        
        if not project_id:
            return jsonify({
                'success': False,
                'error': '项目信息未找到'
            }), 404
        
        project_info = project_manager.get_project_info(project_id)
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'project_path': str(current_project_path),
            'project_info': project_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/memory/files', methods=['GET'])
def list_memory_files():
    """获取memory文件列表"""
    try:
        fm = get_file_manager_instance()
        if not fm:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        memory_files = [
            "current_state",
            "particle_ledger",
            "pending_hooks",
            "chapter_summaries",
            "subplot_board",
            "emotional_arcs",
            "character_matrix",
            "爽点规划",
            "世界观",
            "主角卡",
            "主角组",
            "力量体系",
            "反派设计",
            "复合题材-融合逻辑",
            "女主卡",
            "金手指设计"
        ]
        
        files_info = []
        for name in memory_files:
            try:
                content = fm.read_canon(name)
                files_info.append({
                    'name': name,
                    'exists': bool(content),
                    'size': len(content),
                    'preview': content[:200] if content else ''
                })
            except Exception as e:
                files_info.append({
                    'name': name,
                    'exists': False,
                    'size': 0,
                    'preview': '',
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'files': files_info
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/memory/files/<filename>', methods=['GET'])
def get_memory_file(filename):
    """获取memory文件内容"""
    try:
        fm = get_file_manager_instance()
        if not fm:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        # 移除.md扩展名（如果有）
        filename = filename.replace('.md', '')
        content = fm.read_canon(filename)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content': content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/memory/files/<filename>', methods=['POST'])
def save_memory_file(filename):
    """保存memory文件"""
    try:
        fm = get_file_manager_instance()
        if not fm:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        data = request.json
        content = data.get('content', '')
        
        # 移除.md扩展名（如果有）
        filename = filename.replace('.md', '')
        fm.write_canon(filename, content)
        
        return jsonify({
            'success': True,
            'message': '文件已保存'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/outlines/general', methods=['GET'])
def get_general_outline():
    """获取总纲"""
    try:
        om = get_outline_manager_instance()
        if not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        outline = om.read_general_outline()
        exists = om.general_outline_exists()
        
        return jsonify({
            'success': True,
            'exists': exists,
            'content': outline
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/outlines/general', methods=['POST'])
def generate_general_outline():
    """生成总纲"""
    try:
        fm = get_file_manager_instance()
        om = get_outline_manager_instance()
        if not fm or not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        data = request.json
        target_word_count = data.get('target_word_count', 1000000)
        project_name = data.get('project_name', '')
        genre = data.get('genre', '玄幻')
        
        all_memory = fm.get_all_memory_files()
        agent = GeneralOutlineAgent()
        outline = agent.execute(
            project_name=project_name,
            genre=genre,
            all_memory=all_memory,
            target_word_count=target_word_count
        )
        
        om.save_general_outline(outline, target_word_count)
        
        return jsonify({
            'success': True,
            'content': outline
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/outlines/general/save', methods=['POST'])
def save_general_outline():
    """保存总纲"""
    try:
        om = get_outline_manager_instance()
        if not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({
                'success': False,
                'error': '内容不能为空'
            }), 400
        
        # 读取现有总纲以获取目标字数
        existing = om.read_general_outline()
        target_word_count = 0
        if existing:
            # 尝试从现有内容中提取目标字数
            import re
            match = re.search(r'目标总字数[：:]\s*(\d+)', existing)
            if match:
                target_word_count = int(match.group(1))
        
        om.save_general_outline(content, target_word_count)
        
        return jsonify({
            'success': True,
            'message': '总纲已保存'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/outlines/volumes', methods=['GET'])
def list_volumes():
    """获取卷列表"""
    try:
        om = get_outline_manager_instance()
        if not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        volumes = []
        for vol_num in range(1, 20):
            if om.volume_outline_exists(vol_num):
                content = om.read_volume_outline(vol_num)
                volumes.append({
                    'volume_num': vol_num,
                    'exists': True,
                    'size': len(content),
                    'preview': content[:200] if content else ''
                })
        
        return jsonify({
            'success': True,
            'volumes': volumes
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/outlines/volumes', methods=['POST'])
def generate_volume_outline():
    """生成卷纲"""
    try:
        fm = get_file_manager_instance()
        om = get_outline_manager_instance()
        if not fm or not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        data = request.json
        volume_num = data.get('volume_num', 1)
        
        # 读取总纲
        general_outline = om.read_general_outline()
        if not general_outline:
            return jsonify({
                'success': False,
                'error': '请先生成总纲'
            }), 400
        
        all_memory = fm.get_all_memory_files()
        agent = VolumeOutlineAgent()
        outline = agent.execute(
            volume_num=volume_num,
            general_outline=general_outline,
            all_memory=all_memory
        )
        
        om.save_volume_outline(volume_num, outline)
        
        return jsonify({
            'success': True,
            'content': outline
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/outlines/volumes/<int:volume_num>', methods=['GET'])
def get_volume_outline(volume_num):
    """获取卷纲"""
    try:
        om = get_outline_manager_instance()
        if not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        outline = om.read_volume_outline(volume_num)
        exists = om.volume_outline_exists(volume_num)
        
        return jsonify({
            'success': True,
            'exists': exists,
            'content': outline
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/outlines/volumes/<int:volume_num>/save', methods=['POST'])
def save_volume_outline(volume_num):
    """保存卷纲"""
    try:
        om = get_outline_manager_instance()
        if not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({
                'success': False,
                'error': '内容不能为空'
            }), 400
        
        om.save_volume_outline(volume_num, content)
        
        return jsonify({
            'success': True,
            'message': f'第{volume_num}卷卷纲已保存'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/outlines/chapters/<int:volume_num>', methods=['GET'])
def list_chapters(volume_num):
    """获取章节列表"""
    try:
        om = get_outline_manager_instance()
        if not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        chapters = []
        for ch_num in range(1, 200):
            outline = om.read_chapter_outline(volume_num, ch_num)
            if outline:
                chapters.append({
                    'chapter_num': ch_num,
                    'exists': True,
                    'size': len(outline),
                    'preview': outline[:200] if outline else ''
                })
        
        return jsonify({
            'success': True,
            'chapters': chapters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/outlines/chapters/<int:volume_num>/<int:chapter_num>', methods=['GET'])
def get_chapter_outline(volume_num, chapter_num):
    """获取章节细纲"""
    try:
        om = get_outline_manager_instance()
        if not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        outline = om.read_chapter_outline(volume_num, chapter_num)
        exists = bool(outline)
        
        return jsonify({
            'success': True,
            'exists': exists,
            'content': outline
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/outlines/chapters/<int:volume_num>/<int:chapter_num>/save', methods=['POST'])
def save_chapter_outline(volume_num, chapter_num):
    """保存章节细纲"""
    try:
        om = get_outline_manager_instance()
        if not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        data = request.json
        content = data.get('content', '')
        
        if not content:
            return jsonify({
                'success': False,
                'error': '内容不能为空'
            }), 400
        
        om.save_chapter_outline(volume_num, chapter_num, content)
        
        return jsonify({
            'success': True,
            'message': f'第{volume_num}卷第{chapter_num}章细纲已保存'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/outlines/chapters/<int:volume_num>/<int:chapter_num>', methods=['POST'])
def generate_chapter_outline(volume_num, chapter_num):
    """生成章节细纲"""
    try:
        fm = get_file_manager_instance()
        om = get_outline_manager_instance()
        if not fm or not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        # 读取总纲和卷纲
        general_outline = om.read_general_outline()
        volume_outline = om.read_volume_outline(volume_num)
        
        if not general_outline:
            return jsonify({
                'success': False,
                'error': '请先生成总纲'
            }), 400
        
        if not volume_outline:
            return jsonify({
                'success': False,
                'error': f'请先生成第{volume_num}卷卷纲'
            }), 400
        
        all_memory = fm.get_all_memory_files()
        agent = ChapterOutlineAgent()
        outline = agent.execute(
            volume_num=volume_num,
            chapter_num=chapter_num,
            general_outline=general_outline,
            volume_outline=volume_outline,
            all_memory=all_memory
        )
        
        om.save_chapter_outline(volume_num, chapter_num, outline)
        
        return jsonify({
            'success': True,
            'content': outline
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/chapters/generate', methods=['POST'])
def generate_chapter():
    """生成章节"""
    try:
        fm = get_file_manager_instance()
        om = get_outline_manager_instance()
        if not fm or not om:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        data = request.json
        volume_num = data.get('volume_num', 1)
        chapter_num = data.get('chapter_num', 1)
        
        # 读取细纲、卷纲、总纲
        chapter_outline = om.read_chapter_outline(volume_num, chapter_num)
        volume_outline = om.read_volume_outline(volume_num)
        general_outline = om.read_general_outline()
        
        if not chapter_outline:
            return jsonify({
                'success': False,
                'error': f'第{volume_num}卷第{chapter_num}章细纲不存在'
            }), 404
        
        # 创建chapter_task
        project_info = project_manager.get_project_info(data.get('project_id', ''))
        project_name = project_info.get('name', '') if project_info else ''
        
        chapter_task = {
            "书名": project_name,
            "章节编号": chapter_num,
            "当前卷": f"第{volume_num}卷",
            "目标字数": 3000,
            "本章功能": "推进主线",
            "必须发生的事件": [],
            "不能发生的事": [],
            "本章重点角色": [],
            "建议情绪基调": "",
            "上章结尾钩子": "",
            "本章结束后期待留下的状态": []
        }
        
        # 执行工作流
        workflow = ChapterWorkflow()
        result = workflow.run(
            chapter_num=chapter_num,
            chapter_task=chapter_task,
            genre=data.get('genre', '玄幻'),
            volume_plan="",
            skip_radar=True,  # Web界面默认跳过Radar
            chapter_outline=chapter_outline,
            volume_outline=volume_outline,
            general_outline=general_outline,
            require_user_confirm=False,  # Web界面不需要交互确认
            volume_num=volume_num
        )
        
        return jsonify({
            'success': result.get('status') == 'completed',
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/chapters/<int:chapter_num>', methods=['GET'])
def get_chapter_content(chapter_num):
    """获取章节内容"""
    try:
        fm = get_file_manager_instance()
        if not fm:
            return jsonify({
                'success': False,
                'error': '未选择项目'
            }), 404
        
        chapter_file = fm.chapters_dir / f"chapter_{chapter_num:03d}.md"
        if chapter_file.exists():
            content = chapter_file.read_text(encoding='utf-8')
            return jsonify({
                'success': True,
                'content': content
            })
        else:
            return jsonify({
                'success': False,
                'error': '章节文件不存在'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config/ai', methods=['GET'])
def get_ai_config():
    """获取AI配置"""
    try:
        from utils.ai_config import get_ai_config_manager
        config_manager = get_ai_config_manager()
        
        return jsonify({
            'success': True,
            'current_platform': config_manager.get_current_platform(),
            'platforms': config_manager.get_all_platforms()
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/config/ai', methods=['POST'])
def update_ai_config():
    """更新AI配置"""
    try:
        from utils.ai_config import get_ai_config_manager
        config_manager = get_ai_config_manager()
        
        data = request.json
        current_platform = data.get('current_platform')
        platform_configs = data.get('platforms', {})
        
        if current_platform:
            config_manager.set_current_platform(current_platform)
        
        for platform, config in platform_configs.items():
            config_manager.update_platform_config(platform, config)
        
        return jsonify({
            'success': True,
            'message': '配置已更新'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/config/ai/platforms', methods=['GET'])
def list_ai_platforms():
    """列出所有AI平台"""
    try:
        from utils.ai_config import AIPlatform
        platforms = [{
            'id': platform.value,
            'name': platform.value.upper(),
            'enabled': False  # TODO: 从配置读取
        } for platform in AIPlatform]
        
        return jsonify({
            'success': True,
            'platforms': platforms
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


if __name__ == '__main__':
    # 创建templates和static目录
    Path('templates').mkdir(exist_ok=True)
    Path('static').mkdir(exist_ok=True)
    Path('static/css').mkdir(exist_ok=True)
    Path('static/js').mkdir(exist_ok=True)
    
    print("=" * 60)
    print("AI小说连载系统 - Web界面")
    print("=" * 60)
    print("\n访问地址: http://127.0.0.1:5000")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
