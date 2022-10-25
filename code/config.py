import argparse


def str2bool(v):
    """[将str转化为Bool类型]

    :param v: [字符串]
    :type v: [str]
    :return: [返回str对应的bool值]
    :rtype: [bool]
    """
    return v.lower() in ('true')


def get_config():
    """[获取参数]

    :return: [返回参数]
    :rtype: [_N@parse_args]
    """
    argparser = argparse.ArgumentParser()

    # 脚本路径
    argparser.add_argument('-f', '--scriptfile', type=str, default="test.script",
                           help='script file to execute')

    # 测试桩 提供测试人员调试使用,目前支持输入初始化变量后的内容
    argparser.add_argument('-d', '--debug', metavar='DEBUG_FLAG', nargs='?', const='True', type=str2bool, default="False",
                           help='DEBUG controller [DEBUG_FLAG] = TRUE/FLASE or default')
    # 测试桩,语音输入文件模拟
    argparser.add_argument('-s', '--speakfile', metavar='speak_filedir', type=str, default="",
                           help='if use speak , need a file(example: test.speak) as speak content to test')
    # 测试桩,信息查询后初始化变量
    argparser.add_argument('-v', '--varfile', metavar='var_filedir', type=str, default="",
                           help='init var from a file (example: var.json),the file has json only')
    # 测试桩,多用户并发提供同一语法树进行优化
    argparser.add_argument('-p', '--parserfile', metavar='parser_filedir', type=str, default="",
                           help='load parser object from pickle file(example: test.parser)')
    # 测试桩,多用户并发提供同一语法树进行优化
    argparser.add_argument('-o', '--outfile', metavar='outprint_filedir', type=str, default="",
                           help='out print content to outfile')
    # 测试桩,记录客服服务内容并上传到服务器
    argparser.add_argument('-r', '--record', metavar='RECORD_FLAG', nargs='?', const='True', type=str2bool, default="False",
                           help='IF use this arg , send var infomation to http server')

    # 用于自动化测试,指定该参数-nc即不输出颜色
    argparser.add_argument('-nc', '--no_color', metavar='NO_COLOR_FLAG', nargs='?', const='True', type=str2bool, default="False",
                           help='IF use Auto test and don\'t want to print color just add this args.[NO_COLOR_FLAG] = TRUE/FLASE or default ')
    # 用于自动化测试,指定该参数-nt即不输出时间
    argparser.add_argument('-nt', '--no_time', metavar='NO_TIME_FLAG', nargs='?', const='True', type=str2bool, default="False",
                           help='IF use Auto test and don\'t want to print time just add this args.[NO_TIME_FLAG] = TRUE/FLASE or default ')

    config = argparser.parse_args()

    return config
