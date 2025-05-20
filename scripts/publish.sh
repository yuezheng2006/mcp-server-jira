#!/bin/bash
# 一键发布personal-jira-mcp到PyPI的脚本

set -e  # 遇到错误立即退出

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始发布personal-jira-mcp到PyPI...${NC}"

# 清理之前的构建
echo -e "${YELLOW}清理之前的构建文件...${NC}"
rm -rf dist/ build/ *.egg-info/ ~/PyPI_uploads/*

# 构建包
echo -e "${YELLOW}构建包...${NC}"
UV_HTTP_TIMEOUT=120 uv run -m build

# 备份包
echo -e "${YELLOW}备份包到~/PyPI_uploads/...${NC}"
mkdir -p ~/PyPI_uploads
cp dist/* ~/PyPI_uploads/

# 检查包
echo -e "${YELLOW}检查包...${NC}"
UV_HTTP_TIMEOUT=120 uv pip install -U twine
UV_HTTP_TIMEOUT=120 uv run -m twine check dist/*

# 发布选项
echo -e "${YELLOW}请选择发布模式:${NC}"
echo "1) 发布到测试PyPI"
echo "2) 发布到正式PyPI"
echo "3) 两者都发布"
echo "4) 取消"
read -p "请输入选项 [1-4]: " choice

case $choice in
    1)
        echo -e "${YELLOW}正在上传到测试PyPI...${NC}"
        UV_HTTP_TIMEOUT=120 uv run -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
        echo -e "${GREEN}上传完成！可以使用以下命令测试安装:${NC}"
        echo -e "UV_HTTP_TIMEOUT=120 uv pip install --index-url https://test.pypi.org/simple/ personal-jira-mcp"
        ;;
    2)
        echo -e "${YELLOW}正在上传到正式PyPI...${NC}"
        UV_HTTP_TIMEOUT=120 uv run -m twine upload dist/*
        echo -e "${GREEN}上传完成！可以使用以下命令安装:${NC}"
        echo -e "uv pip install personal-jira-mcp"
        ;;
    3)
        echo -e "${YELLOW}正在上传到测试PyPI...${NC}"
        UV_HTTP_TIMEOUT=120 uv run -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
        
        read -p "测试PyPI上传完成，是否继续上传到正式PyPI？ [y/N] " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            echo -e "${YELLOW}正在上传到正式PyPI...${NC}"
            UV_HTTP_TIMEOUT=120 uv run -m twine upload dist/*
            echo -e "${GREEN}上传完成！可以使用以下命令安装:${NC}"
            echo -e "uv pip install personal-jira-mcp"
        else
            echo -e "${YELLOW}已取消上传到正式PyPI${NC}"
        fi
        ;;
    *)
        echo -e "${RED}已取消发布过程${NC}"
        exit 0
        ;;
esac

echo -e "${GREEN}发布流程完成！${NC}" 