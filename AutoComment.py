import random
import logging
import re
import sys, traceback
import os.path


# 随机选取的函数
basePath = os.path.dirname(sys.argv[0])
if basePath == '': basePath = '.'
try:
    with open(basePath + '/config') as configFile:
        exec(configFile.read())
except Exception as e:
    logging.critical(repr(e))
    logging.debug(traceback.print_exc())
    sys.exit()

def rand(inputStr, conditions = {}):
    handledNumbers = 0
    replacedTextList = {}
    while 1:

        lexicons = re.findall('\{([^|}]*)\}', inputStr)
        if len(lexicons) == 0:
            return ''

        seed = random.random() # 生成随机种子
        pool = [] # 备选池
        result = ''


        reallexicon = ''
        # 同类组件判断
        if re.search('[0-9]', lexicons[handledNumbers]): # 说明一个语句中出现了多个同类分句
            reallexicon = re.search('[^0-9]*', lexicons[handledNumbers]).group(0) # 去除末尾的数字
            logging.debug('出现同类分词！')
        else:
            reallexicon = lexicons[handledNumbers]
        
        # 是否可能有限制条件
        if type(eval(reallexicon)) == type(dict()): # 可能有制约条件的数据
            conditions = eval(reallexicon)['conditions']
        else: # 没有制约条件
            conditions = {}
        

        # 生成 pool
        if type(eval(reallexicon)) == type(list()):
            pool = eval(reallexicon)
        else: # 相对复杂的样子
            content = eval(reallexicon)['v']
            for k, v in content.items():
                if type(v) == type(list()):
                    pool.append([k, v[1]])
                else:
                    pool.append(k)


        # 前文判断
        logging.debug('已处理' + str(handledNumbers))
        repeated = False
        for j in range(0, handledNumbers):
            
            # 代词判断
            try:
                if lexicons[j] == lexicons[handledNumbers]: # 说明是按照代词处理的部分
                    repeated = True
                    logging.debug('这是一个代词')
                    handledNumbers += 1
                    break
            except IndexError:
                print('列表为')
                print(lexicons)
                print('j 为 %d'%j)
                print(handledNumbers)
                sys.exit()

            c = re.search('[^0-9]*', lexicons[j]).group(0) #当前组件的名称
            # 根据同类组件进行范围缩减
            if c == reallexicon: # 是同类组件
                for i in range(0, len(pool)):
                    if pool[i] == replacedTextList[c]:
                        del(pool[i])
                        break

            # 依赖条件判断
            if conditions != {}: # 非简单类型
                if c in conditions.keys(): # 是限制条件
                    logging.debug('出现限制条件！')
                    cl = eval(c) # 限制条件组件库
                    cv = replacedTextList[lexicons[j]] # 对应组件的结果
                    prop = cl['v'][cv] # 对应组件值得属性 或 属性+概率
                    if type(prop) == type(list()):
                        prop = prop[0]


                    # 针对限制条件，缩小 pool 的范围
                    propList = [] # 限制属性的列表
                    poolt = [] # 暂存工具
                    table = conditions[c]
                    if c.lower() == table.split('VS')[0].lower(): # c 是 key，直接选取
                        propList = eval(table)[prop]
                        logging.debug('限制条件是 key')
                    elif c.lower() == table.split('VS')[1].lower(): # 是 value
                        for k1, v1 in eval(table).items():
                            if prop in v1:propList.append(k1)
                        logging.debug('限制条件是 value')          
                    else: # 有错
                        return ''

                    # 有了 propList 之后进行 pool 取并集
                    for i in range(0, len(pool)):

                        if type(pool[i]) == type(list()):
                            content = pool[i][0]
                        else:
                            content = pool[i]
                        
                        prop = eval(reallexicon)['v'][content]
                        if type(prop) == type(list()):
                            prop = prop[0]
                        
                        if prop in propList:
                            poolt.append(pool[i])
                        
                    pool = poolt

        logging.debug('pool 是' + str(pool))
        
        # 随机生成
        if repeated == False:
            step = 0
            summ = 0
            logging.debug('seed 为' + str(seed))

            # 计算步长
            x = 0
            s = 0
            for i in range(0, len(pool)):
                if type(pool[i]) == type(list()):
                    s += pool[i][1]
                else:
                    x += 1
                print(x)
            if x != 0:
                print(s, x)
                step = float((1 - s))/x
            logging.debug('步长为 %f'%step)

            for i in range(0, len(pool)):
                if type(pool[i]) == type(list()): # 有权重的语句
                    logging.debug('进入有权重部分，summ 为' + str(summ))
                    logging.debug(str(i) + '部分概率为' + str(pool[i][1]))
                    if summ <= seed and summ + pool[i][1] > seed:#种子落在这个区间
                        result = pool[i][0]
                        break
                    else: # 没到这个区间
                        summ += pool[i][1]
                        continue
                else:
                    logging.debug('进入无权重部分，summ 为' + str(summ))
                    if summ <= seed and summ + step > seed:
                        result = pool[i]
                        break
                    else:
                        summ += step

            logging.debug('随机生成计算后的结果为' + result)
            logging.debug('======')

            # 处理返回的结果
            if re.search('\{([^|}]*)\}', result): # 还有组件库
                if lexicons[handledNumbers] == 'sentence':
                    logging.info('原始句式为：' + result)
                inputStr = re.sub( '{' + lexicons[handledNumbers] + '}', result, inputStr)
                logging.debug('本次修改后字符串变为' + inputStr)
                # inputStr = eval('inputStr.format(' + lexicons[handledNumbers] + '= \'' + result + '\')')
            else: # 已经没有组件了
                replacedTextList[lexicons[handledNumbers]] = result
                handledNumbers += 1
                logging.debug('已处理的列表' + str(replacedTextList))
        if handledNumbers == len(lexicons) : # 已经处理完了
            logging.info('最终句式为：' + inputStr)
            for k, v in replacedTextList.items():
                if v == '_': v = ''
                inputStr = re.sub( '{' + k + '}', v, inputStr)
                # inputStr = eval('inputStr.format(' + k + '= \'' + v + '\')')
            return inputStr

            



'''
    seed = random.random() # 生成随机种子
    pool = [] # 备选池
    result = ''

    # 判断是否有制约条件，并设置 pool
    if conditions != {}: # 有制约条件
        attr, attrt = [], [] # 临时池
        for k, v in conditions.items():
            table = lexicon['conditions'][k]
            # 判断 限制条件 k 在字典中是 key 还是 value
            logging.debug('限制条件的 k 和 table：' + k + '-' + table)
            if k.lower() == table.split('VS')[0].lower(): # k 是 key，直接选取
                attrt = eval(table)[v]
                logging.debug('限制条件是 key')
            elif k.lower() == table.split('VS')[1].lower(): # k 是 value，需要遍历字典
                logging.debug('限制条件是 value')
                for k1, v1 in eval(table).items():
                    if v in v1:
                        attrt.append(k1)
                logging.debug('限制条件的匹配结果为' + ', '.join(attrt))
            else: # 出现了错误
                return ''
        if attr == []:# 未设置过 pool
            attr = attrt
        else: # 取并集
            attr = (val for val in attr if val in attrt)

        logging.debug('取并集之后' + ', '.join(attr))


        # 此时得到的还是一堆属性，需要转换为名称
        for i in range(0, len(attr)):
            for k, v in lexicon['v'].items():
                if type(v) == type(list()) and v[0] == attr[i]:
                    pool.append([k, v[1]])
                elif v == attr[i]:
                    pool.append(k)


    else: # 没有限制条件
        if type(lexicon) == type(dict()):
            for k in lexicon['v'].keys():
                if type(lexicon['v'][k]) == type(list()):
                    pool.append([k, lexicon['v'][k][1]])
                else:
                    pool.append(k)
        if type(lexicon) == type(list()):
                pool = lexicon
        logging.debug('无限制条件的结果')
    if len(pool) == 0:
        return ''

    
    # 根据随机种子返回生成语句
    step = 0
    summ = 0
    logging.debug('seed 为' + str(seed))
    for i in range(0, len(pool)):
        if type(pool[i]) == type(list()): # 有权重的语句
            logging.debug('进入有权重部分，summ 为' + str(summ))
            logging.debug(str(i) + '部分概率为' + str(pool[i][1]))
            if summ <= seed and summ + pool[i][1] > seed:#种子落在这个区间
                result = pool[i][0]
                break
            else: # 没到这个区间
                summ += pool[i][1]
                continue
        else:
            logging.debug('进入无权重部分，summ 为' + str(summ))
            if step == 0:
                step = (1 - summ)/(len(pool) - i)
                logging.debug('步长' + str(step))
            if summ <= seed and summ + step > seed:
                result = pool[i]
                break
            else:
                summ += step

    logging.debug('随机生成计算后的结果为' + result)
    logging.debug('======')
    
    # 查看返回的结果，看看是否还需要做处理
    if result == '':
        return ''
    else:
        notHandled = re.findall('\{([^|}]*)\}', result) # 没有需要替换的字符
        if notHandled == []:
            return result
        else: # 有需要替换的字符
            logging.debug('需要处理的字符包括' + ', '.join(notHandled))
            replacedText = []
            for i in range(0, len(notHandled)):
                logging.debug('处理' + notHandled[i])
                
                repeated = False
                for j in range(0, len(replacedText)):
                    if replacedText[j][0] == notHandled[i]: # 说明是按照代词处理的部分
                        repeated = True
                        logging.debug('这是一个代词')
                        break
                if repeated == True: # 直接跳入下一个分句
                    continue


                if re.search('[0-9]', notHandled[i]): # 说明一个语句中出现了多个同类分句
                    reallexicon = re.search('[^0-9]*', notHandled[i]).group(0) # 去除末尾的数字
                    logging.debug('出现同类分词！')
                else:
                    reallexicon = notHandled[i]

                if type(eval(reallexicon)) == type(list()): # 是简单的数组
                    r = rand(eval(reallexicon))
                    logging.debug('简单列表处理结果为' + r)
                else: # 可能有制约条件的数据
                    conditions = eval(reallexicon)['conditions']
                    c = {}
                    for j in range(0, len(replacedText)):
                        k = re.search('[^0-9]*', replacedText[j][0]).group(0) # k 是相关的那个表的名称
                        if k in conditions.keys():
                            t = eval(k)['v'][replacedText[j][1]] # 这是 属性值或者属性+概率的表
                            if type(t) == type(list()):
                                c[k] = t[0]
                            else:
                                c[k] = t
                            logging.debug('出现限制条件！' + k + '-' + c[k])
                    r = rand(eval(reallexicon), c)

                if r == '': # 返回失败
                    return ''

                if reallexicon != notHandled[i]: # 一个语句中出现多个同类分句
                    for j in range(0, len(replacedText)):
                        if re.search('[^0-9]*', replacedText[j][0]).group(0) == reallexicon and replacedText[j][1] == r: ## 判断是否重复
                            return ''
                    
                # 没有重复，是成功的
                replacedText.append([notHandled[i], r])

            command = []
            for i in range(0, len(replacedText)):
                if replacedText[i][1] == '_':
                    replacedText[i][1] = ''
                command.append(replacedText[i][0] + '=\'' + replacedText[i][1] + '\'')
            command = ', '.join(command)
            command = 'result.format(' + command + ')'
            logging.debug('指令为' + command)
            return eval(command)
'''

# 进行生成
try:
    with open(basePath + '/comment.txt', 'a') as f:
        i = 0
        while i < totalNumbers:
            result = rand('{sentence}')
            #result = rand('{shortComment}{better}')
            if result != '':
                f.write(result + '\n')
                i += 1
                logging.info('第 %d 次生成结果为: %s'%(i, result))
except Exception as e:
    logging.critical(repr(e))
    logging.debug(traceback.print_exc())
