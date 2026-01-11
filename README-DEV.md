Good call. Here's what to note for README-DEV:
Installing Just - Windows

Open PowerShell as Administrator
Install Scoop (if not already installed):

powershell   irm get.scoop.sh | iex

Install just:

powershell   scoop install just

Verify: just --version

Installing Just - macOS
brew install just

How to Install Homebrew (If You Don't Have It):
Open Terminal.
Install Xcode Command Line Tools: xcode-select --install (if prompted).
Run the official installer script from the Homebrew website:
bash
/bin/bash -c "$(curl -fsSL raw.githubusercontent.com)"
Follow any on-screen instructions, which might include adding Homebrew to your $PATH. 

