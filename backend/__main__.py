#!/usr/bin/env python3
"""
backend模块的入口点
"""
import os
import sys

def main():
    # 确保我们在正确的目录中
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    print(f"Python路径: {sys.path}")

    # 检查是否有backend/app目录，如果没有，尝试切换到backend目录
    if not os.path.exists('app') and os.path.exists('backend/app'):
        # 我们可能在项目根目录，需要进入backend目录
        os.chdir('backend')
        print(f"切换到backend目录: {os.getcwd()}")

    # 添加当前目录到Python路径
    sys.path.insert(0, os.getcwd())

    print(f"最终工作目录: {os.getcwd()}")
    print(f"最终Python路径: {sys.path}")
    print(f"目录内容: {os.listdir('.')}")

    try:
        from app.main import app
        print("SUCCESS: app.main导入成功")
    except ImportError as e:
        print(f"ERROR: 导入失败: {e}")
        print(f"当前目录内容: {os.listdir('.')}")
        if os.path.exists('app'):
            print(f"app目录内容: {os.listdir('app')}")
        sys.exit(1)

    # 运行uvicorn
    port = os.environ.get('PORT', '8000')

    from uvicorn import run
    print(f"启动服务器在端口: {port}")
    run(app, host='0.0.0.0', port=int(port))

if __name__ == '__main__':
    main()