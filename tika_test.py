# coding=utf-8
from tikapp import TikaApp
import json
import subprocess

#tika = TikaApp(file_jar='/Users/laofeng/es_home/tika-app-1.23.jar')

'''
#检查文件类型
r = tika.detect_content_type(path='1.pdf', payload="base64_payload")
print("文件类型：" , r)
#检查文件语言，不太准确
r = tika.detect_language(path='1.pdf', payload="base64_payload")
print("文件语言", r)
#导出meta和内容
r = tika.extract_all_content(path='1.pdf', payload="base64_payload")
print("extract_all_content", r)
#导出文件内容
r = tika.extract_only_content(path='1.pdf', payload="base64_payload")
print(r)
#导出文本内容
'''
#r = tika.extract_only_metadata(path='1.pdf', payload="base64_payload")
#print('extract_only_metadata', r)

#只导出内容
#-t ， 导出内容

commands = ['java', '-cp', '/Users/laofeng/es_home/tika-app-1.23.jar',"org.apache.tika.cli.TikaCLI", "-J", "-t", "-r",
            '/Volumes/portable/sync/es/Apress.Beginning.Elastic.Stack.1484216938.pdf', '-eUTF8', '&']

out = subprocess.Popen(
                    commands,
                    stdin=None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL)

subprocess.run(commands, check=True, stdout=subprocess.PIPE).stdout

subprocess.check_call()

stdoutdata, _ = out.communicate()
lines = stdoutdata.decode("utf-8").strip()

print(lines)
