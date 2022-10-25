class Proc:
    def __init__(self) -> None:
        """[初始化过程实例]
        """        

        self.inst = []
        self.inst_num = 0

        pass

    def push_inst(self, inst_list):
        """[向语法树结构中压入指令list]

        :param inst_list: [某部分指令list]
        :type inst_list: [list]
        """        
        self.inst.append(inst_list)
        self.inst_num += 1

    def get_inst_byindex(self, index):
        """[通过索引获得指令list,测试使用]

        :param index: [索引值]
        :type index: [type]
        :return: [description]
        :rtype: [type]
        """        
        return self.inst[index]

    def change_inst():
        """[预留接口提供 修改指令的功能]
        """        
        return None



def get_proc():
    """[summary]

    :return: [description]
    :rtype: [type]
    """    
    return Proc()
