import numpy, xlwt

base_wit = 446
base_hp = 2542
base_sp = 38

def affliction_sp_distribution(sp):
    result = []
    if sp <= 10 :
        sp_dis = (sp, 0, 0, 0, 0)
        result.append(sp_dis)
        return result
    elif 10 < sp <= 20:
        if sp - 10 <= 5:
                sp_dis = (10, 0, sp-10, 0, 0)
                result.append(sp_dis)
        else:
            for c in range(5, sp-10+1):
                sp_dis = (10, 0, c, sp-10-c, 0)
                result.append(sp_dis)
    elif sp > 20:
        for c in range(5, 11):
            for d in range(10-c, sp-10-c+1):
                e = sp-c-d-10
                if c <= 10 and d <= 10 and e <= 10:
                    sp_dis = (10, 0, c, d, e)
                    result.append(sp_dis)
    return result


# def demon_DPS(sp):
#
# def destroy_DPS(sp):

def sp_distribution(base_sp):
    result = []
    for a in range(0, base_sp + 1):
        for b in range(0, a + 1):
            sp_dis = (base_sp - a, a -b, b)
            result.append(sp_dis)
    return result

def main():
    sp_distribution_result = sp_distribution(base_sp) # 获得当前点数的所有天赋分配
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet("talent")
    row, column = 1, 0
    for each_sp_distribution in sp_distribution_result:
        aff_dis = affliction_sp_distribution(each_sp_distribution(0))
        demo_dis = affliction_sp_distribution(each_sp_distribution(0))
        des_dis = affliction_sp_distribution(each_sp_distribution(0))
        sheet.write(row, column, str(each_sp_distribution))
        sheet.write(row, column+1, str(aff_dis))
        sheet.write(row, column+2, str(demo_dis))
        sheet.write(row, column+3, str(des_dis))

main()
