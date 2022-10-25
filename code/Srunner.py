from os import times
from config import get_config
from Sparser import Parser
import requests
import json
import time


class Runner:

    def __init__(self, parser: Parser) -> None:
        """[解释器运行时Runtime初始化]
        """

        # 存储脚本文件内容,用于报错
        self.lines = parser.lines
        # 过程块类实例字典
        self.proc_block = parser.proc_block
        # 存储变量的dict
        self.var = parser.var

        self.config = get_config()
        if self.config.speakfile != '':
            self.speak_file = open(self.config.speakfile,
                                   'r', encoding='utf-8')

        # 存放函数与Token映射
        self.function = {}

        # 判断是否为float类型函数
        self.is_float = parser.is_float

        pass

    def check_entry(self):
        """[校验是否存在入口Entry过程]

        :return: [返回True则存在脚本入口,返回False则不存在]
        :rtype: [bool]
        """

        if 'Entry' not in self.proc_block.keys():
            return False
        else:
            return True

    def init_func(self):
        """[设置函数调用映射]
        """

        self.function['OUT'] = self.run_out
        self.function['IN'] = self.run_in
        self.function['Switch'] = self.run_switch
        self.function['EXIT'] = self.run_exit
        self.function['Run'] = self.run_run
        self.function['Loop'] = self.run_loop

    def init_var(self, filedir):
        """[从文件初始化变量]

        :param filedir: [文件路径]
        :type filedir: [str]
        """

        try:
            var_file = open(filedir, 'r', encoding='utf-8')
            var_json = json.load(var_file)
            for each in var_json:
                self.var[each] = var_json[each]

            var_file.close()

        except:
            print("Open varfile failed")
            exit(0)

    def get_var(self):
        """[获取当前运行时变量字典,提供测试和调试接口]

        :return: [返回存储变量的字典]
        :rtype: [dict]
        """
        return self.var

    def get_proc_block(self):
        """[获取当前运行时过程块,提供测试和调试接口]

        :return: [返回当前运行时Runner过程块]
        :rtype: [list]
        """
        return self.proc_block

    def print_var(self):
        """[打印脚本变量,提供测试和调试接口]
        """
        for each in self.var:
            print(each + " : " + str(self.var[each]))

    def send_var(self):
        """[测试桩: 向远程服务器发送GET请求请求内容为变量值]
        """

        # 测试桩: 向远程服务器发送GET请求 请求内容为变量值
        url = 'http://49.232.162.82/test.php?var=' + json.dumps(self.var)
        respose = requests.get(url=url)

        # 响应输出
        print(respose.text)

    def send_msg(self, msg):
        """[向远程服务器发送信息]

        :param msg: [要发送的信息]
        :type msg: [str]
        """        

        # 测试桩: 向远程服务器发送信息
        url = 'http://49.232.162.82/test.php?msg=' + msg
        respose = requests.get(url=url)


    def recv_msg(self,request):
        """[从远程服务器获取信息]

        :return: [返回响应]
        :rtype: [Respose]
        """        
        # 测试桩: 从远程服务器接收信息

        url = 'http://49.232.162.82/' + request
        respose = requests.get(url=url)

        return respose

    def change_var(self, name, value):
        """[修改变量函数,用于从外部获取数据后进行修改]

        :param name: [变量名称]
        :type name: [str]
        :param value: [变量值]
        :type value: [Any]
        """

        self.var[name] = value

    def exception(self, inst):
        """[程序检测到脚本运行时异常,抛出异常并给出错误位置后结束运行]

        :param inst: [当前异常指令]
        :type inst: [list]
        """

        print()
        print("Wrong happend at line ", inst[0])
        print(self.lines[inst[0] - 1])
        exit(0)

    def is_float(self, str):
        """[判断传入的字符串参数是否为float类型]

        :param str: [待判断字符串]
        :type str: [str]
        :return: [若返回True则为float类型,返回False则不是float类型]
        :rtype: [bool]
        """

        s = str.split('.')
        if len(s) > 2:
            return False
        else:
            for si in s:
                if not si.isdigit():
                    return False
            return True

    def handle_numeric(self, value_str, inst):
        """[将字符串转变为数字型变量]

        :return: [返回处理完成后的结果]
        :rtype: [Any]
        """

        try:
            if "." in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except:
            self.exception(inst)

    def handle_expression(self, inst):
        """[处理表达式]

        :param inst: [传入的解析后的表达式list]
        :type inst: [list]
        """

        expression_list = inst[1]
        # 表达式检错
        if expression_list[1] != '=' or '$' not in expression_list[0] or expression_list[0][1:] not in self.var.keys():
            self.exception(inst)

        if len(expression_list) == 3:
            # 赋值语句token长度为3
            val = expression_list[2]
            if '$' in val[0] and val[1:] in self.var.keys():
                self.var[expression_list[0][1:]
                         ] = self.var[expression_list[2][1:]]
            else:
                if val.isnumeric() or self.is_float(val):
                    result = self.handle_numeric(val, inst)
                else:
                    result = val
                self.var[expression_list[0][1:]] = result

            return

        # 运算表达式token长度为 5
        op = expression_list[3]
        if op != '+' and op != '-' and op != '*' and op != '/' and op != '%':
            self.exception(inst)

        # 表达式中提取两值
        x = expression_list[2]
        y = expression_list[4]

        if '$' in x:
            if x[1:] not in self.var.keys():
                self.exception(inst)
            else:
                x = self.var[x[1:]]
        else:
            if x.isnumeric() or self.is_float(x):
                x = self.handle_numeric(x, inst)

        if '$' in y:
            if y[1:] not in self.var.keys():
                self.exception(inst)
            else:
                y = self.var[y[1:]]
        else:
            if y.isnumeric() or self.is_float(y):
                y = self.handle_numeric(y, inst)

        if op == '+':
            if (type(x) == str and type(y) == str) or (type(x) != str and type(y) != str):
                self.var[expression_list[0][1:]] = x + y
            else:
                print("Unknow expression : " +
                      str(type(x)) + ' + ' + str(type(y)))
                self.exception(inst)
        else:
            if type(x) != str and type(y) != str:
                try:
                    # 通过eval进行运算 返回值赋值到对应位置
                    self.var[expression_list[0][1:]] = eval('x'+op+'y')
                except:
                    # 捕获除零异常等异常
                    print("Exception caused by operation")
                    self.exception(inst)
            else:
                self.exception(inst)

    def input_stream(self):
        """[输入流,用于不同的输入方式调用统一接口]

        :return: [返回输入内容]
        :rtype: [str]
        """

        if self.config.speakfile != '':
            line = self.speak_file.readline().strip('\n').strip('\r\n')
            # 测试桩 语音输入接口
            if self.config.no_color == False:
                print("\033[31m" + " IN : " + "\033[0m", end='')
                print(line)
            else:
                print(" IN : ", end='')
                print(line)
            return line

        else:
            if self.config.no_color == False:
                return input("\033[31m" + " IN : " + "\033[0m")
            else:
                return input(" IN : ")

    def run_out(self, inst):
        """[运行输出指令OUT]

        :param inst: [当前OUT指令list,包括其输出内容的表达式和行数]
        :type inst: [list]
        """
        if self.config.no_time == False:
            print_time = time.strftime("[%Y-%m-%d %H:%M:%S]",
                                       time.localtime())
        else:
            print_time = ''

        if self.config.no_color == False:
            print("\033[32m" + print_time + "\033[0m", end=' ')
            print("\033[32m" + "OUT : " + "\033[0m", end='')
        else:
            print(print_time, end=' ')
            print("OUT : ", end='')
        for args in inst[1][1:]:
            if args[0] == '$':
                if args[1:] in self.var.keys():
                    print(self.var[args[1:]], end='')
                else:
                    self.exception(inst)
            elif args != '+':
                print(args, end='')

        print()

    def run_in(self, inst):
        """[运行输入指令IN]

        :param inst: [当前IN指令list,包括其输入变量名称和行数]
        :type inst: [list]
        """

        if self.config.no_time == False:
            print_time = time.strftime("[%Y-%m-%d %H:%M:%S]",
                                       time.localtime())
        else:
            print_time = ''

        varname = inst[1][1][1:]
        if varname in self.var.keys():
            if self.config.no_color == False:
                print("\033[31m" + print_time + "\033[0m", end=' ')
            else:
                print(print_time, end=' ')
            try:
                value = self.input_stream()
            except:
                exit(0)
            self.var[varname] = value

        else:
            self.exception(inst)

    def run_run(self, inst):
        """[运行执行过程指令Run]

        :param inst: [当前Run指令list,包括其欲执行的过程名称和行数]
        :type inst: [list]
        """

        proc = inst[1][1]
        if proc in self.proc_block.keys():
            # 若过程存在则运行
            self.run_proc(self.proc_block[proc])
        else:
            self.exception(inst)

    def run_loop(self, inst):
        """[运行循环执行过程指令Loop]

        :param inst: [当前Loop指令list,包括其欲执行的过程名称、循环次数以及行数]
        :type inst: [list]
        """

        proc = inst[1][1]
        times = inst[1][2]

        if proc in self.proc_block.keys():
            for i in range(0, times):
                # 循环运行
                self.run_branch(self.proc_block[proc])
        else:
            self.exception(inst)

    def run_branch(self, proc):
        """[运行Switch分支指向的满足条件的过程]

        :param proc: [过程内容,包括过程具体指令和对应行数]
        :type proc: [list]
        """

        self.run_proc(proc)

    def run_loop_branch(self, proc, times):
        """[循环运行Switch分支执行的某一满足条件的过程]

        :param proc: [过程内容,包括过程具体指令和对应行数]
        :type proc: [list]
        :param times: [循环次数]
        :type times: [int]
        """

        for i in range(0, times):
            self.run_branch(proc)

    def run_switch(self, inst):
        """[解释执行Switch分支结构]

        :param inst: [包含当前Switch结构整体内容的指令集以及每条指令对应行数]
        :type inst: [list]
        """

        # 获取变量名
        varname = inst[1][0][1][1:]
        # 获取分支list
        case = inst[1][1]
        # 在Default之前匹配到分支
        is_match = False
        # 默认分支proc
        default_proc = None

        if varname not in self.var.keys():
            self.exception(inst)

        for each in case:
            if each[0] == 'Branch':
                # 进行模糊匹配,只要存在即进入分支,支持多分支进入
                if each[1] not in self.var[varname]:
                    continue
                is_match = True
                if each[2] == 'Run':
                    # 单词运行
                    if each[3] in self.proc_block.keys():
                        self.run_branch(self.proc_block[each[3]])
                    else:
                        print(
                            "Proc " + each[3] + " is not defined in switch " + inst[1][0][1])
                        self.exception(inst)

                elif each[2] == 'Loop':
                    # 循环运行
                    if each[3] in self.proc_block.keys():
                        self.run_loop_branch(
                            self.proc_block[each[3]], each[4])
                    else:
                        print(
                            "Proc " + each[3] + " is not defined in switch " + inst[1][0][1])
                        self.exception(inst)
                else:
                    self.exception(inst)

            elif each[0] == 'Default':
                # 记录Default分支
                default_proc = each

        # 若未匹配到前面各分支则进入Default分支
        if is_match == False:
            if default_proc != None:
                if default_proc[1] == 'Run':
                    self.run_branch(self.proc_block[each[2]])
                elif default_proc[1] == 'Loop':
                    self.run_loop_branch(
                        self.proc_block[each[2]], each[3])
                else:
                    self.exception()
            else:
                print()
                exit(0)
        return

    def run_exit(self, inst):
        """[运行指令EXIT]

        :param inst: [传入一条指令EXIT以及其所在行数]
        :type inst: [list]
        """
        # 测试桩: 若开启调试模式则输出结束时的变量键值对
        if self.config.debug == True:
            self.print_var()

        # 测试桩,记录客服服务内容并上传到服务器
        if self.config.record == True:
            self.send_var()

        print("程序正在下线...")
        exit(0)

    def run_proc(self, proc):
        """[运行脚本过程]

        :param proc: [传入过程的具体内容,包括指令行数和解析后的具体指令]
        :type proc: [list]
        """
        for inst in proc.inst:

            if 'Switch' not in inst[1][0]:
                # 如果是Switch结构单独映射
                if '$' not in inst[1][0]:
                    func = self.function[inst[1][0]]
                    func(inst)
                else:
                    if len(inst[1]) == 5 or len(inst[1]) == 3:
                        self.handle_expression(inst)
                    else:
                        self.exception(inst)
            else:
                # 直接根据映射内容调用函数
                func = self.function[inst[1][0][0]]
                func(inst)

    def start(self):
        """[开始解释执行]
        """

        # 校验是否存在Entry入口
        if self.check_entry() == False:
            print("Can't find Entry Proc in script")
            print("The program must start at Entry Proc")
            exit(0)

        # 设置Token与函数映射
        self.init_func()

        # 从Entry开始运行
        self.run_proc(self.proc_block['Entry'])


def get_runner(parser: Parser):
    """[获取当前运行时实例]

    :param parser: [脚本解析器Parser实例]
    :type parser: [Parser]
    :return: [返回运行时Runner实例]
    :rtype: [Runner]
    """

    # 初始化运行时实例
    runner = Runner(parser)
    # 获取配置
    config = get_config()

    # 测试桩: 用于接收从其他端口获得变量数据后给与脚本变量初始化
    if config.varfile != '':
        runner.init_var(config.varfile)

    # 测试桩: 若开启调试模式则输出初始化后的变量键值对
    if config.debug == True:
        runner.print_var()

    # 返回运行时实例
    return runner
