import shutil
import os
import glob
import time

# 额外参数

arg = ''

# 输出时间标志,若为0则不保留输出时间,若为1则保留输出时间
time_flag = 1
time_arg = ''

# 存放各种文件的路径
script_dir = '.\\'
varjson_dir = '.\\var\\'
parser_dir = '.\\parser\\'
speak_dir = '.\\speak\\'
output_dir = '.\\out'

count = 0

# 刷新输出目录
shutil.rmtree(output_dir)
os.mkdir(output_dir)

# 遍历脚本所在目录
script = glob.glob(os.path.join(script_dir, "*.script"))

log_file = open(output_dir + '\\log.log','w',encoding='utf-8')


for file in script:
    count += 1
    # 自动寻找文件
    if os.path.exists(speak_dir + file[:-7] + ".speak"):
        speak = ' -s ' + speak_dir + file[:-7] + ".speak"
    else:
        speak = ''

    if os.path.exists(".\\" + file[:-7] + ".json"):
        var_json = '-v ' + varjson_dir + file[:-7] + '.json'
    else:
        var_json = ''

    if time_flag == 0:
        time_arg = '-nt'
    else:
        time_arg = ''

    cmd = 'python .\main.py -f ' + file + speak + var_json + ' -nc ' + arg + time_arg + ' -o ' + output_dir + '.\\' + file[:-7] + '.out'
    os.system(cmd)
    print_time = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
    log_file.write(print_time + ' ' + file + ' 执行命令行: ' + cmd + '\n')
    print(file + "测试结束")

print("\n脚本遍历结束,已自动化测试" + str(count) + "个脚本")
print("输出到文件目录" + output_dir)
