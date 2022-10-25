import shlex
from Sproc import get_proc

class Parser:
    # Class to Parse script

    def __init__(self, file_name='test.script') -> None:
        """[初始化解析器]

        :param file_name: [解析脚本文件名], defaults to 'test.script'
        :type file_name: str, optional
        """        

        # 过程块类实例字典
        self.proc_block = {}
        # 存储变量的dict
        self.var = {}
        # 脚本文件名
        self.file_name = file_name
        # 待parse的下一行的行数
        self.line_num = 0
        # 存储文件内容
        self.lines = []

    def open_file(self):
        """[打开文件并且读取编码方式,根据编码方式重新打开]

        :return: [返回值为文件流]
        :rtype: [TextIOWrapper]
        """        

        # 以utf-8方式打开脚本文件
        file = open(self.file_name, 'r', encoding='utf-8')
        # 编码方式
        encoding = file.readline().split()

        if len(encoding) == 0:
            print("The script must begin at line 1")
            exit(0)

        if encoding[0] == "#":
            if encoding[1] == "using" and encoding[2] == "coding":
                try:
                    # 根据编码方式重打开
                    file.close()
                    file = open(self.file_name, 'r', encoding=encoding[3])
                except:
                    print("Some wrong happend at line 1")
            else:
                print("error grammer at line 1")
                exit(0)
        else:
            file.close()
            file = open(self.file_name, 'r', encoding='utf-8')
        # 返回文件io流
        return file

        
    def is_linefeed(self, line):
        """[判断是否为空行]

        :param line: [当前行内容]
        :type line: [str]
        :return: [若返回True则为空行,返回False则不为空行]
        :rtype: [bool]
        """        

        if line == '\n' or line == '\r\n' or line == '':
            return True
        else:
            return False

    def is_note(self, line):
        """[是否为注释]

        :param line: [当前行内容]
        :type line: [str]
        :return: [若返回True则为注释,返回False则不为注释]
        :rtype: [bool]
        """        
    
        begin = line.strip()[0]
        if begin == '#' or begin == '@':
            return True
        else:
            return False

    def handle_note(self):
        """[处理注释]
        """        

        while True:
            try:
                line = self.lines[self.line_num].lstrip().rstrip()
                if line[0] == "@":
                    self.line_num += 1
                    break
            except:
                print("Wrong becuase @ ... @ be used incorrectly")
                exit(0)

            self.line_num += 1

    def is_float(self, str):
        """[判断字符串是否为str]

        :param str: [待判断的字符串]
        :type str: [str]
        :return: [若返回True则为浮点数的字符串形式,返回False则不是]
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

    def handle_numeric(self, value_str, line):
        """[处理字符串保存为数字]

        :param value_str: [待处理的字符串]
        :type value_str: [str]
        :param line: [当前行的内容]
        :type line: [str]
        :return: [返回处理后的数字]
        :rtype: [Any]

        """        

        try:
            if "." in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except:
            self.exception(line)

    def parse_file(self, file):
        """[对文件整体读入进行解析并用list组合为语法树]

        :param file: [文件IO流]]
        :type file: [TextIOWrapper]
        """        

        self.lines = file.readlines()
        while True:
            i = self.line_num
            self.line_num += 1

            if i >= len(self.lines):
                file.close()
                return

            line = self.lines[i].lstrip().rstrip()

            if line != '' and self.is_linefeed(line) == False:
                if self.is_note(line) == False:
                    token = line.split()
                    # 处理变量定义并插入到符号表
                    if token[0][0] == '$':
                        self.parse_var(line)
                    # 处理过程定义
                    elif token[0] == 'Proc':
                        self.parse_proc(line)

                if line.strip()[0] == "@":
                    # 处理多行注释
                    self.handle_note()

    def parse_var(self, line):
        """[解析变量定义语句并插入变量表]

        :param line: [变量定义所在行内容]
        :type line: [str]
        """        

        token = shlex.split(line)

        if len(token) != 3 or token[1] != '=':
            self.exception(line)

        value_str = token[2]

        varname = token[0].lstrip().rstrip()[1:]

        # 标识符校验
        if varname[0].isalpha() == False and varname[0] != '_':
            self.exception(line)
        
        for i in range(1,len(varname)):
            if varname[i].isalpha() == False and varname[i].isnumeric() == False and varname[i] != '_':
                self.exception(line)


        if value_str.isnumeric() or self.is_float(value_str):
            # 若为数字则进行类型转换
            self.var[varname] = self.handle_numeric(value_str, line)
        else:
            # 否则为字符串保存
            self.var[varname] = value_str

    def parse_switch(self, token):
        """[处理Switch结构]

        :param token: [传入此函数的Tokenlist]
        :type token: [list]
        :return: [返回Switch结构的整体Token]
        :rtype: [list]
        """        

        result_token = []

        default_exist = 0
        # Switch所在行数
        switch_line = self.line_num

        line = self.lines[self.line_num]
        self.line_num += 1
        line = line.rstrip().lstrip()

        # 从begin开始解析
        if line != 'begin':
            self.exception(line)

        while True:
            line = self.lines[self.line_num].lstrip().rstrip()
            self.line_num += 1
            
            # 处理空行和注释
            if self.is_linefeed(line):
                continue

            if self.is_note(line):
                if line[0] == '#':
                    continue
                if line[0] == '@':
                    self.handle_note()
                

            token = shlex.split(line)
            tmp_token = token[0]

            # Switch结构遇到end结束
            if token[0] == 'end':
                break

            if tmp_token == 'Branch':
                if len(token) != 4 and len(token) != 5:
                    self.exception(line)
                if len(token) == 4:
                    if token[2] != 'Run':
                        self.exception(line)
                else:
                    if token[2] != 'Loop':
                        self.exception(line)
                    times = token[4]
                    
                    if times.isdigit() == False:
                            self.exception(line)
                    try:
                        token[4] = int(times)
                    except:
                        self.exception(line)

            elif tmp_token == 'Default':
                default_exist = 1
                if len(token) != 3 or token[1] != 'Run':
                    self.exception(line)
            else:
                self.exception(line)

            result_token.append(token)

        # 必须设置默认分支
        if default_exist == 0:
            print("Default proc in Switch at line " +
                  str(switch_line) + " is not defined")
            exit(0)
        return result_token

    def parse_proc(self, line):
        """[解析过程Proc]

        :param line: [Proc头所在的行内容]
        :type line: [str]
        """       

        token = line.split()

        if len(token) != 2:
            self.exception(line)

        proc_name = token[1]

        if proc_name[0].isalpha() == False and proc_name[0] != '_':
            self.exception(line)

        for i in range(1, len(proc_name)):
            if proc_name[i].isalpha() == False and proc_name[i].isnumeric() == False and proc_name[i] != '_':
                self.exception(line)

        # 获取Proc实例
        proc = get_proc()
        self.proc_block[token[1]] = proc

        # 从begin处开始解析

        line = self.lines[self.line_num].strip()
        self.line_num += 1
        
        if line != "begin":
            self.exception(line)

        while True:
            line = self.lines[self.line_num]
            line = line.lstrip().rstrip()
            self.line_num += 1

            if self.is_linefeed(line):
                continue

            if self.is_note(line):
                if line[0] == '#':
                    continue

                if line[0] == '@':
                    self.handle_note()

            token = shlex.split(line)
            tmp_token = token[0]

            # 如果Token为OUT代表输出
            if tmp_token == 'OUT':
                plus_num = token.count('+')
                if plus_num != len(token) - plus_num - 2:
                    self.exception(line)

                i = 0
                while plus_num != 0:
                    if token[i + 2] != '+':
                        self.exception(line)
                    plus_num -= 1
                    i += 2
            # 如果Token为IN代表输入
            elif tmp_token == 'IN':
                if len(token) == 2:
                    if token[1][0] != '$' or token[1][1:] not in self.var.keys():
                        self.exception(line)
                else:
                    self.exception(line)

            # 如果Token为Run代表运行过程
            elif tmp_token == 'Run':
                if len(token) != 2:
                    self.exception(line)

            # 如果Token为Loop代表循环过程
            elif tmp_token == 'Loop':
                if len(token) == 3:
                    times = token[2]
                    if times.isdigit() == False:
                        self.exception(line)
                    else:
                        try:
                            token[2] = int(times)
                        except:
                            self.exception(line)
                else:
                    self.exception(line)
            
            # Switch结构单独处理
            elif tmp_token == 'Switch':

                if len(token) == 2:
                    if token[1][0] != '$' or token[1][1:] not in self.var.keys():
                        self.exception(line)

                    switch_line = self.line_num
                    # 处理Switch结构
                    switch_token = self.parse_switch(token)
                else:
                    self.exception(line)

            # 如果Token为EXIT代表退出
            elif tmp_token == 'EXIT':
                None

            # 变量赋值定义处理
            elif tmp_token[0] == '$':
                if token[1] != '=':
                    self.exception()

            # 过程结束符
            elif tmp_token == 'end':
                break
            else:
                self.exception(line)

            # 保存Token并组合为语法树
            if tmp_token != 'Switch':
                proc.push_inst([self.line_num, token])
            else:
                proc.push_inst([switch_line, [token, switch_token]])
        

    def exception(self, line):
        """[词法语法错误,抛出错误]

        :param line: [错误所在行]
        :type line: [str]
        """        

        print("Wrong happend at line", self.line_num)
        print(line.lstrip().rstrip())
        exit(0)


def get_parser(filename):
    """[获取解析器实例]

    :param filename: [待解析脚本文件名]
    :type filename: [str]
    :return: [返回解析器实例]
    :rtype: [(TextIOWrapper,Parser)]
    """    
    
    parser = Parser(filename)
    file = parser.open_file()
    return file, parser
