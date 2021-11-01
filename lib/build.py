build = open('data/builds.txt', 'r', encoding='utf_8').read()
open('data/builds.txt', 'w', encoding='utf_8').write(str(int(build)+1))