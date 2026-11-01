# Records assets/demo.gif. Run from the repository root:
#   poetry run vhs scripts/demo.tape
# It uses a temporary data folder, so your own toolbox is never touched.

Output assets/demo.gif
Require clihax

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 700
Set Padding 24
Set Theme "Dracula"
Set TypingSpeed 45ms
Set Framerate 20
Set Framerate 20

Hide
Type "export CLIHAX_HOME=$(mktemp -d) PS1='$ '"
Enter
Ctrl+L
Show

Type "clihax --version"
Enter
Sleep 2s

Type "clihax starter --yes | tail -n 1"
Enter
Sleep 3s
Ctrl+L

Type "clihax search sqlmap"
Enter
Sleep 4s
Ctrl+L

Type "clihax search smb --quick"
Enter
Sleep 4s
Ctrl+L

Type "clihax search gobsuter --quick"
Enter
Sleep 4s
Ctrl+L

Type "clihax search ffuf --json | head -n 12"
Enter
Sleep 5s
