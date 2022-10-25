from config import get_config
from Srunner import get_runner
from Sparser import get_parser
import os
import pickle
import sys

def main():
    """[整个解释器最外层框架,获得解析器和运行时实例进行运行]
    """    
    config = get_config()

    # 测试桩: 输出重定向到文件,可用于
    if config.outfile != '':
        out = open(config.outfile, 'w',encoding='utf-8')
        sys.stdout = out

    # 测试桩: 读取程序语法树,提供多用户方案
    if config.parserfile != '':
        with open(config.parserfile,'rb') as fp:
            parser = pickle.load(fp)
    else:
        if config.scriptfile != '' and config.scriptfile[-7:] == '.script':
            # 解析脚本
            file, parser = get_parser(config.scriptfile)
            parser.parse_file(file)

            # 测试桩: 保存程序语法树,提供多用户方案
            with open('.\\parser\\' + config.scriptfile[:-7] + '.parser', 'wb') as fp:
                pickle.dump(parser,fp)
                fp.close()
        else:
            print("There is no script for parse and run")

    runner = get_runner(parser)
    runner.start()

    

if __name__ == "__main__":

    # 新建目录
    path = ['speak','var','out','parser']
    for each in path:
        if os.path.exists('.\\' + each + '\\') == False:
            os.mkdir('.\\' + each)
    
    main()
