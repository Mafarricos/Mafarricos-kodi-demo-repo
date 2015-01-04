Mafarricos-kodi-demo-repo
=========================

Demonstration of a basic repository for kodi (To use as template)

1. Make an account on github:<br>
    https://github.com/join
2. Download and install github application for your system or some compatible with github:<br>
    https://windows.github.com/<br>
    https://mac.github.com/<br>
    http://git-scm.com/downloads/guis<br>
    etc
3. Download and install python for your system<br>
    https://www.python.org/downloads/<br>
4. Fork this repo:<br>
    https://github.com/Mafarricos/Mafarricos-kodi-demo-repo/fork
5. On your forked project go to Settings and change the repository name to what do you want.
<img src=https://raw.githubusercontent.com/Mafarricos/Mafarricos-kodi-demo-repo/master/imgs/1.jpg>
<img src=https://raw.githubusercontent.com/Mafarricos/Mafarricos-kodi-demo-repo/master/imgs/2.jpg>
6. Clone your new repo to your PC.
7. On your PC edit the folder repository.demo.kodi to the name of your desire as the folder repository.demo.kodi inside repo folder (in my case would be repository.mafarricos.kodi).
8. Edit the addon.xml inside the repository.XXX.kodi
<img src=https://raw.githubusercontent.com/Mafarricos/Mafarricos-kodi-demo-repo/master/imgs/3.jpg>
    - In the addon id="XXX" name="YYY" version="0.0.1" provider-name="ZZZ" line change XXX to your new folder name, YYY to your repo name and ZZZ to your nickname.
    - In the extension point="xbmc.addon.repository" name="XXX" line change XXX to your repository name.
    - On the other lines change the Mafarricos/Mafarricos-kodi-demo-repo to your nick/the new folder name
    - On summary and description you change to what you want.
9. After this you can put your addons in the root folder, inside the repo folder you should create a folder with the same name of the addon and inside you will put the zip file with the format addonname-addonversion (as you see for the demo repo).
10. You should do the same to the new repo that you created.
11. In the end run addons_xml_generator.py so addons.xml.md5 and addons.xml is recriated.
12. Push and sync changes on your PC to github and you can share the zip file with your repo and addons.
