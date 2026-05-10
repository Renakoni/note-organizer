#!/usr/bin/env bash
set -euo pipefail

skills_dir="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$skills_dir"

install_or_update_repo() {
  local name="$1"
  local repo="$2"
  local target="$skills_dir/$name"

  if [ -d "$target/.git" ]; then
    echo "Updating $name..."
    git -C "$target" pull --ff-only
  elif [ -e "$target" ]; then
    echo "Skipping $name: $target already exists and is not a git repository."
    echo "Remove it or set CLAUDE_SKILLS_DIR to another directory if you want this script to install it."
  else
    echo "Installing $name..."
    git clone "$repo" "$target"
  fi
}

install_markdown_mermaid_writing() {
  local target="$skills_dir/markdown-mermaid-writing"

  if [ -d "$target" ]; then
    echo "Skipping markdown-mermaid-writing: $target already exists."
    return
  fi

  local tmp_dir
  tmp_dir="$(mktemp -d)"

  echo "Installing markdown-mermaid-writing..."
  git clone --filter=blob:none --sparse https://github.com/K-Dense-AI/scientific-agent-skills.git "$tmp_dir/scientific-agent-skills"
  git -C "$tmp_dir/scientific-agent-skills" sparse-checkout set scientific-skills/markdown-mermaid-writing
  cp -R "$tmp_dir/scientific-agent-skills/scientific-skills/markdown-mermaid-writing" "$target"
  rm -rf "$tmp_dir"
}

install_or_update_repo "humanizer" "https://github.com/blader/humanizer.git"
install_markdown_mermaid_writing

echo "Recommended skills installed in: $skills_dir"
echo "Restart Claude Code or open a new session before using them."
