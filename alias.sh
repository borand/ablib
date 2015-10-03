#!/bin/bash 
alias clc='clear'
alias ve='source ~/venv/bin/activate'
alias de='deactivate'
alias ip='ipython'
alias p='python'

alias dt='digitemp_DS2490'

alias lnk='ln -s ~/projects/ablib/mypath.pth ~/venv/lib/python2.7/site-packages/ablib.pth'

alias gitcom='git commit -am"..."'
alias push='git push'

alias fps='~/venv/bin/fab -f~/projects/ablib/ablib/util/fabfile.py ps'
alias fstart='~/venv/bin/fab -f~/projects/ablib/ablib/util/fabfile.py start'
alias fkill='~/venv/bin/fab -f~/projects/ablib/ablib/util/fabfile.py kill'
alias serv='ssh andrzej@192.168.1.12'