from online.utils.funcs import ReSet


class ChineseNumberInteger(object):
    _rrcm = ReSet()
    digit = {'一': 1, '二': 2, '三': 3, '叁': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,'两':2}

    def __init__(self):
        pass

    def _trans(self, s):
        num = 0
        try:
            if s:
                idx_q, idx_b, idx_s = s.find('千'), s.find('百'), s.find('十')
                if idx_q != -1:
                    num += self.digit[s[idx_q - 1:idx_q]] * 1000
                if idx_b != -1:
                    # print('s==>',s)
                    num += self.digit[s[idx_b - 1:idx_b]] * 100
                if idx_s != -1:
                    # 十前忽略一的处理
                    cur_val=self.digit.get(s[idx_s - 1:idx_s], 1) * 10
                    num +=cur_val
                if s[-1] in self.digit:
                    num += self.digit[s[-1]]
        except KeyError as e:
            print('ChineseNumberInteger  e.args==>',e.args)
            num=s
        return num

    def trans_chinese2digit(self, chn):
        chn = chn.replace('零', '')
        idx_y, idx_w = chn.rfind('亿'), chn.rfind('万')
        if idx_w < idx_y:
            idx_w = -1
        num_y, num_w = 100000000, 10000
        if idx_y != -1 and idx_w != -1:
            return self.trans_chinese2digit(chn[:idx_y]) * num_y + self._trans(
                chn[idx_y + 1:idx_w]) * num_w + self._trans(chn[idx_w + 1:])
        elif idx_y != -1:
            return self.trans_chinese2digit(chn[:idx_y]) * num_y + self._trans(chn[idx_y + 1:])
        elif idx_w != -1:
            return self._trans(chn[:idx_w]) * num_w + self._trans(chn[idx_w + 1:])
        return self._trans(chn)


class ChineseNumberDecimal(object):
    _rrcm = ReSet()
    decimal_digit = {'零': 0, '点': '.', '一': 1, '二': 2,'两':2, '三': 3, '叁': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}

    def __init__(self):
        pass

    def trans_chinese_decimal2digit(self, chn):
        # print(list(chn))
        decimal_str = ''.join([str(self.decimal_digit[char]) for char in list(chn)])
        return float(decimal_str)

    def judge_chinese_number_decimal(self, order_in):
        restr_chinese_number_decimal = self._rrcm.chinese_number_pattern
        part_matched = restr_chinese_number_decimal.search(order_in)
        if part_matched and len(part_matched) > 2:
            return True, part_matched.groups()[0]
        return False, None


if __name__ == '__main__':
    cn = ChineseNumberInteger()
    # print(cn.trans_chinese2digit('十') == 10)
    # print(cn.trans_chinese2digit('一百零一') == 101)
    # print(cn.trans_chinese2digit('九百a二十一') == 921)
    # print(cn.trans_chinese2digit('五十六万零一十') == 560010)
    # print(cn.trans_chinese2digit('一万亿零二千一百零一') == 1000000002101)
    # print(cn.trans_chinese2digit('一万亿二千一百万零一百零一') == 1000021000101)
    # print(cn.trans_chinese2digit('一万零二百三十亿四千零七千八百九十') == 1023000007890)
    print(cn.trans_chinese2digit('十八') )

    cn = ChineseNumberDecimal()

    a = '三百四十九'
    a = '十七周岁'
    # print(trans(a))
    out = cn.trans_chinese_decimal2digit(a)
    print(out)
