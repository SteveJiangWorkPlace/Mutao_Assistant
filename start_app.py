#!/usr/bin/env python3
"""
启动脚本用于Render部署
"""
import os
import sys
import subprocess

def main():
    # 切换到backend目录
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)

    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python路径: {sys.path}")

    # 添加当前目录到Python路径
    sys.path.insert(0, os.getcwd())

    # 检查app模块是否可以导入
    try:
        import app.main
        print("✅ app模块导入成功")
    except ImportError as e:
        print(f"❌ app模块导入失败: {e}")
        print(f"当前目录内容: {os.listdir('.')}")
        print(f"app目录内容: {os.listdir('app') if os.path.exists('app') else 'app目录不存在'}")
        sys.exit(1)

    # 运行uvicorn
    port = os.environ.get('PORT', '8000')
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', port
    ]

    print(f"启动命令: {' '.join(cmd)}")
    sys.stdout.flush()

    # 执行uvicorn
    os.execvp(sys.executable, [sys.executable, '-m', 'uvicorn',
                               'app.main:app',
                               '--host', '0.0.0.0',
                               '--port', port])

if __name__ == '__main__':
    main()